from fastapi import HTTPException
from sqlalchemy import select, update, func, case
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from starlette.responses import JSONResponse

from exceptions import SuccessResponse
from .ai_model import get_info_ai_model
from .maps import get_street_by_coordinates
from .models import Application, Shop
from .recomendations import read_recommendation_data
from .schemas import AddSchema, ChangeApplicationSchema


async def getMyApplicationsClient(db: AsyncSession, id: int, status: int, count: int, offset: int = 0,
                                  shop_id: int = None):
    query = select(Application)
    query = query.where(Application.owner_id == id, Application.status == status)
    if shop_id is not None:
        query = query.where(Application.shop_id == shop_id)
    print(count)
    result = await db.execute(query.offset(offset).limit(count))
    result = result.fetchall()
    print(result)
    if result == []:
        return SuccessResponse(status_code=200, data={"applications": []})

    return SuccessResponse(status_code=200, data={"applications": [await res[0].to_dict(shop=True) for res in result]})


async def get_statistics(db: AsyncSession, owner_id: int):
    res = await db.execute(select(Application).where(Application.owner_id == owner_id))
    res = res.fetchall()
    if res is None:
        return SuccessResponse(data={
            "-1": 0,
            "0": 0,
            "1": 1
        })

    result = {
        "-1": 0,
        "0": 0,
        "1": 0
    }

    for row in res:
        if row[0].status == -1:
            result["-1"] += 1
        elif row[0].status == 0:
            result["0"] += 1
        elif row[0].status == 1:
            result["1"] += 1
        else:
            print("else")
    return SuccessResponse(data={"statistics": result})


async def get_statistics_by_ids(db: AsyncSession, owner_ids: str):
    list_ids = list(map(int, owner_ids.split(",")))
    print(list_ids)
    all_data = {}
    for id in list_ids:
        all_data[id] ={
            "-1": 0,
            "0": 0,
            "1": 0
        }

    query = await db.execute(select(Application).where(Application.owner_id.in_(list_ids)))
    query = query.fetchall()
    if query is None:
        return SuccessResponse(data=[])

    for row in query:
        if row[0].status == -1:
            all_data[row[0].owner_id]["-1"] += 1
        elif row[0].status == 0:
            all_data[row[0].owner_id]["0"] += 1
        if row[0].status == 1:
            all_data[row[0].owner_id]["1"] += 1
    return SuccessResponse(data={"statistics": all_data})


async def getMyApplicationsController(db: AsyncSession, id: int, status: int, count: int, offset: int,
                                      shop_id: int = None):
    query = select(Application).where(
        Application.status == status
    ).order_by(Application.id.desc())

    if shop_id is not None:
        query = query.where(Application.shop_id == shop_id)

    applications = await db.execute(query.limit(count).offset(offset))
    applications = applications.fetchall()
    if applications == []:
        return SuccessResponse(status_code=200, data={
            "applications": []
        })
    #[await res[0].to_dict(shop=True) for res in result]

    return SuccessResponse(status_code=200, data={
        "applications": [await application[0].to_dict(shop=True) for application in applications]
    })


async def getMyApplications(db: AsyncSession,
                            id: int,
                            role: str,
                            status: int = 0,
                            count: int = 10,
                            offset: int = 0,
                            shop_id: int = None):
    if role == "client":
        return await getMyApplicationsClient(db, id, status, count, offset, shop_id)
    elif role == "controller":
        return await getMyApplicationsController(db, id, status, count, offset, shop_id)
    else:
        raise HTTPException(status_code=403, detail=f"Неверная роль - {role}")


def remove_non_numeric_chars(value):
    value_str = str(value)
    numeric_chars = [char for char in value_str if char.isdigit() or char == '.']

    numeric_value = ''.join(numeric_chars)
    return float(numeric_value)


async def addApplication(db: AsyncSession, user_id: int,
                         data: AddSchema):
    # получаем данные о месте координат
    #1 - longitude
    #2 - latitude
    maps_info = get_street_by_coordinates(data.coordinates[0], data.coordinates[1])
    first_check = await is_accreditation(db, maps_info[0])
    second_check = await is_accreditation(db, maps_info[1])
    #print(first_check, second_check)

    if first_check[0] is False and second_check[0] is False:
        return HTTPException(404, f"Магазин не аккредитован, адреса: \n1. {maps_info[0]}\n2.{maps_info[1]}")

    if len(first_check) == 2:
        shop_name = first_check[1]
    else:
        #print(second_check)
        shop_name = second_check[1]
    # обращаемся с фотографией к Костиной нейросети
    info_ai_model = await get_info_ai_model(data.photo)
    if info_ai_model['status'] == False:
        raise HTTPException(403, "Это не красный ценник")

    name_product_ai_model = info_ai_model['data']['name']
    category_product_ai_model = info_ai_model['data']['category'].lower()
    category_product_ai_model_capitalize = category_product_ai_model.capitalize()
    price_product_ai_model = info_ai_model['data']['price']

    recommendations = read_recommendation_data()

    for element in recommendations:
        if element[0] == category_product_ai_model:
            print(element[2], price_product_ai_model)
            if element[2] < float(price_product_ai_model):
                shop = await db.execute(select(Shop).where(Shop.name == shop_name).limit(1))
                shop = shop.fetchone()
                if shop is None:
                    raise HTTPException(404, "Магазин не найден, что странно")
                shop = shop[0]
                print(element[2])
                application = Application(name_product=data.name_product,
                                          photo=data.photo,
                                          coordinates=data.coordinates,
                                          owner_id=user_id,
                                          shop_id=shop.id,
                                          category=category_product_ai_model_capitalize,
                                          status=0,
                                          price=remove_non_numeric_chars(price_product_ai_model),
                                          max_price=remove_non_numeric_chars(element[2]))
                db.add(application)
                await db.commit()
                await db.refresh(application)
                return await application.to_dict(shop=True)
            else:
                raise HTTPException(403, f"Цена в норме: рекомендованная: {element[2]},"
                                         f" ваша: {price_product_ai_model}")
    raise HTTPException(404, "Товар не найден среди рекомендованных")


# async def shopAdd(db: AsyncSession):
#     file_path = 'applications/shops.xlsx'
#
#     df = pd.read_excel(file_path, header=2)
#
#     for index, row in df.iterrows():
#         if index < 0:
#             continue
#         if index > 2679:
#             break
#         ppp_number = row['№ п/п']
#         city_name = row['Наименование города/района']
#         subject_name = row['Наименование хозяйствующего субъекта, заключившего Меморандум (ИП/ООО)']
#         inn_ogrn = row['ИНН (ОГРНИП) / ОГРН']
#         memorandum_date = row['Дата заключения Меморандума']
#         trade_objects_count = row['Количество торговых объектов хозяйствующего субъекта, заключившего Меморандум']
#         trade_objects_address = row['Фактический адрес торговых объектов ']
#         product_name = row['Наименование реализуемой продукции (согласно приложению Меморандума)']
#
#         print(f"№ п/п: {ppp_number}")
#         print(f"Наименование города/района: {city_name}")
#         print(f"Наименование хозяйствующего субъекта: {subject_name}")
#         print(f"ИНН (ОГРНИП) / ОГРН: {inn_ogrn}")
#         print(f"Дата заключения Меморандума: {memorandum_date}")
#         print(f"Количество торговых объектов: {trade_objects_count}")
#         print(f"Фактический адрес торговых объектов: {trade_objects_address}")
#         print(f"Наименование реализуемой продукции: {product_name}")
#         print("-------------------------------------")
#         shop = Shop(name=subject_name, address=trade_objects_address)
#         db.add(shop)
#         try:
#             #await db.commit()
#             pass
#         except Exception as e:
#             print()
#             print()
#             print()
#             print(e)
#             print()
#             print()
#             print()
#             print("Наименование - ", subject_name)
#             break


async def is_accreditation(db: AsyncSession, address: str):
    all_data = await db.execute(select(Shop).order_by(Shop.id.asc()))
    all_data = all_data.fetchall()
    new_data = [await data[0].to_dict() for data in all_data]
    if not any(char.isdigit() for char in address):
        return [False]
    address = address.lower()
    first = str(address).lower().replace(" ", "")
    second = str(address).replace(" ", "").replace("улица", "ул. ")
    for row in new_data:
        cleaned_address = row["address"].lower().replace(" ", "")
        if first.lower().replace(" ", "") in cleaned_address:
            return True, row["name"]
        if second.lower().replace(" ", "") in cleaned_address:
            return True, row["name"]
    return [False]


async def getAllController(db: AsyncSession, limit: int = 10, offset: int = 0):
    all = await db.execute(select(Application).order_by(Application.id.desc()).limit(limit).offset(offset))
    all = all.fetchall()
    if all == []:
        return SuccessResponse(data={"applications": []})
    return SuccessResponse(data={"applications": [await element[0].to_dict(shop=True) for element in all]})


async def changeStatus(db: AsyncSession, data: ChangeApplicationSchema):
    if data.status not in [-1, 1]:
        raise HTTPException(403, "Статус неверный передан")
    if data.status == -1:
        if data.controller_comment is None:
            raise HTTPException(403, "Комментарий обязателен")

        ai_data = await get_info_ai_model(data.controller_photo)
        if ai_data['status'] == False:
            raise HTTPException(403, "Вероятно это и вовсе не чек. Закрыть отрицательно нельзя")
        upd = await db.execute(
            update(Application).where(Application.id == data.application_id).values(status=data.status,
                                                                                    photo_controller=data.controller_photo, controller_comment=data.controller_comment))
        await db.commit()
        return SuccessResponse()

    application = await db.execute(select(Application).where(Application.id == data.application_id).limit(1))
    application = application.fetchone()
    if application is None:
        raise HTTPException(404, "Нет заявки")

    application = application[0]

    ai_data = await get_info_ai_model(data.controller_photo)
    if ai_data['status'] == False:
        raise HTTPException(403, "Товар не относится к социальным")

    name_product_ai_model = ai_data['data']['name']
    category_product_ai_model = ai_data['data']['category'].lower()
    price_product_ai_model = ai_data['data']['price']

    #recommendations = read_recommendation_data()

    #print(category_product_ai_model.lower(), application.category.lower())
    if category_product_ai_model.lower() == application.category.lower():
        if remove_non_numeric_chars(price_product_ai_model) > remove_non_numeric_chars(application.max_price):
            raise HTTPException(403, f"Рекомендация({application.max_price}) меньше, чем предлагаемая цена({price_product_ai_model})")

        upd = await db.execute(update(Application).where(Application.id == data.application_id).values(status=data.status,
                                                                                                       photo_controller=data.controller_photo, controller_comment=data.controller_comment))
        await db.commit()
        return SuccessResponse()
    return HTTPException(404, "Не найден товар")



