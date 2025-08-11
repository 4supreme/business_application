from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .database import engine, get_db
from .models import Base, Product, Doc, DocItem, StockMove
from . import schemas

app = FastAPI(title="Business MVP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# ======= Products =======

@app.get("/products", response_model=List[schemas.ProductOut])
def products(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.id).all()

@app.post("/products", response_model=schemas.ProductOut)
def create_product(body: schemas.ProductCreate, db: Session = Depends(get_db)):
    p = Product(name=body.name, sku=body.sku, unit=body.unit, barcode=body.barcode, qty=0.0, avg_cost=0.0)
    db.add(p); db.commit(); db.refresh(p)
    return p

@app.get("/stock", response_model=List[schemas.ProductOut])
def stock(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.id).all()

# ======= Docs create (draft) =======

def _doc_total(items: List[schemas.DocItemIn]) -> float:
    return float(sum(i.qty * i.price for i in items))

@app.post("/purchase", response_model=schemas.DocOut)
def create_purchase(body: schemas.DocCreate, db: Session = Depends(get_db)):
    if not body.items:
        raise HTTPException(400, "Add at least one item")
    doc = Doc(type="purchase", date=body.date, partner=body.partner, status="draft", total=_doc_total(body.items))
    db.add(doc); db.flush()
    for it in body.items:
        db.add(DocItem(doc_id=doc.id, product_id=it.product_id, qty=it.qty, price=it.price))
    db.commit(); db.refresh(doc)
    doc.items
    return doc

@app.post("/sale", response_model=schemas.DocOut)
def create_sale(body: schemas.DocCreate, db: Session = Depends(get_db)):
    if not body.items:
        raise HTTPException(400, "Add at least one item")
    doc = Doc(type="sale", date=body.date, partner=body.partner, status="draft", total=_doc_total(body.items))
    db.add(doc); db.flush()
    for it in body.items:
        db.add(DocItem(doc_id=doc.id, product_id=it.product_id, qty=it.qty, price=it.price))
    db.commit(); db.refresh(doc)
    doc.items
    return doc

# ======= Get doc =======

@app.get("/docs/{doc_id}", response_model=schemas.DocOut)
def get_doc(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Doc).filter(Doc.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Doc not found")
    doc.items
    return doc

# ======= Posting / Unposting =======

def _make_number(doc: Doc) -> str:
    prefix = "P" if doc.type == "purchase" else "S"
    y = doc.date.year
    return f"{prefix}-{y}-{doc.id:06d}"

@app.post("/docs/{doc_id}/post", response_model=schemas.DocOut)
def post_doc(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Doc).filter(Doc.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Doc not found")
    if doc.status == "posted":
        doc.items; return doc

    items = db.query(DocItem).filter(DocItem.doc_id == doc.id).all()

    if doc.type == "purchase":
        for it in items:
            p: Product = db.query(Product).get(it.product_id)
            if not p:
                raise HTTPException(400, f"Product {it.product_id} not found")

            prev_qty = p.qty
            prev_cost = p.avg_cost
            new_qty = prev_qty + it.qty
            if new_qty <= 0:
                p.avg_cost = 0.0
                p.qty = 0.0
            else:
                p.avg_cost = (prev_qty * prev_cost + it.qty * it.price) / new_qty
                p.qty = new_qty

            db.add(StockMove(doc_id=doc.id, product_id=p.id, qty=+it.qty, price=it.price, direction="in"))

    elif doc.type == "sale":
        for it in items:
            p: Product = db.query(Product).get(it.product_id)
            if not p:
                raise HTTPException(400, f"Product {it.product_id} not found")
            if p.qty < it.qty:
                raise HTTPException(400, f"Not enough stock for product #{p.id} ({p.name})")
            p.qty = p.qty - it.qty
            db.add(StockMove(doc_id=doc.id, product_id=p.id, qty=-it.qty, price=it.price, direction="out"))

    doc.status = "posted"
    if not doc.number:
        doc.number = _make_number(doc)
    db.commit(); db.refresh(doc); doc.items
    return doc

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/docs/{doc_id}/unpost", response_model=schemas.DocOut)
def unpost_doc(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Doc).filter(Doc.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Doc not found")
    if doc.status != "posted":
        doc.items; return doc

    items = db.query(DocItem).filter(DocItem.doc_id == doc.id).all()

    if doc.type == "purchase":
        for it in items:
            p: Product = db.query(Product).get(it.product_id)
            if not p:
                raise HTTPException(400, f"Product {it.product_id} not found")
            if p.qty - it.qty < 0:
                raise HTTPException(400, f"Cannot unpost: negative stock for product #{p.id}")
            new_qty = p.qty - it.qty
            if new_qty <= 0:
                p.qty = 0.0
                p.avg_cost = 0.0
            else:
                prev_total = p.qty * p.avg_cost
                new_total = prev_total - it.qty * it.price
                p.qty = new_qty
                p.avg_cost = new_total / new_qty
        db.query(StockMove).filter(StockMove.doc_id == doc.id).delete()

    elif doc.type == "sale":
        for it in items:
            p: Product = db.query(Product).get(it.product_id)
            if not p:
                raise HTTPException(400, f"Product {it.product_id} not found")
            p.qty = p.qty + it.qty
        db.query(StockMove).filter(StockMove.doc_id == doc.id).delete()

    doc.status = "draft"
    db.commit(); db.refresh(doc); doc.items
    return doc