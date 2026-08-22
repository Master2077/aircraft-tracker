class Plane:
    """
    Класс, представляющий один самолет.
    Содержит атрибуты и методы сравнения + валидацию данных.
    """

    def __init__(self, country, callsign, velocity, geo_altitude, vertical_velocity, baro_altitude, longitude, latitude):
        self.country = self._validate_str(country, "Страна регистрации")
        self.callsign = self._validate_str(callsign, "Позывной")
        self.velocity = self._validate_number(velocity, "Горизонтальная скорость")
        self.vertical_velocity = self._validate_number(vertical_velocity, "Вертикальная скорость")
        self.geo_altitude = self._validate_number(geo_altitude, "Геометрическая высота")
        self.baro_altitude = self._validate_number(baro_altitude, "Барометрическая высота")
        self.longitude = self._validate_number(longitude, "Долгота")
        self.latitude = self._validate_number(latitude, "Широта")

    @staticmethod
    def _validate_str(value, name: str) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise TypeError(f"{name} должна быть строкой или None")
        return value.strip()

    @staticmethod
    def _validate_number(value, name: str) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{name} должна быть числом или None")

    def is_faster_than(self, other) -> str:
        """Сравнивает горизонтальную скорость двух самолетов."""
        if not isinstance(other, Plane):
            raise TypeError("Сравнивать можно только с другим объектом Plane")

        if self.velocity is None:
            return f"У самолета {self.callsign} отсутствуют данные о скорости"
        if other.velocity is None:
            return f"У самолета {other.callsign} отсутствуют данные о скорости"

        if self.velocity > other.velocity:
            diff = round(self.velocity - other.velocity, 3)
            return (
                f"Самолет {self.callsign} быстрее самолета {other.callsign} "
                f"на {diff} м/с"
            )
        elif other.velocity > self.velocity:
            diff = round(other.velocity - self.velocity, 3)
            return (
                f"Самолет {other.callsign} быстрее самолета {self.callsign} "
                f"на {diff} м/с"
            )
        return "Скорости равны"

    def is_higher_than(self, other) -> str:
        """Сравнивает геометрическую высоту двух самолетов."""
        if not isinstance(other, Plane):
            raise TypeError("Сравнивать можно только с другим объектом Plane")

        if self.geo_altitude is None:
            return f"У самолета {self.callsign} отсутствуют данные о высоте"
        if other.geo_altitude is None:
            return f"У самолета {other.callsign} отсутствуют данные о высоте"

        if self.geo_altitude > other.geo_altitude:
            diff = round(self.geo_altitude - other.geo_altitude, 3)
            return (
                f"Самолет {self.callsign} летит выше самолета {other.callsign} "
                f"на {diff} м"
            )
        elif other.geo_altitude > self.geo_altitude:
            diff = round(other.geo_altitude - self.geo_altitude, 3)
            return (
                f"Самолет {other.callsign} летит выше самолета {self.callsign} "
                f"на {diff} м"
            )
        return "Высоты равны"

    def __repr__(self) -> str:
        return (
            f"Plane(callsign={self.callsign!r}, country={self.country!r}, "
            f"velocity={self.velocity}, vertical_velocity={self.vertical_velocity}, "
            f"geo_altitude={self.geo_altitude}, baro_altitude={self.baro_altitude},"
            f"longitude={self.longitude}, latitude={self.latitude})"
        )


if __name__ == "__main__":
    plane1 = Plane(
        country="Germany",
        callsign="DLH4A",
        velocity=245.6,
        vertical_velocity=93.1,
        geo_altitude=43.5,
        baro_altitude=32.1,
        longitude=87.77,
        latitude=12.12

    )

    plane2 = Plane(
        country="France",
        callsign="AFR123",
        velocity=260.3,
        vertical_velocity=123.1,
        geo_altitude=10850.5,
        baro_altitude=72.1,
        longitude=141.21,
        latitude=42.12

    )

    plane3 = Plane(
        country="Russia",
        callsign="AFL901",
        velocity=None,
        vertical_velocity=421.1,
        geo_altitude=170.5,
        baro_altitude=53.1,
        longitude=112.21,
        latitude=52.12
    )

    print("Созданные самолеты:")
    print(plane1)
    print(plane2)
    print(plane3)
    print()

    # Проверка сравнения скорости
    print("Сравнение скорости:")
    print(plane1.is_faster_than(plane2))
    print(plane2.is_faster_than(plane1))
    print(plane1.is_faster_than(plane3))
    print()

    # Проверка сравнения высоты
    print("Сравнение высоты:")
    print(plane1.is_higher_than(plane2))
    print(plane3.is_higher_than(plane1))
    print()

