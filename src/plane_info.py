from src.api import APIGetAeroplanes


class InformationAboutPlanes(APIGetAeroplanes):
    """
    Класс для получения и анализа информации о самолётах.

    Наследуется от APIGetAeroplanes, который отвечает за получение
    исходных данных из OpenSky Network.
    """

    def __init__(self) -> None:
        self.information = []
        super().__init__()

    def get_information(self, country: str) -> list[dict]:
        """
        Получает и обрабатывает информацию о самолётах над страной.
        """
        self.get_aeroplanes(country)  # вызываем API из родителя

        states = self.aeroplanes.get("states", [])

        for i in range(len(states)):
            plane = states[i]

            # На случай если позывной - None
            callsign = plane[1]
            callsign = callsign.strip() if isinstance(callsign, str) else callsign

            self.information.append(
                {
                    "Страна регистрации": plane[2],
                    "Позывной рейса": callsign,
                    "Горизонтальная скорость": plane[9],
                    "Вертикальная скорость": plane[11],
                    "Барометрическая высота": plane[7],
                    "Геометрическая высота": plane[13],
                    "Долгота": plane[5],
                    "Широта": plane[6],
                }
            )

        return self.information

    def velocity(self, plane1: int, plane2: int) -> str:
        """
        Сравнивает горизонтальную скорость двух самолетов.
        """
        if not isinstance(plane1, int):
            raise TypeError(f"Не удалось найти рейс с индексом: {plane1}. Индекс должен быть целым числом")
        if not isinstance(plane2, int):
            raise TypeError(f"Не удалось найти рейс с индексом: {plane2}. Индекс должен быть целым числом")

        try:
            v1 = self.information[plane1]["Горизонтальная скорость"]
            v2 = self.information[plane2]["Горизонтальная скорость"]
        except IndexError:
            return "Невозможно сравнить высоты: индекс рейса вне диапазона"

        if v1 is None:
            return f"Невозможно сравнить скорость: у рейса {v1} отсутствуют данные о скорости"
        if v2 is None:
            return f"Невозможно сравнить скорость: у рейса {v2} отсутствуют данные о скорости"

        try:
            v1 = float(v1)
            v2 = float(v2)
        except (TypeError, ValueError):
            return "Невозможно сравнить скорости: данные не являются числом"

        if v1 > v2:
            return (
                f"На данный момент скорость рейса {self.information[plane1]['Позывной рейса']}"
                f"({plane1}) больше чем скорость рейса {self.information[plane2]['Позывной рейса']}({plane2})"
                f"на {round(v1 - v2, 3)} м/с"
            )
        elif v2 > v1:
            return (
                f"На данный момент скорость рейса {self.information[plane2]['Позывной рейса']}"
                f"({plane2}) больше чем скорость рейса {self.information[plane1]['Позывной рейса']}({plane1})"
                f" на {round(v2 - v1, 3)} м/с"
            )
        else:
            return "Скорости равны"

    def altitude(self, plane1: int, plane2: int) -> str:
        """
        Сравнивает геометрическую высоту двух самолетов.
        """
        if not isinstance(plane1, int):
            raise TypeError(f"Не удалось найти рейс с индексом: {plane1}. Индекс должен быть целым числом")
        if not isinstance(plane2, int):
            raise TypeError(f"Не удалось найти рейс с индексом: {plane2}. Индекс должен быть целым числом")

        try:
            a1 = self.information[plane1]["Геометрическая высота"]
            a2 = self.information[plane2]["Геометрическая высота"]
        except IndexError:
            return "Невозможно сравнить высоты: индекс рейса вне диапазона"

        if a1 is None:
            return f"Невозможно сравнить высоты: у рейса {a1} отсутсвуют данные о высоте"
        if a2 is None:
            return f"Невозможно сравнить высоты: у рейса {a2} отсутсвуют данные о высоте"

        try:
            a1 = float(a1)
            a2 = float(a2)
        except (TypeError, ValueError):
            return "Невозможно сравнить высоты: данные не являются числом"

        if a1 > a2:
            return (
                f"На данный момент высота рейса {self.information[plane1]['Позывной рейса']}"
                f"({plane1}) больше чем высота рейса {self.information[plane2]['Позывной рейса']}({plane2})"
                f"на {round(a1 - a2, 3)} м"
            )
        elif a2 > a1:
            return (
                f"На данный момент высота рейса {self.information[plane2]['Позывной рейса']}"
                f"({plane2}) больше чем высота рейса {self.information[plane1]['Позывной рейса']}({plane1})"
                f" на {round(a2 - a1, 3)} м"
            )
        else:
            return "Высоты равны"


if __name__ == "__main__":
    e = InformationAboutPlanes()
    print(e.get_information("Russia"))
    print()
    print(e.information[1])
    print(e.altitude(1, 2))
