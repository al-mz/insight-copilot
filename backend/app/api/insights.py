from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, distinct, func
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import (
    Actor,
    Address,
    Category,
    City,
    Country,
    Customer,
    Film,
    Inventory,
    Payment,
    Rental,
    Store,
)

router = APIRouter()


@router.get("/insights")
async def get_insights(db: Session = Depends(get_db)):
    try:
        # TODO: Implement insights generation logic
        return {"status": "success", "insights": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/top-films")
async def get_top_films(limit: int = 10, db: Session = Depends(get_db)):
    try:
        # Get top films by rental count
        top_films = (
            db.query(
                Film.title,
                func.count(Rental.rental_id).label("rental_count"),
                Film.rental_rate,
                func.sum(Payment.amount).label("total_revenue"),
            )
            .join(Rental, Film.film_id == Rental.inventory_id)
            .join(Payment, Rental.rental_id == Payment.rental_id)
            .group_by(Film.film_id)
            .order_by(desc("rental_count"))
            .limit(limit)
            .all()
        )

        return {
            "status": "success",
            "data": [
                {
                    "title": film.title,
                    "rental_count": film.rental_count,
                    "rental_rate": float(film.rental_rate),
                    "total_revenue": float(film.total_revenue),
                }
                for film in top_films
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/category-performance")
async def get_category_performance(db: Session = Depends(get_db)):
    try:
        # Get performance metrics by category
        category_stats = (
            db.query(
                Category.name,
                func.count(Film.film_id).label("film_count"),
                func.avg(Film.rental_rate).label("avg_rental_rate"),
                func.sum(Payment.amount).label("total_revenue"),
            )
            .join(Film, Category.category_id == Film.film_id)
            .join(Rental, Film.film_id == Rental.inventory_id)
            .join(Payment, Rental.rental_id == Payment.rental_id)
            .group_by(Category.category_id)
            .all()
        )

        return {
            "status": "success",
            "data": [
                {
                    "category": cat.name,
                    "film_count": cat.film_count,
                    "avg_rental_rate": float(cat.avg_rental_rate),
                    "total_revenue": float(cat.total_revenue),
                }
                for cat in category_stats
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/customer-activity")
async def get_customer_activity(limit: int = 10, db: Session = Depends(get_db)):
    try:
        # Get most active customers
        active_customers = (
            db.query(
                Customer.first_name,
                Customer.last_name,
                func.count(Rental.rental_id).label("rental_count"),
                func.sum(Payment.amount).label("total_spent"),
            )
            .join(Rental, Customer.customer_id == Rental.customer_id)
            .join(Payment, Rental.rental_id == Payment.rental_id)
            .group_by(Customer.customer_id)
            .order_by(desc("total_spent"))
            .limit(limit)
            .all()
        )

        return {
            "status": "success",
            "data": [
                {
                    "customer_name": f"{cust.first_name} {cust.last_name}",
                    "rental_count": cust.rental_count,
                    "total_spent": float(cust.total_spent),
                }
                for cust in active_customers
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/store-performance")
async def get_store_performance(db: Session = Depends(get_db)):
    try:
        # Get store performance metrics
        store_stats = (
            db.query(
                Store.store_id,
                func.count(Rental.rental_id).label("rental_count"),
                func.sum(Payment.amount).label("total_revenue"),
                func.avg(Payment.amount).label("avg_transaction"),
            )
            .join(Rental, Store.store_id == Rental.staff_id)
            .join(Payment, Rental.rental_id == Payment.rental_id)
            .group_by(Store.store_id)
            .all()
        )

        return {
            "status": "success",
            "data": [
                {
                    "store_id": store.store_id,
                    "rental_count": store.rental_count,
                    "total_revenue": float(store.total_revenue),
                    "avg_transaction": float(store.avg_transaction),
                }
                for store in store_stats
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/actor-popularity")
async def get_actor_popularity(limit: int = 10, db: Session = Depends(get_db)):
    try:
        # Get most popular actors based on film rentals
        popular_actors = (
            db.query(
                Actor.first_name,
                Actor.last_name,
                func.count(Rental.rental_id).label("rental_count"),
                func.sum(Payment.amount).label("total_revenue"),
            )
            .join(Film, Actor.actor_id == Film.film_id)
            .join(Rental, Film.film_id == Rental.inventory_id)
            .join(Payment, Rental.rental_id == Payment.rental_id)
            .group_by(Actor.actor_id)
            .order_by(desc("rental_count"))
            .limit(limit)
            .all()
        )

        return {
            "status": "success",
            "data": [
                {
                    "actor_name": f"{actor.first_name} {actor.last_name}",
                    "rental_count": actor.rental_count,
                    "total_revenue": float(actor.total_revenue),
                }
                for actor in popular_actors
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/sales-overview")
async def get_sales_overview(db: Session = Depends(get_db)):
    try:
        # Get monthly sales data for the past year
        sales_data = (
            db.query(
                func.strftime("%Y-%m", Payment.payment_date).label("date"),
                func.sum(Payment.amount).label("Sales"),
                func.sum(Payment.amount * 0.7).label("Profit"),  # Assuming 70% profit margin
                func.sum(Payment.amount * 0.3).label("Expenses"),  # Assuming 30% expenses
                func.count(distinct(Rental.customer_id)).label("Customers"),
            )
            .join(Rental, Payment.rental_id == Rental.rental_id)
            .group_by(func.strftime("%Y-%m", Payment.payment_date))
            .order_by(func.strftime("%Y-%m", Payment.payment_date))
            .limit(12)
            .all()
        )

        return {
            "status": "success",
            "data": [
                {
                    "date": sale.date,
                    "Sales": float(sale.Sales),
                    "Profit": float(sale.Profit),
                    "Expenses": float(sale.Expenses),
                    "Customers": sale.Customers,
                }
                for sale in sales_data
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/regional-sales")
async def get_regional_sales(db: Session = Depends(get_db)):
    try:
        # Get sales data by country
        regional_data = (
            db.query(
                Country.country.label("region"),
                func.sum(Payment.amount).label("sales"),
                func.count(distinct(Rental.customer_id)).label("marketShare"),
            )
            .join(City, Country.country_id == City.country_id)
            .join(Address, City.city_id == Address.city_id)
            .join(Store, Address.address_id == Store.address_id)
            .join(Inventory, Store.store_id == Inventory.store_id)
            .join(Rental, Inventory.inventory_id == Rental.inventory_id)
            .join(Payment, Rental.rental_id == Payment.rental_id)
            .group_by(Country.country)
            .order_by(func.sum(Payment.amount).desc())
            .all()
        )

        return {
            "status": "success",
            "data": [
                {"region": region.region, "sales": float(region.sales), "marketShare": region.marketShare}
                for region in regional_data
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
