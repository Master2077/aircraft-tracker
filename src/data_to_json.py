import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from src.plane import Plane
from src.plane_info import InformationAboutPlanes


FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "info.json"


class SaveDataPlanesABC(ABC):
    """
    Абстрактный класс для сохранения, загрузки
    и удаления данных о самолётах.
    """

    @abstractmethod
    def save_data(self, planes: List[Plane]) -> None:
        pass

    @abstractmethod
    def load_data(self, criteria: dict = None) -> List[Plane]:
        pass

    @abstractmethod
    def del_data(self, criteria: dict) -> str:
        pass


class SaveDataPlanesJSON(SaveDataPlanesABC):
    """
    Реализация хранения информации о самолётах в JSON-файле.
    Работает со списком объектов Plane.
    """

    def save_data(self, planes: List[Plane]) -> None:
        """
        Сохраняет список самолётов в JSON-файл.
        """
        data = []
        for plane in planes:
            data.append({
                "Страна регистрации": plane.country,
                "Позывной рейса": plane.callsign,
                "Горизонтальная скорость": plane.velocity,
                "Вертикальная скорость": plane.vertical_velocity,
                "Геометрическая высота": plane.geo_altitude,
                "Барометрическая высота": plane.baro_altitude,
                "Долгота": plane.longitude,
                "Широта": plane.latitude
            })

        try:
            FILE_PATH.parent.mkdir(parents=True, exist_ok=True)  # создаём папку data, если её нет
            with open(FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Ошибка записи в файл: {e}")

    def load_data(self, criteria: dict = None) -> List[Plane]:
        """
        Загружает данные из JSON-файла и возвращает список объектов Plane.
        Можно передать criteria для фильтрации.
        """
        if not FILE_PATH.exists() or FILE_PATH.stat().st_size == 0:
            print("Файла не существует или он пуст")
            return []

        try:
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Ошибка чтения файла: {e}")
            return []

        if not isinstance(data, list):
            return []

        planes = []
        for item in data:
            try:
                plane = Plane(
                    country=item.get("Страна регистрации"),
                    callsign=item.get("Позывной рейса"),
                    velocity=item.get("Горизонтальная скорость"),
                    vertical_velocity=item.get("Вертикальная скорость"),
                    geo_altitude=item.get("Геометрическая высота"),
                    baro_altitude=item.get("Барометрическая высота"),
                    longitude=item.get('Долгота'),
                    latitude=item.get('Широта')
                )
                planes.append(plane)
            except (TypeError, ValueError) as e:
                print(f"Пропущен некорректный самолет: {e}")
                continue

        # Фильтрация по критериям (если переданы)
        if criteria:
            filtered = []
            for plane in planes:
                match = True
                for key, value in criteria.items():
                    plane_value = getattr(plane, self._key_to_attr(key), None)
                    if plane_value != value:
                        match = False
                        break
                if match:
                    filtered.append(plane)
            return filtered

        return planes

    def del_data(self, criteria: dict) -> str:
        """
        Удаляет записи из JSON-файла по заданным критериям.
        """
        if not FILE_PATH.exists() or FILE_PATH.stat().st_size == 0:
            return "Файла не существует или он пуст"

        planes = self.load_data()  # загружаем все

        if not criteria:
            return "Критерии удаления не заданы"

        remain = []
        deleted_count = 0

        for plane in planes:
            match = True
            for key, value in criteria.items():
                plane_value = getattr(plane, self._key_to_attr(key), None)
                if plane_value != value:
                    match = False
                    break
            if match:
                deleted_count += 1
            else:
                remain.append(plane)

        # Сохраняем оставшиеся
        self.save_data(remain)

        return f"Удалено {deleted_count} записей"

    @staticmethod
    def _key_to_attr(key: str) -> str:
        """Преобразует ключ из JSON в имя атрибута класса Plane"""
        mapping = {
            "Страна регистрации": "country",
            "Позывной рейса": "callsign",
            "Горизонтальная скорость": "velocity",
            "Вертикальная скорость": "vertical_velocity",
            "Геометрическая высота": "geo_altitude",
            "Барометрическая высота": "baro_altitude",
            "Долгота": "longitude",
            "Широта": "latitude",
        }
        return mapping.get(key, key)


if __name__ == "__main__":
    from src.plane import Plane

    storage = SaveDataPlanesJSON()

    test_planes = [
        Plane("Germany",
              "DLH4A",
              245.6,
              11200.0,
              122,
              244,
              2 ,
              4),

        Plane("France",
              "AFR123",
              260.3,
              10850.5,
              333,
              23,
              232.32,
              233),

        Plane("Russia",
              "AFL901",
              230.0,
              11500.0,
              333,
              23,
              232.32,
              233
              ),
    ]
    e = InformationAboutPlanes()
    #Сохраняем самолёты
    storage.save_data(e.get_information('Russia'))

    print("\nСписок всех самолетов:")
    loaded = storage.load_data()
    for p in loaded:
        print(p)

    print("\nФильтр по стране:")
    filtered = storage.load_data({"Страна регистрации": "France"})
    for p in filtered:
        print(p)
