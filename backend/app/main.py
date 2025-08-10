from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine, SessionLocal
from . import models, schemas
from pydantic import BaseModel

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Business MVP API")

# Разрешаем фронту (Vite на 5173) ходить к API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Старый HTML интерфейс можно оставить (не обязателен)
app.mount("/ui", StaticFiles(directory="backend/app/ui", html=True), name="ui")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Products ----------
@app.post("/products/", response_model=schemas.ProductOut)
def create_product(data: schemas.ProductCreate, db: Session = Depends(get_db)):
    obj = models.Product(
        name=data.name,
        sku=data.sku,
        unit=data.unit or "pcs",
        barcode=data.barcode,
        qty_on_hand=0.0,
        avg_cost=0.0,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.get("/products/", response_model=List[schemas.ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(models.Product).order_by(models.Product.id).all()

@app.get("/stock/", response_model=List[schemas.ProductOut])
def get_stock(db: Session = Depends(get_db)):
    return db.query(models.Product).order_by(models.Product.name).all()

# ---------- Clients ----------
@app.post("/clients/", response_model=schemas.ClientOut)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    obj = models.Client(**client.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.get("/clients/{client_id}", response_model=schemas.ClientOut)
def get_client(client_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Client).get(client_id)
    if not obj:
        raise HTTPException(404, "Client not found")
    return obj

# ---------- Vendors helper (последние 5) ----------
@app.get("/vendors/recent", response_model=List[str])
def recent_vendors(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Purchase.vendor, func.max(models.Purchase.date).label("md"))
        .filter(models.Purchase.vendor.isnot(None))
        .group_by(models.Purchase.vendor)
        .order_by(func.max(models.Purchase.date).desc())
        .limit(5)
        .all()
    )
    return [r[0] for r in rows]

# ---------- Purchase (приход) ----------
@app.post("/purchase/", response_model=schemas.PurchaseOut)
def create_purchase(data: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    if not data.items:
        raise HTTPException(400, "Purchase must contain at least one item")

    doc_date = None
    if data.date:
        try:
            doc_date = datetime.fromisoformat(data.date)
        except Exception:
            raise HTTPException(400, "Invalid date format. Use 'YYYY-MM-DD' or ISO datetime")

    purchase = models.Purchase(date=doc_date or None, vendor=data.vendor or None, total_amount=0.0)
    db.add(purchase)
    db.flush()

    total = 0.0
    for it in data.items:
        if it.qty <= 0 or it.price < 0:
            raise HTTPException(400, "Invalid qty/price in purchase item")

        product = db.query(models.Product).get(it.product_id)
        if not product:
            raise HTTPException(404, f"Product {it.product_id} not found")

        pi = models.PurchaseItem(
            purchase_id=purchase.id,
            product_id=product.id,
            qty=it.qty,
            price=it.price,
        )
        db.add(pi)

        move = models.StockMove(
            product_id=product.id,
            qty=it.qty,  # приход > 0
            ref_type="purchase",
            ref_id=purchase.id,
        )
        db.add(move)

        old_qty = product.qty_on_hand or 0.0
        old_avg = product.avg_cost or 0.0
        new_qty = old_qty + it.qty
        new_avg = it.price if new_qty == 0 else (old_qty * old_avg + it.qty * it.price) / new_qty
        product.qty_on_hand = new_qty
        product.avg_cost = new_avg

        total += it.qty * it.price

    purchase.total_amount = total
    db.commit()
    db.refresh(purchase)
    return purchase

# ---------- История закупок по поставщику ----------
class VendorPurchaseRow(BaseModel):
    date: datetime
    product_name: str
    qty: float
    price: float
    total: float

@app.get("/purchase/vendor-history", response_model=List[VendorPurchaseRow])
def vendor_history(vendor: str, limit: int = 30, db: Session = Depends(get_db)):
    q = (
        db.query(
            models.Purchase.date,
            models.Product.name,
            models.PurchaseItem.qty,
            models.PurchaseItem.price,
        )
        .join(models.PurchaseItem, models.Purchase.id == models.PurchaseItem.purchase_id)
        .join(models.Product, models.Product.id == models.PurchaseItem.product_id)
        .filter(models.Purchase.vendor == vendor)
        .order_by(models.Purchase.date.desc(), models.Purchase.id.desc())
        .limit(limit)
    )
    rows = []
    for dt, pname, qty, price in q:
        rows.append(VendorPurchaseRow(date=dt, product_name=pname, qty=qty, price=price, total=qty*price))
    return rows

# ---------- Sale (продажа) ----------
@app.post("/sale/", response_model=schemas.SaleOut)
def create_sale(data: schemas.SaleCreate, db: Session = Depends(get_db)):
    if not data.items:
        raise HTTPException(400, "Sale must contain at least one item")

    sale = models.Sale(client_id=data.client_id, total_amount=0.0, total_cogs=0.0, gross_profit=0.0)
    db.add(sale)
    db.flush()

    total_amount = 0.0
    total_cogs = 0.0
    sale_items: List[models.SaleItem] = []

    for it in data.items:
        product = db.query(models.Product).get(it.product_id)
        if not product:
            raise HTTPException(404, f"Product {it.product_id} not found")

        if it.qty <= 0 or it.price < 0:
            raise HTTPException(400, "Invalid qty/price in sale item")

        if (product.qty_on_hand or 0.0) < it.qty:
            raise HTTPException(400, f"Not enough stock for product '{product.name}'")

        line_total = it.qty * it.price
        line_cogs = it.qty * (product.avg_cost or 0.0)

        si = models.SaleItem(
            sale_id=sale.id,
            product_id=product.id,
            qty=it.qty,
            price=it.price,
            line_total=line_total,
            line_cogs=line_cogs,
        )
        sale_items.append(si)

    for si in sale_items:
        db.add(si)
        product = db.query(models.Product).get(si.product_id)
        product.qty_on_hand = (product.qty_on_hand or 0.0) - si.qty

        move = models.StockMove(
            product_id=si.product_id,
            qty=-si.qty,  # расход < 0
            ref_type="sale",
            ref_id=sale.id,
        )
        db.add(move)

        total_amount += si.line_total
        total_cogs += si.line_cogs

    sale.total_amount = total_amount
    sale.total_cogs = total_cogs
    sale.gross_profit = total_amount - total_cogs

    db.commit()
    db.refresh(sale)
    sale.items
    return sale

# ---------- Treasury: Bank & Cash ----------
def _parse_date(s: str) -> datetime:
    try:
        return datetime.fromisoformat(s)
    except Exception:
        raise HTTPException(400, "Invalid date format. Use 'YYYY-MM-DD' or ISO datetime")

@app.post("/treasury/txn", response_model=schemas.CashTxnOut)
def create_cash_txn(data: schemas.CashTxnCreate, db: Session = Depends(get_db)):
    if data.account not in ("cash", "bank"):
        raise HTTPException(400, "account must be 'cash' or 'bank'")
    if data.direction not in ("in", "out"):
        raise HTTPException(400, "direction must be 'in' or 'out'")
    if data.amount <= 0:
        raise HTTPException(400, "amount must be > 0")

    doc_date = _parse_date(data.date) if data.date else None

    txn = models.CashTxn(
        date=doc_date or None,
        account=data.account,
        direction=data.direction,
        amount=data.amount,
        counterparty=data.counterparty or None,
        note=data.note or None,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn

@app.get("/treasury/balance", response_model=schemas.CashBalance)
def treasury_balance(db: Session = Depends(get_db)):
    q = db.query(
        models.CashTxn.account,
        models.CashTxn.direction,
        func.coalesce(func.sum(models.CashTxn.amount), 0.0)
    ).group_by(models.CashTxn.account, models.CashTxn.direction)

    cash_in = cash_out = bank_in = bank_out = 0.0
    for acc, dir_, s in q:
        if acc == "cash":
            if dir_ == "in": cash_in = s
            else: cash_out = s
        elif acc == "bank":
            if dir_ == "in": bank_in = s
            else: bank_out = s

    cash = round(cash_in - cash_out, 2)
    bank = round(bank_in - bank_out, 2)
    return schemas.CashBalance(cash=cash, bank=bank, total=round(cash+bank, 2))

@app.get("/treasury/last", response_model=List[schemas.CashTxnOut])
def treasury_last(db: Session = Depends(get_db)):
    rows = db.query(models.CashTxn).order_by(models.CashTxn.id.desc()).limit(10).all()
    return rows
