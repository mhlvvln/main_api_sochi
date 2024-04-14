from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from applications.models import User
from applications.recomendations import read_recommendation_data
from applications.schemas import AddSchema, ChangeApplicationSchema
from applications.service import getMyApplications, is_accreditation, addApplication, getAllController, get_statistics, \
    get_statistics_by_ids, changeStatus
from database.database import get_session
from exceptions import SuccessResponse
from utils import method_for_role

security = HTTPBearer()

application_router = APIRouter()
shops_router = APIRouter()
users_router = APIRouter()
recommendations_router = APIRouter()


@users_router.get("/statistics")
async def getStatistic(owner_id: int,
                        token: HTTPAuthorizationCredentials = Depends(security),
                        db: AsyncSession = Depends(get_session)):
    user_data = await method_for_role(token, ["controller"])
    return await get_statistics(db, owner_id)


@users_router.get("/statistics_by_ids")
async def getStatistic(owner_ids: str,
                        token: HTTPAuthorizationCredentials = Depends(security),
                        db: AsyncSession = Depends(get_session)):
    user_data = await method_for_role(token, ["controller"])
    return await get_statistics_by_ids(db, owner_ids)


@recommendations_router.get("/all_products")
async def get_all_products():
    data = read_recommendation_data()
    result = []
    count = 0
    for row in data:
        photos = ["http://79.174.80.94:8015/photos/5851429215f488bb5ca32aff7b2fe4169816eac8.png",
                  "https://oldfarmer.ru/wp-content/uploads/2019/12/belokochannaya-kapusta.jpg",
                  "https://yastatic.net/naydex/yandex-search/Mkc6VD565/5ac53cTor/wTEsvCFPDUJ1Q7WsKcbzBGK8UALtb7qwZt4yoebO_-PKxK3DMCPeLvTBOs5MlkW73XPFnzI6tBxaZFdnLmzT6o0J1BChg8iG_ZtcCOl6rxBOzXxbwXbSUIw",
                  "https://polza4u.ru/wp-content/uploads/2022/06/svekla-scaled.jpg",
                  "https://gas-kvas.com/grafic/uploads/posts/2023-09/1695965688_gas-kvas-com-p-kartinki-morkov-12.png",
                  "https://avatars.mds.yandex.net/i?id=f651893a2e5856f5e5e8d871dd4bc9cefd217ea3-12585680-images-thumbs&n=13"
                 ]
        photo = ""
        if count < 6:
            photo = photos[count]
        result.append({
            "name": row[0].capitalize(),
            "unit": row[1],
            "price": row[2],
            "photo": photo
        })
        count+=1
    return SuccessResponse(data={"recommendations": result})


@users_router.get("/me")
async def me(token: HTTPAuthorizationCredentials = Depends(security),
             db: AsyncSession = Depends(get_session)):
    user_data = await method_for_role(token, ["client", "controller"])
    user_id: int = user_data['id']
    user = await db.execute(select(User).where(User.id == user_id).limit(1))
    user = user.fetchone()
    if user is None:
        raise HTTPException(404, "User not found")
    user = user[0]
    return SuccessResponse(data={"user": await user.to_dict()})


# @shops_router.get("/add")
# async def addShops(db: AsyncSession = Depends(get_session)):
#     return await addApplication(db)


@shops_router.get("/is_accreditation")
async def all_data(address: str, db: AsyncSession = Depends(get_session)):
    return await is_accreditation(db, address)


# статус 0 - заявка открыта
# статус 1 - заявка закрыта

@application_router.get("/get_my_applications")
async def get_my_applications(status: int = 0,
                              count: int = 10,
                              offset: int = 0,
                              shop_id: int = None,
                              token: HTTPAuthorizationCredentials = Depends(security),
                              db: AsyncSession = Depends(get_session)):
    user_data = await method_for_role(token, ["client", "controller"])
    user_id = user_data['id']
    user_role = user_data['role']
    return await getMyApplications(db, user_id, user_role, status, count, offset, shop_id)


@application_router.get("/getAll")
async def get_all_controller(limit: int = 10,
                             offset: int = 0,
                             token: HTTPAuthorizationCredentials = Depends(security),
                             db: AsyncSession = Depends(get_session)):
    user_data = await method_for_role(token, ["controller"])
    user_id = user_data['id']
    return await getAllController(db, limit, offset)


@application_router.post("/add")
async def add_application(data: AddSchema,
                          token: HTTPAuthorizationCredentials = Depends(security),
                          db: AsyncSession = Depends(get_session)):
    user_data = await method_for_role(token, "client")
    user_id = user_data['id']
    return await addApplication(db, user_id, data)


@application_router.post("/changeStatus")
async def change_application(data: ChangeApplicationSchema,
                             token: HTTPAuthorizationCredentials = Depends(security),
                             db: AsyncSession = Depends(get_session)):
    user_data = await method_for_role(token, "controller")
    user_id = user_data['id']
    return await changeStatus(db, data)
