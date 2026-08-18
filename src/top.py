import json
from pathlib import Path

FILE_PATH = Path(__file__).resolve().parent / ".." / "data" / "info.json"


class TopPlanes:
    """
    Класс для получения рейтинга самолётов.

    Данные читаются из JSON-файла info.json.
    Класс позволяет вывести самолеты с наибольшей
    горизонтальной скоростью или высотой.
    """

    def _load_data(self):
        """
        Загружает данные о самолётах из JSON-файла.
        """
        if not FILE_PATH.exists() or FILE_PATH.stat().st_size == 0:
            raise "Файла не существует или же он пуст"

        try:
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Ошибка. Файл поврежден: {e}")
            return []
        except Exception as e:
            print(f"Ошибка чтения файла: {e}")
            return []

        # data должен быть списком словарей
        if not isinstance(data, list):
            return []

        return data

    def top_velocity(self, n: int) -> str:
        """
        Вохвращает топ N (N - задана пользователем) самолетов по скорости.
        """
        data = self._load_data()
        key = "Горизонтальная скорость"
        top = []

        if n < 0:
            raise ValueError("Количество самолётов не может быть отрицательным")

        try:
            for item in data:
                velocity = item.get(key)
                if velocity is not None:
                    top.append(item)
            top.sort(key=lambda item: item.get(key), reverse=True)
            top = top[:n]
            return json.dumps(top, ensure_ascii=False, indent=2)
        except TypeError as t:
            raise f"Для выдачи топ самолетов нужно указать число. Ошибка: {t}"

    def top_altitude(self, n: int) -> str:
        """
        Вохвращает топ N (N - задана пользователем) самолетов по высоте.
        """
        data = self._load_data()
        key = "Геометрическая высота"
        top = []

        if n < 0:
            raise ValueError("Количество самолётов не может быть отрицательным")
        try:
            for item in data:
                velocity = item.get(key)
                if velocity is not None:
                    top.append(item)
            top.sort(key=lambda item: item.get(key), reverse=True)
            top = top[:n]
            return json.dumps(top, ensure_ascii=False, indent=2)
        except TypeError as t:
            raise f"Для выдачи топ самолетов нужно указать число. Ошибка: {t}"


if __name__ == "__main__":
    t = TopPlanes()
    print(t.top_altitude(5))
