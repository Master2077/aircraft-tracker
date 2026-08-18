import json
from abc import ABC, abstractmethod
from pathlib import Path

from src.plane_info import InformationAboutPlanes

FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "info.json"


class SaveDataPlanesABC(ABC):
    """
    Абстрактный класс для сохранения, загрузки
    и удаления данных о самолетах.
    """

    @abstractmethod
    def save_data(self) -> None:
        pass

    @abstractmethod
    def load_data(self, criteria: dict):
        pass

    @abstractmethod
    def del_data(self, criteria: dict):
        pass


class SaveDataPlanesJSON(SaveDataPlanesABC, InformationAboutPlanes):
    """
    Реализация хранения информации о самолетах в JSON-файле.

    Класс получает информацию о самолетах через API
    и позволяет сохранять, загружать и удалять данные в JSON-файле.
    """

    def __init__(self):
        super().__init__()

    def save_data(self) -> None:
        """
        Сохраняет текущую информацию о самолетах в JSON-файл.
        """
        data = self.information
        try:
            with open(FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise f"Ошибка записи в файл: {e}"

    def load_data(self, criteria: dict):
        """
        Загружает данные из JSON-файла и фильтрует их.
        """
        if not FILE_PATH.exists() or FILE_PATH.stat().st_size == 0:
            return "Файла не существует или же он пуст"

        try:
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Ошибка. Файл чтения поврежден: {e}")
            return []

        if not criteria:
            return data
        if not isinstance(data, list):
            return []

        filtered = []
        for item in data:
            if any(item.get(key) == value for key, value in criteria.items()):
                filtered.append(item)

        return json.dumps(filtered, ensure_ascii=False, indent=2)

    def del_data(self, criteria: dict):
        """
        Удаляет записи из JSON-файла по заданным критериям
        """
        if not FILE_PATH.exists() or FILE_PATH.stat().st_size == 0:
            return "Файла не существует или же он пуст"

        try:
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Ошибка. Файл чтения поврежден: {e}")
            return []

        if not criteria:
            return data
        if not isinstance(data, list):
            return []

        to_delete = []
        remain = []
        for item in data:
            if any(item.get(key) == value for key, value in criteria.items()):
                to_delete.append(item)
            else:
                remain.append(item)

        try:
            with open(FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(remain, f, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Ошибка записи в файл: {e}"

        return f"Удалено {len(to_delete)} данных"


if __name__ == "__main__":
    r = SaveDataPlanesJSON()
    r.get_information("Russia")
    r.save_data()
    criterion = {"Позывной рейса": "TVF94PD"}
    result_del = r.del_data(criterion)
    print(result_del)

    criteria = {"Страна регистрации": "Germany", "Позывной рейса": "TVF94PD"}
    result_load = r.load_data(criteria)
    print(result_load)
