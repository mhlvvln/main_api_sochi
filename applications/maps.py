import os

import requests

access_token = os.getenv("MAPS_TOKEN")


def get_street_by_coordinates(longitude: float, latitude: float):
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={access_token}&geocode={longitude},{latitude}&results=1&format=json"
    response = requests.get(url).json()
    short_name = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['name']
    full_name = (response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['text'])
    full_name = full_name.replace("Украина, ", "")
    return short_name, full_name


if __name__ == "__main__":
    print(get_street_by_coordinates(38.495244, 47.785964))