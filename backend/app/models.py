from sqlalchemy import Column, Integer, String, Float, Date, Enum, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# ====== Справочники ======

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    sku = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    barcode = Column(String, nullable=True)

    # оперативный учёт
    qty = Column(Float, nullable=False, default=0.0)
    avg_cost = Column(Float, nullable=False, default=0.0)

# ====== Документы ======

class Doc(Base):
    __tablename__ = "docs"
    id = Column(Integer, primary_key=True)
    type = Column(Enum("purchase", "sale", name="doc_type"), nullable=False)
    number = Column(String, nullable=True, index=True)   # присваивается при проведении
    date = Column(Date, nullable=False)
    partner = Column(String, nullable=True)              # vendor/client
    status = Column(Enum("draft", "posted", "canceled", name="doc_status"), nullable=False, default="draft")
    total = Column(Float, nullable=False, default=0.0)

    items = relationship("DocItem", cascade="all, delete-orphan", back_populates="doc")

class DocItem(Base):
    __tablename__ = "doc_items"
    id = Column(Integer, primary_key=True)
    doc_id = Column(Integer, ForeignKey("docs.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    qty = Column(Float, nullable=False)
    price = Column(Float, nullable=False)

    doc = relationship("Doc", back_populates="items")

# ====== Движения по складу (история) ======

class StockMove(Base):
    __tablename__ = "stock_moves"
    id = Column(Integer, primary_key=True)
    doc_id = Column(Integer, ForeignKey("docs.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    # +qty для прихода, -qty для продажи
    qty = Column(Float, nullable=False)
    price = Column(Float, nullable=False)  # покупная для purchase, продажная для sale (для отчётов)
    direction = Column(Enum("in", "out", name="move_dir"), nullable=False)

    __table_args__ = (
        CheckConstraint("qty <> 0"),
    )