import pytest

from src.plane_info import InformationAboutPlanes


def create_plane(
    callsign=" SU123 ",
    country="Russia",
    velocity=250.5,
    vertical_velocity=-1.2,
    barometric_altitude=9_500,
    geometric_altitude=10_000,
    longitude=37.6,
    latitude=55.7,
):
    """
    Создаёт состояние самолёта в формате OpenSky Network.
    """
    plane = [None] * 14

    plane[1] = callsign
    plane[2] = country
    plane[5] = longitude
    plane[6] = latitude
    plane[7] = barometric_altitude
    plane[9] = velocity
    plane[11] = vertical_velocity
    plane[13] = geometric_altitude

    return plane


@pytest.fixture
def service():
    """
    Создаёт объект без вызова __init__ родительского класса.
    Это предотвращает настоящий запрос к API.
    """
    obj = InformationAboutPlanes.__new__(InformationAboutPlanes)
    obj.information = []
    return obj


@pytest.fixture
def filled_service(service):
    service.information = [
        {
            "Страна регистрации": "Russia",
            "Позывной рейса": "SU123",
            "Горизонтальная скорость": 250.5,
            "Вертикальная скорость": -1.2,
            "Барометрическая высота": 9500,
            "Геометрическая высота": 10000,
            "Долгота": 37.6,
            "Широта": 55.7,
        },
        {
            "Страна регистрации": "France",
            "Позывной рейса": "AF456",
            "Горизонтальная скорость": 300,
            "Вертикальная скорость": 0.5,
            "Барометрическая высота": 11000,
            "Геометрическая высота": 12000,
            "Долгота": 2.3,
            "Широта": 48.8,
        },
    ]

    return service


def test_get_information(service, monkeypatch):
    states = [
        create_plane(
            callsign=" SU123 ",
            country="Russia",
            velocity=250.5,
            vertical_velocity=-1.2,
            barometric_altitude=9500,
            geometric_altitude=10000,
            longitude=37.6,
            latitude=55.7,
        ),
        create_plane(
            callsign=None,
            country="France",
            velocity=300,
            vertical_velocity=0.5,
            barometric_altitude=11000,
            geometric_altitude=12000,
            longitude=2.3,
            latitude=48.8,
        ),
    ]

    def fake_get_aeroplanes(country):
        assert country == "Russia"
        service.aeroplanes = {"states": states}

    monkeypatch.setattr(service, "get_aeroplanes", fake_get_aeroplanes)

    result = service.get_information("Russia")

    assert result == [
        {
            "Страна регистрации": "Russia",
            "Позывной рейса": "SU123",
            "Горизонтальная скорость": 250.5,
            "Вертикальная скорость": -1.2,
            "Барометрическая высота": 9500,
            "Геометрическая высота": 10000,
            "Долгота": 37.6,
            "Широта": 55.7,
        },
        {
            "Страна регистрации": "France",
            "Позывной рейса": None,
            "Горизонтальная скорость": 300,
            "Вертикальная скорость": 0.5,
            "Барометрическая высота": 11000,
            "Геометрическая высота": 12000,
            "Долгота": 2.3,
            "Широта": 48.8,
        },
    ]


def test_get_information_without_states(service, monkeypatch):
    monkeypatch.setattr(
        service,
        "get_aeroplanes",
        lambda country: setattr(service, "aeroplanes", {}),
    )

    result = service.get_information("Russia")

    assert result == []


def test_get_information_calls_api_with_country(service, monkeypatch):
    countries = []

    def fake_get_aeroplanes(country):
        countries.append(country)
        service.aeroplanes = {"states": []}

    monkeypatch.setattr(service, "get_aeroplanes", fake_get_aeroplanes)

    service.get_information("Germany")

    assert countries == ["Germany"]


def test_velocity_first_plane_is_faster(filled_service):
    result = filled_service.velocity(0, 1)

    assert result == (
        "На данный момент скорость рейса AF456"
        "(1) больше чем скорость рейса SU123(0)"
        " на 49.5 м/с"
    )


def test_velocity_second_plane_is_faster(filled_service):
    result = filled_service.velocity(1, 0)

    assert result == (
        "На данный момент скорость рейса AF456"
        "(1) больше чем скорость рейса SU123(0)"
        "на 49.5 м/с"
    )


def test_velocity_equal(filled_service):
    filled_service.information[1][
        "Горизонтальная скорость"
    ] = 250.5

    result = filled_service.velocity(0, 1)

    assert result == "Скорости равны"


def test_velocity_returns_error_when_first_value_is_none(
    filled_service,
):
    filled_service.information[0][
        "Горизонтальная скорость"
    ] = None

    result = filled_service.velocity(0, 1)

    assert result == (
        "Невозможно сравнить скорость: "
        "у рейса None отсутствуют данные о скорости"
    )


def test_velocity_returns_error_when_second_value_is_none(
    filled_service,
):
    filled_service.information[1][
        "Горизонтальная скорость"
    ] = None

    result = filled_service.velocity(0, 1)

    assert result == (
        "Невозможно сравнить скорость: "
        "у рейса None отсутствуют данные о скорости"
    )


def test_velocity_returns_error_for_non_numeric_values(
    filled_service,
):
    filled_service.information[0][
        "Горизонтальная скорость"
    ] = "unknown"

    result = filled_service.velocity(0, 1)

    assert result == (
        "Невозможно сравнить скорости: "
        "данные не являются числом"
    )


def test_velocity_returns_error_for_invalid_index(filled_service):
    result = filled_service.velocity(0, 10)

    assert result == (
        "Невозможно сравнить высоты: "
        "индекс рейса вне диапазона"
    )


@pytest.mark.parametrize("invalid_index", ["0", 1.5, None])
def test_velocity_raises_type_error_for_invalid_index(
    filled_service,
    invalid_index,
):
    with pytest.raises(TypeError):
        filled_service.velocity(invalid_index, 1)


def test_altitude_first_plane_is_lower(filled_service):
    result = filled_service.altitude(0, 1)

    assert result == (
        "На данный момент высота рейса AF456"
        "(1) больше чем высота рейса SU123(0)"
        " на 2000.0 м"
    )


def test_altitude_second_plane_is_lower(filled_service):
    result = filled_service.altitude(1, 0)

    assert result == (
        "На данный момент высота рейса AF456"
        "(1) больше чем высота рейса SU123(0)"
        "на 2000.0 м"
    )


def test_altitude_equal(filled_service):
    filled_service.information[1][
        "Геометрическая высота"
    ] = 10000

    result = filled_service.altitude(0, 1)

    assert result == "Высоты равны"


def test_altitude_returns_error_when_first_value_is_none(
    filled_service,
):
    filled_service.information[0][
        "Геометрическая высота"
    ] = None

    result = filled_service.altitude(0, 1)

    assert result == (
        "Невозможно сравнить высоты: "
        "у рейса None отсутсвуют данные о высоте"
    )


def test_altitude_returns_error_when_second_value_is_none(
    filled_service,
):
    filled_service.information[1][
        "Геометрическая высота"
    ] = None

    result = filled_service.altitude(0, 1)

    assert result == (
        "Невозможно сравнить высоты: "
        "у рейса None отсутсвуют данные о высоте"
    )


def test_altitude_returns_error_for_non_numeric_values(
    filled_service,
):
    filled_service.information[0][
        "Геометрическая высота"
    ] = "unknown"

    result = filled_service.altitude(0, 1)

    assert result == (
        "Невозможно сравнить высоты: "
        "данные не являются числом"
    )


def test_altitude_returns_error_for_invalid_index(filled_service):
    result = filled_service.altitude(0, 10)

    assert result == (
        "Невозможно сравнить высоты: "
        "индекс рейса вне диапазона"
    )


@pytest.mark.parametrize("invalid_index", ["0", 1.5, None])
def test_altitude_raises_type_error_for_invalid_index(
    filled_service,
    invalid_index,
):
    with pytest.raises(TypeError):
        filled_service.altitude(invalid_index, 1)


