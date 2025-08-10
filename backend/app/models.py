from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

# ---------- Справочники ----------

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, index=True, nullable=False)
    unit = Column(String, default="pcs")
    barcode = Column(String, nullable=True)

    # Текущие остатки и средняя себестоимость (упрощённо)
    qty_on_hand = Column(Float, default=0.0)
    avg_cost = Column(Float, default=0.0)

    sale_items = relationship("SaleItem", back_populates="product")
    purchase_items = relationship("PurchaseItem", back_populates="product")


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    sales = relationship("Sale", back_populates="client", cascade="all, delete-orphan")


# ---------- Документы: Приход (закупка) ----------

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    vendor = Column(String, nullable=True)  # для MVP просто строка
    total_amount = Column(Float, default=0.0)

    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"
    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    qty = Column(Float, nullable=False)
    price = Column(Float, nullable=False)  # закупочная цена

    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product", back_populates="purchase_items")


# ---------- Документы: Продажа ----------

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    total_amount = Column(Float, default=0.0)   # сумма по продажным ценам
    total_cogs = Column(Float, default=0.0)     # себестоимость по средней
    gross_profit = Column(Float, default=0.0)   # валовая прибыль

    client = relationship("Client", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    qty = Column(Float, nullable=False)
    price = Column(Float, nullable=False)  # продажная цена за единицу
    line_total = Column(Float, default=0.0)
    line_cogs = Column(Float, default=0.0)  # qty * avg_cost на момент продажи

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")


# ---------- Движения склада (аудит) ----------

class StockMove(Base):
    __tablename__ = "stock_moves"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    product_id = Column(Integer, ForeignKey("products.id"))
    qty = Column(Float, nullable=False)   # приход >0, расход <0
    ref_type = Column(String)             # 'purchase' / 'sale'
    ref_id = Column(Integer)              # id документа

    product = relationship("Product")


# ---------- Казначейство (Банк и касса) ----------

class CashTxn(Base):
    """
    Простая таблица движений денег:
    - account: 'cash' | 'bank'
    - direction: 'in' | 'out'
    """
    __tablename__ = "cash_txn"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    account = Column(String, index=True)     # cash / bank
    direction = Column(String, index=True)   # in / out
    amount = Column(Float, nullable=False)
    counterparty = Column(String, nullable=True)  # от кого / кому
    note = Column(String, nullable=True)
