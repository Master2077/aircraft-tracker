from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def interface_class():
    """
    Импортирует класс Interface с подменённым пользовательским вводом.

    Это необходимо, потому что main_menu() запускается
    непосредственно при импорте src.main.
    """

    # Значения, которые будут использованы при автоматическом
    # запуске main_menu() во время импорта src.main:
    #
    # 1. Название страны;
    # 2. Пункт меню;
    # 3. Количество самолётов.
    input_values = iter([
        "Russia",
        "1",
        "3",
    ])

    with patch(
        "builtins.input",
        side_effect=lambda prompt="": next(input_values),
    ), patch(
        "src.data_to_json.SaveDataPlanesJSON.get_information",
        return_value=[],
    ), patch(
        "src.data_to_json.SaveDataPlanesJSON.save_data",
        return_value=None,
    ), patch(
        "src.top.TopPlanes.top_altitude",
        return_value="Тестовый результат",
    ):
        from src.main import Interface

    return Interface


def test_interface_is_created(interface_class):
    """
    Проверяет создание объекта Interface.
    """

    interface = interface_class()

    assert interface is not None
    assert isinstance(interface, interface_class)


def test_main_menu_top_altitude(interface_class, capsys):
    """
    Проверяет выбор топа самолётов по высоте.
    """

    interface = interface_class()

    # Подменяем методы объекта, чтобы не обращаться к API
    # и не работать с реальным JSON-файлом.
    interface.get_information = Mock()
    interface.save_data = Mock()
    interface.top_altitude = Mock(
        return_value="Топ самолётов по высоте"
    )

    # Имитируем действия пользователя:
    # страна, пункт меню, количество самолётов.
    input_values = iter([
        "Russia",
        "1",
        "5",
    ])

    with patch(
        "builtins.input",
        side_effect=lambda prompt="": next(input_values),
    ):
        interface.main_menu()

    # Проверяем получение информации о стране.
    interface.get_information.assert_called_once_with("Russia")

    # Проверяем сохранение данных.
    interface.save_data.assert_called_once_with()

    # Проверяем получение топа из пяти самолётов.
    interface.top_altitude.assert_called_once_with(5)

    # Проверяем вывод результата.
    captured = capsys.readouterr()

    assert "Топ самолётов по высоте" in captured.out


def test_main_menu_top_velocity(interface_class):
    """
    Проверяет выбор топа самолётов по скорости.
    """

    interface = interface_class()

    interface.get_information = Mock()
    interface.save_data = Mock()
    interface.top_velocity = Mock(
        return_value="Топ самолётов по скорости"
    )

    input_values = iter([
        "Germany",
        "2",
        "10",
    ])

    with patch(
        "builtins.input",
        side_effect=lambda prompt="": next(input_values),
    ):
        interface.main_menu()

    interface.get_information.assert_called_once_with("Germany")
    interface.save_data.assert_called_once_with()
    interface.top_velocity.assert_called_once_with(10)


def test_main_menu_search_by_registration_country(
    interface_class,
):
    """
    Проверяет поиск самолётов по стране регистрации.
    """

    interface = interface_class()

    interface.get_information = Mock()
    interface.save_data = Mock()
    interface.load_data = Mock(
        return_value='[{"Страна регистрации": "France"}]'
    )

    input_values = iter([
        "Russia",
        "3",
        "france",
    ])

    with patch(
        "builtins.input",
        side_effect=lambda prompt="": next(input_values),
    ):
        interface.main_menu()

    interface.get_information.assert_called_once_with("Russia")
    interface.save_data.assert_called_once_with()

    # Метод capitalize() преобразует "france" в "France".
    interface.load_data.assert_called_once_with({
        "Страна регистрации": "France"
    })
