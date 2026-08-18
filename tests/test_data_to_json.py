import json

import pytest

from src.data_to_json import SaveDataPlanesJSON
import src.data_to_json as save_data_module


@pytest.fixture
def storage(tmp_path, monkeypatch):
    """
    Создаёт объект без вызова __init__ и подменяет путь к JSON-файлу.
    Благодаря этому не выполняется настоящий запрос к API.
    """
    file_path = tmp_path / "info.json"

    monkeypatch.setattr(
        save_data_module,
        "FILE_PATH",
        file_path,
    )

    obj = SaveDataPlanesJSON.__new__(SaveDataPlanesJSON)
    obj.information = []

    return obj


@pytest.fixture
def planes_data():
    return [
        {
            "Страна регистрации": "Russia",
            "Позывной рейса": "SU123",
            "Горизонтальная скорость": 250.5,
            "Геометрическая высота": 10_000,
        },
        {
            "Страна регистрации": "Germany",
            "Позывной рейса": "TVF94PD",
            "Горизонтальная скорость": 300,
            "Геометрическая высота": 12_000,
        },
        {
            "Страна регистрации": "France",
            "Позывной рейса": "AF456",
            "Горизонтальная скорость": 280,
            "Геометрическая высота": 11_000,
        },
    ]


def write_json(file_path, data):
    file_path.write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
    )


def read_json(file_path):
    return json.loads(
        file_path.read_text(encoding="utf-8")
    )


def test_save_data(storage, planes_data):
    storage.information = planes_data

    storage.save_data()

    assert save_data_module.FILE_PATH.exists()
    assert read_json(save_data_module.FILE_PATH) == planes_data


def test_save_data_preserves_cyrillic_symbols(storage):
    storage.information = [
        {
            "Страна регистрации": "Россия",
            "Позывной рейса": "АЭРОФЛОТ123",
        }
    ]

    storage.save_data()

    content = save_data_module.FILE_PATH.read_text(
        encoding="utf-8"
    )

    assert "Россия" in content
    assert "АЭРОФЛОТ123" in content


def test_load_data_returns_message_for_missing_file(storage):
    result = storage.load_data({})

    assert result == "Файла не существует или же он пуст"


def test_load_data_returns_message_for_empty_file(storage):
    save_data_module.FILE_PATH.touch()

    result = storage.load_data({})

    assert result == "Файла не существует или же он пуст"


def test_load_data_returns_all_data_without_criteria(
    storage,
    planes_data,
):
    write_json(save_data_module.FILE_PATH, planes_data)

    result = storage.load_data({})

    assert result == planes_data


def test_load_data_filters_by_one_criterion(
    storage,
    planes_data,
):
    write_json(save_data_module.FILE_PATH, planes_data)

    result = storage.load_data(
        {"Страна регистрации": "Germany"}
    )

    assert json.loads(result) == [planes_data[1]]


def test_load_data_filters_by_any_criterion(
    storage,
    planes_data,
):
    write_json(save_data_module.FILE_PATH, planes_data)

    result = storage.load_data(
        {
            "Страна регистрации": "France",
            "Позывной рейса": "SU123",
        }
    )

    result = json.loads(result)

    assert result == [
        planes_data[0],
        planes_data[2],
    ]


def test_load_data_returns_empty_list_for_invalid_json(storage):
    save_data_module.FILE_PATH.write_text(
        "{invalid json",
        encoding="utf-8",
    )

    result = storage.load_data({})

    assert result == []


def test_load_data_returns_empty_list_when_json_is_not_list(
    storage,
):
    write_json(
        save_data_module.FILE_PATH,
        {"Позывной рейса": "SU123"},
    )

    result = storage.load_data(
        {"Позывной рейса": "SU123"}
    )

    assert result == []


def test_del_data_deletes_matching_records(
    storage,
    planes_data,
):
    write_json(save_data_module.FILE_PATH, planes_data)

    result = storage.del_data(
        {"Позывной рейса": "TVF94PD"}
    )

    assert result == "Удалено 1 данных"
    assert read_json(save_data_module.FILE_PATH) == [
        planes_data[0],
        planes_data[2],
    ]


def test_del_data_deletes_records_by_any_criterion(
    storage,
    planes_data,
):
    write_json(save_data_module.FILE_PATH, planes_data)

    result = storage.del_data(
        {
            "Позывной рейса": "SU123",
            "Страна регистрации": "France",
        }
    )

    assert result == "Удалено 2 данных"
    assert read_json(save_data_module.FILE_PATH) == [
        planes_data[1],
    ]


def test_del_data_returns_message_for_missing_file(storage):
    result = storage.del_data(
        {"Позывной рейса": "SU123"}
    )

    assert result == "Файла не существует или же он пуст"


def test_del_data_returns_message_for_empty_file(storage):
    save_data_module.FILE_PATH.touch()

    result = storage.del_data(
        {"Позывной рейса": "SU123"}
    )

    assert result == "Файла не существует или же он пуст"


def test_del_data_returns_empty_list_for_invalid_json(storage):
    save_data_module.FILE_PATH.write_text(
        "{invalid json",
        encoding="utf-8",
    )

    result = storage.del_data(
        {"Позывной рейса": "SU123"}
    )

    assert result == []


def test_del_data_with_empty_criteria_returns_original_data(
    storage,
    planes_data,
):
    write_json(save_data_module.FILE_PATH, planes_data)

    result = storage.del_data({})

    assert result == planes_data
    assert read_json(save_data_module.FILE_PATH) == planes_data
