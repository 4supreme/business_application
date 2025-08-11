from datetime import date
from typing import List, Optional
from pydantic import BaseModel

# ===== Products =====
class ProductCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    unit: Optional[str] = None
    barcode: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    name: str
    sku: Optional[str]
    unit: Optional[str]
    barcode: Optional[str]
    qty: float
    avg_cost: float
    class Config:
        orm_mode = True

# ===== Docs =====
class DocItemIn(BaseModel):
    product_id: int
    qty: float
    price: float

class DocCreate(BaseModel):
    date: date
    partner: Optional[str] = None
    items: List[DocItemIn]

class DocItemOut(BaseModel):
    product_id: int
    qty: float
    price: float
    class Config:
        orm_mode = True

class DocOut(BaseModel):
    id: int
    type: str
    number: Optional[str]
    date: date
    partner: Optional[str]
    status: str
    total: float
    items: List[DocItemOut]
    class Config:
        orm_mode = True