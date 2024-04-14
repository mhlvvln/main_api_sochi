from sqlalchemy import String, Column, Float

from AbstractModel import AbstractModel


class Example(AbstractModel):
    __tablename__ = "examples"

    name = Column(String, index=True, nullable=True)
    in_russia = Column(Float)
    in_dpr = Column(Float)
    in_lpr = Column(Float)
    in_zaporozhie = Column(Float)
    in_kherson = Column(Float)

