from sqlalchemy import Column, String, ARRAY, Float, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship

from AbstractModel import AbstractModel


class Category(AbstractModel):
    __tablename__ = "categories"
    name = Column(String, nullable=False)


class Status(AbstractModel):
    __tablename__ = "statuses"
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    status = Column(Integer, nullable=False)


class Shop(AbstractModel):
    __tablename__ = "shops"
    name = Column(String)
    address = Column(String)
    inn_ogrn = Column(String)
    accreditation = Column(Boolean, default=True)

    applications = relationship("Application", back_populates="shop", lazy="selectin")


class Application(AbstractModel):
    # статус 0 - заявка стартовала
    # статус 1 - заявка закрыта успехом
    # статус -1 - заявка закрыта неуспехом(например - она оказалась ложной)
    #
    #

    __tablename__ = "applications"
    name_product = Column(String, nullable=False)
    photo = Column(String, nullable=False)
    coordinates = Column(ARRAY(Float), nullable=False)
    owner_id = Column(Integer, nullable=False)
    status = Column(Integer)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=True)
    category = Column(String, nullable=True)
    photo_controller = Column(String, nullable=True)
    type = Column(String, server_default="overstated")
    shop = relationship("Shop", back_populates="applications", lazy="selectin")
    price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    controller_comment = Column(String)
    # статус фото дата получения адрес


class Recommendation(AbstractModel):
    __tablename__ = "recommendations"
    group = Column(String, nullable=False)
    price = Column(Float, nullable=False)


class User(AbstractModel):
    __tablename__ = "users"

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    patronymic = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True, index=True)
    code = Column(Integer, default=None)
    role = Column(String)
    photo = Column(String, nullable=True)
    #phone = Column(String, nullable=False, unique=True, index=True)
    #phone_confirmed = Column(Boolean, default=False)
    email_confirmed = Column(Boolean, default=False)