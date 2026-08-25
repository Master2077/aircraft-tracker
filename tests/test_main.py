from unittest.mock import Mock, patch, MagicMock
import pytest

from src.plane import Plane


@pytest.fixture
def sample_planes():
    return [
        Plane(
            country="Russia",
            callsign="SU123",
            velocity=250.0,
            vertical_velocity=0.0,
            geo_altitude=10000,
            baro_altitude=9900,
            longitude=37.6,
            latitude=55.7,
        ),
        Plane(
            country="Germany",
            callsign="DLH456",
            velocity=300.0,
            vertical_velocity=-1.0,
            geo_altitude=12000,
            baro_altitude=11900,
            longitude=13.4,
            latitude=52.5,
        ),
    ]


@pytest.fixture
def interface(monkeypatch):
    """
    Создаёт Interface с полностью замоканными зависимостями,
    чтобы не было реальных запросов к API и файловой системе.
    """
    # Чтобы при импорте не запускался main_menu
    monkeypatch.setattr("builtins.input", lambda prompt="": "Russia")

    with patch("src.main.InformationAboutPlanes") as MockInfo, \
         patch("src.main.SaveDataPlanesJSON") as MockStorage, \
         patch("src.main.TopPlanes") as MockTop:

        mock_info = MockInfo.return_value
        mock_storage = MockStorage.return_value
        mock_top = MockTop.return_value

        from src.main import Interface
        app = Interface()

        # Сохраняем моки, чтобы тесты могли их проверять
        app._mock_info = mock_info
        app._mock_storage = mock_storage
        app._mock_top = mock_top

        return app


def test_interface_created(interface):
    assert interface is not None
    assert hasattr(interface, "info_service")
    assert hasattr(interface, "storage")
    assert hasattr(interface, "top_service")


def test_main_menu_top_altitude(interface, sample_planes, capsys):
    interface._mock_info.get_information.return_value = sample_planes
    interface._mock_top.top_altitude.return_value = "Топ по высоте"

    inputs = iter(["Russia", "1", "5"])
    with patch("builtins.input", side_effect=lambda prompt="": next(inputs)):
        interface.main_menu()

    interface._mock_info.get_information.assert_called_once_with("Russia")
    interface._mock_storage.save_data.assert_called_once_with(sample_planes)
    interface._mock_top.top_altitude.assert_called_once_with(sample_planes, 5)

    captured = capsys.readouterr()
    assert "Топ по высоте" in captured.out


def test_main_menu_top_velocity(interface, sample_planes, capsys):
    interface._mock_info.get_information.return_value = sample_planes
    interface._mock_top.top_velocity.return_value = "Топ по скорости"

    inputs = iter(["Germany", "2", "3"])
    with patch("builtins.input", side_effect=lambda prompt="": next(inputs)):
        interface.main_menu()

    interface._mock_info.get_information.assert_called_once_with("Germany")
    interface._mock_storage.save_data.assert_called_once_with(sample_planes)
    interface._mock_top.top_velocity.assert_called_once_with(sample_planes, 3)

    captured = capsys.readouterr()
    assert "Топ по скорости" in captured.out


def test_main_menu_filter_by_country(interface, sample_planes, capsys):
    interface._mock_info.get_information.return_value = sample_planes
    interface._mock_top._to_pretty_json.return_value = '[{"Страна регистрации": "Germany"}]'

    inputs = iter(["Russia", "3", "germany"])
    with patch("builtins.input", side_effect=lambda prompt="": next(inputs)):
        interface.main_menu()

    interface._mock_info.get_information.assert_called_once_with("Russia")
    interface._mock_storage.save_data.assert_called_once_with(sample_planes)

    # Проверяем, что фильтрация произошла
    captured = capsys.readouterr()
    assert "Germany" in captured.out


def test_main_menu_no_planes(interface, capsys):
    interface._mock_info.get_information.return_value = []

    inputs = iter(["Spain"])
    with patch("builtins.input", side_effect=lambda prompt="": next(inputs)):
        interface.main_menu()

    captured = capsys.readouterr()
    assert "Самолеты не найдены" in captured.out
    interface._mock_storage.save_data.assert_not_called()


def test_main_menu_invalid_choice(interface, sample_planes, capsys):
    interface._mock_info.get_information.return_value = sample_planes

    inputs = iter(["Russia", "99"])
    with patch("builtins.input", side_effect=lambda prompt="": next(inputs)):
        interface.main_menu()

    captured = capsys.readouterr()
    assert "Нет такого действия" in captured.out
