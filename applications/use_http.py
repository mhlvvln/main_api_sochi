import random

import requests

photos = [
    {
        "name": "Банан",
        "normal": "http://79.174.80.94:8015/photos/ec26151dd96e955ddc18e8eafe5118d1c803a438.jpeg",
        "not_normal": "http://79.174.80.94:8015/photos/b94524f349bc4134ce6312b64ac4f05dca0e25d2.jpeg"
    },
    {
        "name": "Колбаса",
        "normal": "http://79.174.80.94:8015/photos/3fcfab421495880f03ae91155d1748f4e42b6870.jpeg",
        "not_normal": "http://79.174.80.94:8015/photos/dfd7f230fca645980032cbe83ea6dba8b68a8caf.jpeg"
    },
    {
        "name": "Мука",
        "normal": "http://79.174.80.94:8015/photos/c42f9f0d0791474ec89bc2663390771a309a2c29.jpeg",
        "not_normal": "http://79.174.80.94:8015/photos/dcbed53a6b90b2de01aa861bc9a1495ac774979b.jpeg"
    },
    {
        "name": "Огурец",
        "normal": "http://79.174.80.94:8015/photos/7e4000bcecca4daaedb0b8bf57bb25a22d999c50.jpeg",
        "not_normal": "http://79.174.80.94:8015/photos/339bdba66aa76cfc2f337f7da2f3006458171b8f.jpeg"
    },
    {
        "name": "Сахар",
        "normal": "http://79.174.80.94:8015/photos/82c591b33f610c634d358f4aae17d14d704e2f96.jpeg",
        "not_normal": "http://79.174.80.94:8015/photos/339bdba66aa76cfc2f337f7da2f3006458171b8f.jpeg"
    },
    {
        "name": "Яблоко",
        "normal": "http://79.174.80.94:8015/photos/fbb41607078960adbdc131f4b72a6b64f79eca25.jpeg",
        "not_normal": "http://79.174.80.94:8015/photos/b94524f349bc4134ce6312b64ac4f05dca0e25d2.jpeg"
    },
    {
        "name": "Яблоко айдаред",
        "normal": "http://79.174.80.94:8015/photos/a758d132b8c3fa7a39c48d262cfafd91696fb950.jpeg",
        "not_normal": "http://79.174.80.94:8015/photos/61a244e021dbf442c3cf7e01f0537c60236953e5.jpeg"
    },
    {
        "name": "Яйцо",
        "normal": "http://79.174.80.94:8015/photos/cb6ba76bd9f9864c1d0e0c965bd2e6a9ddb4ff7b.jpeg",
        "not_normal": "http://79.174.80.94:8015/photos/75792d880ce0ce0e4229f1bffe2d5ea3e59df90c.jpeg"
    }
]


def get_random_name():
    return random.choice(["Михаил", "Анатолий", "Виталий", "Дмитрий"])


def get_random_surname():
    return random.choice(["Хохоев", "Самсунгов", "Енотин", "Болотов"])


def get_random_patronymic():
    return random.choice(["Зайкович", "Бикович", "Кайфович", "Геннадиевич"])


def get_random_email():
    return "+7" + str(random.randint(1111111111, 8888888888))


def get_random_avatar():
    return random.choice(["http://79.174.80.94:8015/photos/4cd5e533b8afe2124afb03c8eb87c45e38337875.jpeg",
                          "http://79.174.80.94:8015/photos/1d25e01dd438cff11891ddcd743780619e3a056a.jpeg",
                          "http://79.174.80.94:8015/photos/e3eb5f1f6294064bf25d1881c73fba0a0c47d126.jpeg"])


def send_registration_request(name, surname, patronymic, email, avatar):
    url = 'http://79.174.80.94:8000/auth/registration'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        'first_name': name,
        'last_name': surname,
        'patronymic': patronymic,
        'email': email,
        'role': 'client',
        'photo': avatar
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        json_response = response.json()
        print(json_response)
        return json_response
    except requests.exceptions.RequestException as e:
        print('Ошибка при выполнении запроса:', e)
        return None


def write_to_file(text, filename):
    with open(filename, 'a') as file:
        file.write(text + '\n')


def read_file_lines(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        lines = [line.strip() for line in lines]
        return lines


def confirm_registration(email):
    url = 'http://79.174.80.94:8000/auth/registration_confirm'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        'email': email,
        'role': 'client',
        'code': 111111
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        json_response = response.json()
        access_token = json_response['access_token']
        write_to_file(access_token, "tokens.txt")
        return json_response
    except requests.exceptions.RequestException as e:
        print('Ошибка при выполнении запроса:', e)
        return None


def create_users(count: int):
    for i in range(count):
        name = get_random_name()
        surname = get_random_surname()
        patronymic = get_random_patronymic()
        email = get_random_email()
        avatar = get_random_avatar()
        print(send_registration_request(name, surname, patronymic, email, avatar))

        print(confirm_registration(email))


create_users(0)

print(read_file_lines("tokens.txt"))


def get_random_product_name():
    return random.choice(['Банан', 'Колбаса', 'Мука', 'Огурец', 'Сахар', 'Яблоко', 'Яблоко айдаред', 'Яйцо'])


def get_normal_photo_by_product_name(product_name: str):
    for photo in photos:
        if photo['name'] == product_name:
            return photo['normal']
    return None


def get_not_normal_photo_by_product_name(product_name: str):
    for photo in photos:
        if photo['name'] == product_name:
            return photo['not_normal']
    return None


def get_random_coordinates():
    return random.choice(
        [
            [37.789115, 47.979406],  #
            [38.3989883, 48.3425333], #
            [38.090086, 47.112760], #
            [48.010139, 38.260874][::-1],#
            [48.050010, 38.484141][::-1]#
        ]
    )


def send_add_application_request(name_product, coordinates, shop_id, token):
    url = 'http://0.0.0.0:8011/applications/add'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'name_product': name_product,
        'photo': get_not_normal_photo_by_product_name(name_product),
        'coordinates': coordinates,
        'shop_id': shop_id
    }

    response = requests.post(url, headers=headers, json=data)
    json_response = response.json() if response.ok else response.json()
    return json_response


def create_applications(count: int):
    for i in range(count):
        try:
            name_product = get_random_product_name()
            coordinates = get_random_coordinates()
            shop_id = 0
            token = random.choice(read_file_lines("tokens.txt"))
            print(send_add_application_request(name_product, coordinates, shop_id, token))
        except:
            print("error: ", coordinates)


create_applications(25)
