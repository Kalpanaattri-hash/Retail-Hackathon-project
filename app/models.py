from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)

    sales = relationship("Sale", back_populates="product")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    segment = Column(String(100), nullable=False, index=True)


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    region = Column(String(100), nullable=False, index=True)
    revenue = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    sale_date = Column(Date, nullable=False, index=True)

    product = relationship("Product", back_populates="sales")
