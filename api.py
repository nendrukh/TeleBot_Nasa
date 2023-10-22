import requests
from config import API_KEY


class ParamMars:
    camera = None
    earth_date = None


def api_request_img_day(date) -> str:
    response = requests.get("https://api.nasa.gov/planetary/apod", params={
        "date": date,
        "api_key": API_KEY
    })
    response_json = response.json()

    if response.status_code == 400:
        return "За эту дату фоток нет, введи другую.\n" \
               "Можно вводить дату от 16.01.1995 до сегодняшнего дня.\n" \
               "За сегодняшний день фоток может не быть (у NASA).\n" \
               "\nПосмотреть все команды можно через команду /start"
    return f"Картинка: {response_json['hdurl']}\n" \
           f"С описанием: {response_json['title']}\n"


def api_request_mars(earth_date, camera: str) -> list:
    if camera == "Фронт":
        camera = "FHAZ"
    elif camera == "Задняя":
        camera = "RHAZ"
    else:
        camera = "MAST"
    response = requests.get("https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos", params={
        "earth_date": earth_date,
        "camera": camera,
        "api_key": API_KEY
    })
    response_json = response.json()

    if len(response_json["photos"]) == 0:
        return list(["Фоток нет. Попробуй другую дату.\nПосмотреть все команды можно через команду /start"])

    count = 0
    result = list()
    for i_object in response_json['photos']:
        if count == 5:
            break
        result.append(i_object['img_src'])
        count += 1

    return result
