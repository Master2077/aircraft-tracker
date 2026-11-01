from src.api import APIGetAeroplanes
from src.plane import Plane

class InformationAboutPlanes(APIGetAeroplanes):
    """
    Класс для получения и анализа информации о самолётах.

    Наследуется от APIGetAeroplanes, который отвечает за получение
    исходных данных из OpenSky Network.
    """

    def __init__(self) -> None:
        self.information = []
        self.country = None
        self.aeroplanes_count = None
        super().__init__()

    def get_information(self, country: str) -> list:
        """
        Получает и обрабатывает информацию о самолётах над страной.
        Возвращает список объектов Plane.
        """
        self.get_aeroplanes(country)

        states = self.aeroplanes.get("states", []) if self.aeroplanes else []
        planes = []

        for plane_data in states:
            # plane_data — это список из OpenSky
            callsign = plane_data[1]
            callsign = callsign.strip() if isinstance(callsign, str) else callsign

            try:
                plane = Plane(
                    country=plane_data[2],
                    callsign=callsign,
                    velocity=plane_data[9],  # Горизонтальная скорость
                    vertical_velocity=plane_data[11],  # Вертикальная скорость
                    geo_altitude=plane_data[13],
                    baro_altitude=plane_data[7],
                    longitude=plane_data[5],
                    latitude=plane_data[6],
                )
                planes.append(plane)
            except (TypeError, ValueError, IndexError) as e:
                # Пропускаем битые данные
                continue

        self.information = planes
        self.country = country
        self.aeroplanes_count = len(planes)
        return planes


if __name__ == "__main__":
    e = InformationAboutPlanes()
    print(e.get_information("Китай"))
    print()
    print(e.information[1])
    print(e.country)
    #print(len(e.get_information("Russia")))
    print()
    print(e.aeroplanes_count)

