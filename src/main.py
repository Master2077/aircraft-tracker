from src.data_to_json import SaveDataPlanesJSON
from src.top import TopPlanes
from src.plane_info import InformationAboutPlanes   # или как у тебя называется модуль
from src.plane import Plane

class Interface:
    """
    Интерфейс для взаимодействия пользователя с программой.
    """

    def __init__(self):
        self.info_service = InformationAboutPlanes()  # получение данных
        self.storage = SaveDataPlanesJSON()           # работа с JSON
        self.top_service = TopPlanes()                # топы

    def main_menu(self) -> None:
        country = input("Введите название страны: ").strip().capitalize()

        # Получаем список объектов Plane
        planes = self.info_service.get_information(country)

        if not planes:
            print("Самолеты не найдены.")
            return

        # Сохраняем в JSON
        self.storage.save_data(planes)

        print(f"\nНайдено самолетов: {len(planes)}")

        choice = input(
            "\nВыберите действие:\n"
            "1) Получить топ N самолетов по высоте полёта\n"
            "2) Получить топ N самолетов по скорости\n"
            "3) Получить самолеты по стране регистрации\n"
            "4) Сравнить два самолета по скорости\n"
            "5) Сравнить два самолета по высоте\n"
        ).strip()

        if choice == "1":
            n = int(input("Укажите топ скольких самолётов вы хотите получить: "))
            print(self.top_service.top_altitude(planes, n))

        elif choice == "2":
            n = int(input("Укажите топ скольких самолётов вы хотите получить: "))
            print(self.top_service.top_velocity(planes, n))

        elif choice == "3":
            country_reg = input(
                "Укажите страну регистрации (на английском языке): "
            ).strip().capitalize()
            filtered = [p for p in planes if p.country == country_reg]
            print(self.top_service._to_pretty_json(filtered))

        elif choice == "4":
            self._compare_velocity(planes)

        elif choice == "5":
            self._compare_altitude(planes)

        else:
            print("Нет такого действия")

    def _compare_velocity(self, planes: list) -> None:
        """Сравнение двух самолетов по скорости"""
        print("\nСписок самолётов:")
        for i, plane in enumerate(planes):
            print(f"{i}) {plane.callsign} ({plane.country}) — {plane.velocity} м/с")

        try:
            idx1 = int(input("\nВведите индекс первого самолета: "))
            idx2 = int(input("Введите индекс второго самолета: "))
            print(planes[idx1].is_faster_than(planes[idx2]))
        except (ValueError, IndexError) as e:
            print(f"Ошибка: {e}")

    def _compare_altitude(self, planes: list) -> None:
        """Сравнение двух самолётов по высоте"""
        print("\nСписок самолетов:")
        for i, plane in enumerate(planes):
            print(f"{i}) {plane.callsign} ({plane.country}) — {plane.geo_altitude} м")

        try:
            idx1 = int(input("\nВведите индекс первого самолета: "))
            idx2 = int(input("Введите индекс второго самолета: "))
            print(planes[idx1].is_higher_than(planes[idx2]))
        except (ValueError, IndexError) as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    app = Interface()
    app.main_menu()