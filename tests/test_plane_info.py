import pytest

from src.plane_info import InformationAboutPlanes
from src.plane import Plane


def create_plane_data(
    callsign=" SU123 ",
    country="Russia",
    velocity=250.5,
    vertical_velocity=-1.2,
    barometric_altitude=9500,
    geometric_altitude=10000,
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
    Создаёт объект без вызова __init__ родительского класса,
    чтобы не делать реальный запрос к API.
    """
    obj = InformationAboutPlanes.__new__(InformationAboutPlanes)
    obj.information = []
    obj.aeroplanes = None
    return obj


def test_get_information_returns_list_of_planes(service, monkeypatch):
    states = [
        create_plane_data(
            callsign=" SU123 ",
            country="Russia",
            velocity=250.5,
            vertical_velocity=-1.2,
            barometric_altitude=9500,
            geometric_altitude=10000,
            longitude=37.6,
            latitude=55.7,
        ),
        create_plane_data(
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

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(p, Plane) for p in result)

    # Первый самолёт
    assert result[0].country == "Russia"
    assert result[0].callsign == "SU123"          # пробелы должны быть убраны
    assert result[0].velocity == 250.5
    assert result[0].vertical_velocity == -1.2
    assert result[0].geo_altitude == 10000
    assert result[0].baro_altitude == 9500
    assert result[0].longitude == 37.6
    assert result[0].latitude == 55.7

    # Второй самолёт (callsign = None)
    assert result[1].country == "France"
    assert result[1].callsign is None
    assert result[1].velocity == 300
    assert result[1].vertical_velocity == 0.5
    assert result[1].geo_altitude == 12000


def test_get_information_without_states(service, monkeypatch):
    def fake_get_aeroplanes(country):
        service.aeroplanes = {}

    monkeypatch.setattr(service, "get_aeroplanes", fake_get_aeroplanes)

    result = service.get_information("Russia")
    assert result == []


def test_get_information_with_none_aeroplanes(service, monkeypatch):
    def fake_get_aeroplanes(country):
        service.aeroplanes = None

    monkeypatch.setattr(service, "get_aeroplanes", fake_get_aeroplanes)

    result = service.get_information("Russia")
    assert result == []


def test_get_information_calls_api_with_country(service, monkeypatch):
    called_countries = []

    def fake_get_aeroplanes(country):
        called_countries.append(country)
        service.aeroplanes = {"states": []}

    monkeypatch.setattr(service, "get_aeroplanes", fake_get_aeroplanes)

    service.get_information("Germany")
    assert called_countries == ["Germany"]


def test_get_information_skips_invalid_data(service, monkeypatch):
    """Битые записи (слишком короткие) должны пропускаться"""
    states = [
        create_plane_data(callsign="OK123"),   # нормальный
        [None] * 5,                            # слишком короткий — должен быть пропущен
        create_plane_data(callsign="OK456"),   # нормальный
    ]

    def fake_get_aeroplanes(country):
        service.aeroplanes = {"states": states}

    monkeypatch.setattr(service, "get_aeroplanes", fake_get_aeroplanes)

    result = service.get_information("Russia")

    assert len(result) == 2
    assert result[0].callsign == "OK123"
    assert result[1].callsign == "OK456"


def test_information_attribute_is_updated(service, monkeypatch):
    """После вызова get_information атрибут self.information тоже должен обновиться"""
    states = [create_plane_data(callsign="TEST1")]

    def fake_get_aeroplanes(country):
        service.aeroplanes = {"states": states}

    monkeypatch.setattr(service, "get_aeroplanes", fake_get_aeroplanes)

    result = service.get_information("Russia")

    assert service.information is result
    assert len(service.information) == 1
    assert service.information[0].callsign == "TEST1"
