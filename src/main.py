from src.data_to_json import SaveDataPlanesJSON
from src.top import TopPlanes


class Interface(SaveDataPlanesJSON, TopPlanes):
    """
    Интерфейс для взаимодействия пользователя с программой.
    """

    def __init__(self):
        super().__init__()

    def main_menu(self) -> None:
        country = input("Введите название страны: ").capitalize()
        self.get_information(country)  # получаем информацию о самолетах над выбранной страной
        self.save_data()  # сохраняем информацию о самолетах в JSON-файл

        # Показываем пользователю список доступных действий
        choice = (
            input(
                "Выберити следующее действие:\n1) Получить топ N самолетов по высоте полета\n"
                "2) Получить топ N самолетов по их скорости\n"
                "3) Получить самолеты по стране их регистрации\n"
            )
            .strip()
            .lower()
        )

        # Выводит топ самолетов по высоте
        if choice == "1" or choice == "Получить топ N самолетов по высоте полета".lower():
            top = int(input("Укажите топ скольких самолетов вы хотите получить: "))
            print(self.top_altitude(top))

        # Выводит топ самолетов по скорости
        elif choice == "2" or choice == "Получить топ N самолетов по их скорости".lower():
            top = int(input("Укажите топ скольких самолетов вы хотите получить: "))
            print(self.top_velocity(top))

        # Выводит самолеты по стране регистрации
        elif choice == "3" or choice == "Получить самолеты по стране их регистрации".lower():
            country_of_registration = input(
                "Укажите страну регистрации самолетов по которым "
                "вы хотите получить информацию (на английском языке): "
            )
            criterion = {"Страна регистрации": None}
            criterion["Страна регистрации"] = country_of_registration.capitalize()
            print(self.load_data(criterion))


if __name__ == "__main__":
    m = Interface()
    m.main_menu()
