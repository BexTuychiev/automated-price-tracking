from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProductCreate(BaseModel):
    """Schema for creating a new product"""

    url: str = Field(description="The URL of the product")
    name: str = Field(description="The product name/title")
    price: float = Field(description="The current price of the product")
    currency: str = Field(description="Currency code (USD, EUR, etc)")
    check_date: str = Field(
        default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d")
    )
    main_image_url: str = Field(description="The URL of the main image of the product")

    class Config:
        from_attributes = True  # Enables ORM mode


class Product(ProductCreate):
    """Schema for reading a product"""

    pass


class PriceHistoryCreate(BaseModel):
    """Schema for creating a price history entry"""

    product_url: str
    price: float
    product_name: str

    class Config:
        from_attributes = True


class PriceHistory(PriceHistoryCreate):
    """Schema for reading a price history entry"""

    id: int
    timestamp: datetime