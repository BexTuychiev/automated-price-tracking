from firecrawl import FirecrawlApp
from models import Product as PydanticProduct
from storage import Session, PriceHistory, Product as DBProduct
from notifications import send_price_alert
from config import settings
from dotenv import load_dotenv
import asyncio
import warnings

load_dotenv()


async def check_single_product(url: str, normalized_url: str = None) -> PydanticProduct:
    """Check a single product URL and return its details."""
    app = FirecrawlApp()

    data = app.scrape_url(
        url,
        params={
            "formats": ["extract"],
            "extract": {"schema": PydanticProduct.model_json_schema()},
        },
    )
    
    product = PydanticProduct(**data["extract"])
    if normalized_url:
        product.url = normalized_url
    return product


async def check_prices():
    # Set up Firecrawl and database session
    app = FirecrawlApp()
    session = Session()

    try:
        # Get all products from database
        products = session.query(DBProduct).all()

        # Iterate over each product
        for product in products:
            try:
                updated_product = await check_single_product(product.url)

                # Get the earliest price from the database
                last_price = (
                    session.query(PriceHistory)
                    .filter_by(product_url=product.url)
                    .order_by(PriceHistory.timestamp.asc())
                    .first()
                )

                if last_price and last_price.price > updated_product.price:
                    drop_pct = (
                        last_price.price - updated_product.price
                    ) / last_price.price

                    # Send notification if price drop exceeds threshold
                    if drop_pct >= settings.PRICE_DROP_THRESHOLD:
                        await send_price_alert(
                            product.name,
                            last_price.price,
                            updated_product.price,
                            product.url,
                        )

                # Save new price
                session.add(
                    PriceHistory(
                        product_url=product.url,
                        price=updated_product.price,
                        product_name=product.name,
                    )
                )
            except Exception as e:
                warnings.warn(f"Error checking product {product.url}: {e}")
                continue

        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    asyncio.run(check_prices())