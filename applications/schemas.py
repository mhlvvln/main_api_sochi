from typing import Tuple, Optional

from pydantic import BaseModel


class AddSchema(BaseModel):
    name_product: str
    photo: str
    coordinates: Tuple[float, float]
    shop_id: Optional[int]


class ChangeApplicationSchema(BaseModel):
    application_id: int
    controller_photo: str
    status: int
    controller_comment: Optional[str]