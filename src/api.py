from abc import ABC, abstractmethod

from requests import get


class APIAdapter(ABC):
    """
    Абстрактный базовый класс для работы с внешними API.

    Класс хранит адреса API-сервисов и результат поиска самолётов.
    Конкретная реализация метода get_aeroplanes() должна быть определена
    в дочернем классе.
    """

    def __init__(self) -> None:
        self.openstreetmap_url = (
            "https://nominatim.openstreetmap.org/search"  # для поиска координат страны по ее названию
        )
        self.opensky_url = (
            "https://opensky-network.org/api/states/all?"  # для получения данных о самолетах по координатам.
        )
        self.aeroplanes = None  # результат запроса со списком самолетов

    @abstractmethod
    def get_aeroplanes(self, country: str) -> None:
        pass


class APIGetAeroplanes(APIAdapter):
    """
    Реализация адаптера для получения самолётов через внешние API.

    Сначала класс получает координаты страны через Nominatim OpenStreetMap,
    затем использует эти координаты для фильтрации самолётов в OpenSky Network.
    """

    def get_aeroplanes(self, country: str) -> None:
        """
        Находит самолёты, находящиеся в пределах указанной страны.
        """
        headers_nominatim = {
            "User-Agent": "test-app/1.0",
        }

        # Указываем параметры: в каком формате возвращать данные и максимальную длину списка стран в ответе.
        params_nominatim = {
            "country": country,
            "format": "json",
            "limit": 1,
        }

        response = get(url=self.openstreetmap_url, params=params_nominatim, headers=headers_nominatim)

        data = response.json()

        if not data:
            raise ValueError(f"Не удалось найти координаты для страны: {country}")

        geo_coordinates = data[0].get("boundingbox")

        # Параметры для фильтрации самолетов по их географическим координатам.
        params = {
            "lamin": geo_coordinates[0],
            "lamax": geo_coordinates[1],
            "lomin": geo_coordinates[2],
            "lomax": geo_coordinates[3],
        }

        response = get(url=self.opensky_url, params=params)

        self.aeroplanes = response.json()


if __name__ == "__main__":
    api = APIGetAeroplanes()
    api.get_aeroplanes("Россия")
    print(api.aeroplanes)
