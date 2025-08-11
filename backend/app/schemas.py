from datetime import date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

# ===== Products =====
class ProductCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    unit: Optional[str] = None
    barcode: Optional[str] = None

class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    sku: Optional[str] = None
    unit: Optional[str] = None
    barcode: Optional[str] = None
    qty: float
    avg_cost: float

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
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    qty: float
    price: float

class DocOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: str
    number: Optional[str] = None
    date: date
    partner: Optional[str] = None
    status: str
    total: float
    items: List[DocItemOut]