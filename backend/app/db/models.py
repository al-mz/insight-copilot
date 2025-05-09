from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class Actor(Base):
    __tablename__ = "actor"

    actor_id = Column(Integer, primary_key=True)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    last_update = Column(DateTime, nullable=False)
    films = relationship("Film", secondary="film_actor", back_populates="actors")


class Category(Base):
    __tablename__ = "category"

    category_id = Column(SmallInteger, primary_key=True)
    name = Column(String(25), nullable=False)
    last_update = Column(DateTime, nullable=False)
    films = relationship("Film", secondary="film_category", back_populates="categories")


class Film(Base):
    __tablename__ = "film"

    film_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    release_year = Column(String(4))
    language_id = Column(SmallInteger, ForeignKey("language.language_id"), nullable=False)
    original_language_id = Column(SmallInteger, ForeignKey("language.language_id"))
    rental_duration = Column(SmallInteger, nullable=False, default=3)
    rental_rate = Column(Numeric(4, 2), nullable=False, default=4.99)
    length = Column(SmallInteger)
    replacement_cost = Column(Numeric(5, 2), nullable=False, default=19.99)
    rating = Column(String(10), default="G")
    special_features = Column(String(100))
    last_update = Column(DateTime, nullable=False)
    language = relationship("Language", foreign_keys=[language_id])
    original_language = relationship("Language", foreign_keys=[original_language_id])
    inventory = relationship("Inventory", back_populates="film")
    actors = relationship("Actor", secondary="film_actor", back_populates="films")
    categories = relationship("Category", secondary="film_category", back_populates="films")


class Customer(Base):
    __tablename__ = "customer"

    customer_id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("store.store_id"), nullable=False)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    email = Column(String(50))
    address_id = Column(Integer, ForeignKey("address.address_id"), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    create_date = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=False)
    store = relationship("Store", back_populates="customers")
    address = relationship("Address", back_populates="customers")
    rentals = relationship("Rental", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")


class Store(Base):
    __tablename__ = "store"

    store_id = Column(Integer, primary_key=True)
    manager_staff_id = Column(SmallInteger, ForeignKey("staff.staff_id"), nullable=False)
    address_id = Column(Integer, ForeignKey("address.address_id"), nullable=False)
    last_update = Column(DateTime, nullable=False)
    address = relationship("Address", back_populates="stores")
    manager = relationship("Staff", foreign_keys=[manager_staff_id])
    inventory = relationship("Inventory", back_populates="store")
    customers = relationship("Customer", back_populates="store")


class Rental(Base):
    __tablename__ = "rental"

    rental_id = Column(Integer, primary_key=True)
    rental_date = Column(DateTime, nullable=False)
    inventory_id = Column(Integer, ForeignKey("inventory.inventory_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    return_date = Column(DateTime)
    staff_id = Column(SmallInteger, ForeignKey("staff.staff_id"), nullable=False)
    last_update = Column(DateTime, nullable=False)
    inventory = relationship("Inventory", back_populates="rentals")
    customer = relationship("Customer", back_populates="rentals")
    staff = relationship("Staff", back_populates="rentals")
    payments = relationship("Payment", back_populates="rental")


class Payment(Base):
    __tablename__ = "payment"

    payment_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    staff_id = Column(SmallInteger, ForeignKey("staff.staff_id"), nullable=False)
    rental_id = Column(Integer, ForeignKey("rental.rental_id"))
    amount = Column(Numeric(5, 2), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=False)
    customer = relationship("Customer", back_populates="payments")
    staff = relationship("Staff", back_populates="payments")
    rental = relationship("Rental", back_populates="payments")


class Country(Base):
    __tablename__ = "country"

    country_id = Column(SmallInteger, primary_key=True)
    country = Column(String(50), nullable=False)
    last_update = Column(DateTime)
    cities = relationship("City", back_populates="country")


class City(Base):
    __tablename__ = "city"

    city_id = Column(Integer, primary_key=True)
    city = Column(String(50), nullable=False)
    country_id = Column(SmallInteger, ForeignKey("country.country_id"), nullable=False)
    last_update = Column(DateTime, nullable=False)
    country = relationship("Country", back_populates="cities")
    addresses = relationship("Address", back_populates="city")


class Address(Base):
    __tablename__ = "address"

    address_id = Column(Integer, primary_key=True)
    address = Column(String(50), nullable=False)
    address2 = Column(String(50))
    district = Column(String(20), nullable=False)
    city_id = Column(Integer, ForeignKey("city.city_id"), nullable=False)
    postal_code = Column(String(10))
    phone = Column(String(20), nullable=False)
    last_update = Column(DateTime, nullable=False)
    city = relationship("City", back_populates="addresses")
    stores = relationship("Store", back_populates="address")
    customers = relationship("Customer", back_populates="address")
    staff = relationship("Staff", back_populates="address")


class Staff(Base):
    __tablename__ = "staff"

    staff_id = Column(SmallInteger, primary_key=True)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    address_id = Column(Integer, ForeignKey("address.address_id"), nullable=False)
    picture = Column(Text)
    email = Column(String(50))
    store_id = Column(Integer, ForeignKey("store.store_id"), nullable=False)
    active = Column(SmallInteger, nullable=False, default=1)
    username = Column(String(16), nullable=False)
    password = Column(String(40))
    last_update = Column(DateTime, nullable=False)
    address = relationship("Address", back_populates="staff")
    store = relationship("Store", foreign_keys=[store_id])
    rentals = relationship("Rental", back_populates="staff")
    payments = relationship("Payment", back_populates="staff")


class Language(Base):
    __tablename__ = "language"

    language_id = Column(SmallInteger, primary_key=True)
    name = Column(String(20), nullable=False)
    last_update = Column(DateTime, nullable=False)


class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey("film.film_id"), nullable=False)
    store_id = Column(Integer, ForeignKey("store.store_id"), nullable=False)
    last_update = Column(DateTime, nullable=False)
    film = relationship("Film", back_populates="inventory")
    store = relationship("Store", back_populates="inventory")
    rentals = relationship("Rental", back_populates="inventory")


class FilmActor(Base):
    __tablename__ = "film_actor"

    actor_id = Column(Integer, ForeignKey("actor.actor_id"), primary_key=True)
    film_id = Column(Integer, ForeignKey("film.film_id"), primary_key=True)
    last_update = Column(DateTime, nullable=False)


class FilmCategory(Base):
    __tablename__ = "film_category"

    film_id = Column(Integer, ForeignKey("film.film_id"), primary_key=True)
    category_id = Column(SmallInteger, ForeignKey("category.category_id"), primary_key=True)
    last_update = Column(DateTime, nullable=False)
