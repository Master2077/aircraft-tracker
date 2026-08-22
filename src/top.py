import json
from typing import List

from src.plane import Plane


class TopPlanes:
    """
    Класс для получения топа самолётов по скорости и высоте.
    Работает со списком объектов Plane.
    """

    def top_velocity(self, planes: List[Plane], n: int) -> str:
        """
        Возвращает топ-N самолётов по горизонтальной скорости.
        """
        if not isinstance(n, int):
            raise TypeError("Количество самолетов должно быть целым числом")
        if n < 0:
            raise ValueError("Количество самолетов не может быть отрицательным")

        # Берём только те самолёты, у которых есть данные о скорости
        valid_planes = [p for p in planes if p.velocity is not None]

        # Сортируем по убыванию скорости
        sorted_planes = sorted(
            valid_planes,
            key=lambda plane: plane.velocity,
            reverse=True
        )

        top = sorted_planes[:n]
        return self._to_pretty_json(top)

    def top_altitude(self, planes: List[Plane], n: int) -> str:
        """
        Возвращает топ-N самолетов по геометрической высоте.
        """
        if not isinstance(n, int):
            raise TypeError("Количество самолетов должно быть целым числом")
        if n < 0:
            raise ValueError("Количество самолетов не может быть отрицательным")

        # Берем только те самолеты, у которых есть данные о высоте
        valid_planes = [p for p in planes if p.geo_altitude is not None]

        sorted_planes = sorted(
            valid_planes,
            key=lambda plane: plane.geo_altitude,
            reverse=True
        )

        top = sorted_planes[:n]
        return self._to_pretty_json(top)

    @staticmethod
    def _to_pretty_json(planes: List[Plane]) -> str:
        """Преобразует список самолетов в JSON для вывода."""
        data = []
        for plane in planes:
            data.append({
                "Страна регистрации": plane.country,
                "Позывной рейса": plane.callsign,
                "Горизонтальная скорость": plane.velocity,
                "Геометрическая высота": plane.geo_altitude,
                "Барометрическая высота": plane.baro_altitude,
                "Долгота": plane.longitude,
                "Широта": plane.latitude
            })
        return json.dumps(data, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    planes = [
        Plane("Germany", "DLH4A", 245.6, 11200.0),
        Plane("France", "AFR123", 260.3, 10850.5),
        Plane("Russia", "AFL901", 230.0, 11500.0),
        Plane("Spain", "IBE45C", 255.1, 10900.0),
        Plane("Italy", "AZA789", None, 10500.0),
    ]

    top = TopPlanes()

    print("Топ-3 по скорости:")
    print(top.top_velocity(planes, 3))
    print()

    print("Топ-3 по высоте:")
    print(top.top_altitude(planes, 3))