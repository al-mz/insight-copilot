from sqlalchemy import Column, DateTime, Integer, Numeric, SmallInteger, String, Text

from .database import Base


class Actor(Base):
    __tablename__ = "actor"

    actor_id = Column(Integer, primary_key=True)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    last_update = Column(DateTime, nullable=False)


class Category(Base):
    __tablename__ = "category"

    category_id = Column(SmallInteger, primary_key=True)
    name = Column(String(25), nullable=False)
    last_update = Column(DateTime, nullable=False)


class Film(Base):
    __tablename__ = "film"

    film_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    release_year = Column(String(4))
    language_id = Column(SmallInteger, nullable=False)
    original_language_id = Column(SmallInteger)
    rental_duration = Column(SmallInteger, nullable=False, default=3)
    rental_rate = Column(Numeric(4, 2), nullable=False, default=4.99)
    length = Column(SmallInteger)
    replacement_cost = Column(Numeric(5, 2), nullable=False, default=19.99)
    rating = Column(String(10), default="G")
    special_features = Column(String(100))
    last_update = Column(DateTime, nullable=False)


class Customer(Base):
    __tablename__ = "customer"

    customer_id = Column(Integer, primary_key=True)
    store_id = Column(Integer, nullable=False)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    email = Column(String(50))
    address_id = Column(Integer, nullable=False)
    active = Column(String(1), nullable=False, default="Y")
    create_date = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=False)


class Store(Base):
    __tablename__ = "store"

    store_id = Column(Integer, primary_key=True)
    manager_staff_id = Column(SmallInteger, nullable=False)
    address_id = Column(Integer, nullable=False)
    last_update = Column(DateTime, nullable=False)


class Rental(Base):
    __tablename__ = "rental"

    rental_id = Column(Integer, primary_key=True)
    rental_date = Column(DateTime, nullable=False)
    inventory_id = Column(Integer, nullable=False)
    customer_id = Column(Integer, nullable=False)
    return_date = Column(DateTime)
    staff_id = Column(SmallInteger, nullable=False)
    last_update = Column(DateTime, nullable=False)


class Payment(Base):
    __tablename__ = "payment"

    payment_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False)
    staff_id = Column(SmallInteger, nullable=False)
    rental_id = Column(Integer)
    amount = Column(Numeric(5, 2), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=False)
