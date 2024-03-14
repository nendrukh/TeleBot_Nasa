import requests
import datetime
from requests import Response
from config import API_KEY


class ParamMars:
    camera = None
    earth_date = None


def api_request_img_day(date: datetime.date) -> str:
    """
    We use NASA's API to get picture of the day.
    In response we get json from which we get an image using the 'hdurl' or 'url' keys
    :param date: date for which the picture is needed. Example 2024-01-01
    :return: image and description (str)
    """
    response: Response = requests.get("https://api.nasa.gov/planetary/apod", params={
        "date": date,
        "api_key": API_KEY
    })
    response_json = response.json()

    if response.status_code == 400:
        now_date: datetime.date = datetime.datetime.now()
        return f"""
За эту дату фоток нет, введи другую.
Можно вводить дату от 16.01.1995 до {now_date.strftime("%d.%m.%Y")}.
За сегодняшний день фоток ещё может не быть.
Посмотреть все команды можно через команду /start
"""
    try:
        image: str = response_json["hdurl"]
    except KeyError:
        image: str = response_json["url"]
    return f"""
Картинка: {image}
С описанием: {response_json["title"]}
"""


def api_request_mars(earth_date: datetime.date, camera: str) -> list:
    """
    We use NASA's API to get photos from Mars.
    In response, we receive json, from which we obtain an array with links to images using the “photos” key.
    We take links to photos using the "img src" key in the array object
    :param earth_date: date for which photos are needed. Example 2024-01-01
    :param camera: camera type
    :return: list with links to photos or text in a list with no photos
    """
    if camera == "Фронт" or camera == "фронт":
        camera: str = "FHAZ"
    elif camera == "Задняя" or camera == "задняя":
        camera: str = "RHAZ"
    else:
        camera: str = "MAST"
    response = requests.get("https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos", params={
        "earth_date": earth_date,
        "camera": camera,
        "api_key": API_KEY
    })
    response_json: dict = response.json()

    if len(response_json["photos"]) == 0:
        return list(["Фоток нет. Попробуй другую дату."])

    count: int = 0
    result = list()
    for i_object in response_json['photos']:
        if count == 5:
            break
        result.append(i_object['img_src'])
        count += 1

    return result
