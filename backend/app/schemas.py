from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ---------- Products ----------

class ProductCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    unit: Optional[str] = "pcs"
    barcode: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    name: str
    sku: Optional[str] = None
    unit: Optional[str] = "pcs"
    barcode: Optional[str] = None
    qty_on_hand: float
    avg_cost: float

    class Config:
        from_attributes = True


# ---------- Clients ----------

class ClientCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None

class ClientOut(ClientCreate):
    id: int
    class Config:
        from_attributes = True


# ---------- Purchase ----------

class PurchaseItemIn(BaseModel):
    product_id: int
    qty: float
    price: float   # закупочная цена за единицу

class PurchaseCreate(BaseModel):
    date: Optional[str] = None   # "YYYY-MM-DD" или ISO
    vendor: Optional[str] = None
    items: List[PurchaseItemIn]

class PurchaseOut(BaseModel):
    id: int
    date: datetime
    vendor: Optional[str] = None
    total_amount: float
    class Config:
        from_attributes = True


# ---------- Sale ----------

class SaleItemIn(BaseModel):
    product_id: int
    qty: float
    price: float   # продажная цена за единицу

class SaleCreate(BaseModel):
    client_id: Optional[int] = None
    items: List[SaleItemIn]

class SaleItemOut(BaseModel):
    product_id: int
    qty: float
    price: float
    line_total: float
    line_cogs: float
    class Config:
        from_attributes = True

class SaleOut(BaseModel):
    id: int
    date: datetime
    client_id: Optional[int] = None
    total_amount: float
    total_cogs: float
    gross_profit: float
    items: List[SaleItemOut]
    class Config:
        from_attributes = True


# ---------- Treasury (Bank & Cash) ----------

class CashTxnCreate(BaseModel):
    date: Optional[str] = None         # "YYYY-MM-DD" или ISO
    account: str                       # 'cash' | 'bank'
    direction: str                     # 'in' | 'out'
    amount: float
    counterparty: Optional[str] = None
    note: Optional[str] = None

class CashTxnOut(BaseModel):
    id: int
    date: datetime
    account: str
    direction: str
    amount: float
    counterparty: Optional[str] = None
    note: Optional[str] = None
    class Config:
        from_attributes = True

class CashBalance(BaseModel):
    cash: float
    bank: float
    total: float
