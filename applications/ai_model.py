import os

import requests


async def get_info_ai_model(photo: str):
    url = os.getenv("ML_SERVICE")
    body = {
        "image": photo
    }
    request = requests.post(url=url, json=body).json()
    request['data']['price'] = str(float(request['data']['price'])+0)
    return request
    # return {
    #     "status": True,
    #     "data": {
    #         "name": "name",
    #         "category": "Лук репчатый",
    #         "price": 10000
    #     }
    # }
