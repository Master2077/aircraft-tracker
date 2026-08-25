import json
from pathlib import Path

import pytest

from src.data_to_json import SaveDataPlanesJSON
from src.plane import Plane
import src.data_to_json as save_data_module


@pytest.fixture
def storage(tmp_path, monkeypatch):
    """
    Подменяет путь к JSON-файлу на временный.
    """
    file_path = tmp_path / "info.json"

    monkeypatch.setattr(
        save_data_module,
        "FILE_PATH",
        file_path,
    )

    return SaveDataPlanesJSON()


@pytest.fixture
def sample_planes():
    """Список объектов Plane для тестов"""
    return [
        Plane(
            country="Russia",
            callsign="SU123",
            velocity=250.5,
            vertical_velocity=0.0,
            geo_altitude=10000,
            baro_altitude=9950,
            longitude=37.6,
            latitude=55.7,
        ),
        Plane(
            country="Germany",
            callsign="TVF94PD",
            velocity=300.0,
            vertical_velocity=-2.5,
            geo_altitude=12000,
            baro_altitude=11900,
            longitude=13.4,
            latitude=52.5,
        ),
        Plane(
            country="France",
            callsign="AF456",
            velocity=280.0,
            vertical_velocity=1.2,
            geo_altitude=11000,
            baro_altitude=10950,
            longitude=2.3,
            latitude=48.8,
        ),
    ]


def planes_to_dicts(planes: list[Plane]) -> list[dict]:
    """Вспомогательная функция: Plane → dict (как в JSON)"""
    result = []
    for p in planes:
        result.append({
            "Страна регистрации": p.country,
            "Позывной рейса": p.callsign,
            "Горизонтальная скорость": p.velocity,
            "Вертикальная скорость": p.vertical_velocity,
            "Геометрическая высота": p.geo_altitude,
            "Барометрическая высота": p.baro_altitude,
            "Долгота": p.longitude,
            "Широта": p.latitude,
        })
    return result


def write_json(file_path: Path, data: list[dict]):
    file_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_json(file_path: Path):
    return json.loads(file_path.read_text(encoding="utf-8"))


# ===================== save_data =====================

def test_save_data(storage, sample_planes):
    storage.save_data(sample_planes)

    assert save_data_module.FILE_PATH.exists()
    saved = read_json(save_data_module.FILE_PATH)
    assert saved == planes_to_dicts(sample_planes)


def test_save_data_preserves_cyrillic(storage):
    planes = [
        Plane(
            country="Россия",
            callsign="АЭРОФЛОТ123",
            velocity=250.0,
            vertical_velocity=0.0,
            geo_altitude=10000,
            baro_altitude=9900,
            longitude=37.6,
            latitude=55.7,
        )
    ]

    storage.save_data(planes)

    content = save_data_module.FILE_PATH.read_text(encoding="utf-8")
    assert "Россия" in content
    assert "АЭРОФЛОТ123" in content


# ===================== load_data =====================

def test_load_data_returns_empty_list_for_missing_file(storage):
    result = storage.load_data()
    assert result == []


def test_load_data_returns_empty_list_for_empty_file(storage):
    save_data_module.FILE_PATH.touch()
    result = storage.load_data()
    assert result == []


def test_load_data_returns_all_planes(storage, sample_planes):
    write_json(save_data_module.FILE_PATH, planes_to_dicts(sample_planes))

    result = storage.load_data()

    assert len(result) == 3
    assert all(isinstance(p, Plane) for p in result)
    assert result[0].callsign == "SU123"
    assert result[1].country == "Germany"
    assert result[2].velocity == 280.0


def test_load_data_filters_by_one_criterion(storage, sample_planes):
    write_json(save_data_module.FILE_PATH, planes_to_dicts(sample_planes))

    result = storage.load_data({"Страна регистрации": "Germany"})

    assert len(result) == 1
    assert result[0].callsign == "TVF94PD"
    assert result[0].country == "Germany"


def test_load_data_filters_by_multiple_criteria_and_logic(storage, sample_planes):
    """Фильтрация работает по логике AND (все условия должны совпасть)"""
    write_json(save_data_module.FILE_PATH, planes_to_dicts(sample_planes))

    result = storage.load_data({
        "Страна регистрации": "France",
        "Позывной рейса": "AF456",
    })

    assert len(result) == 1
    assert result[0].callsign == "AF456"


def test_load_data_returns_empty_list_when_no_match(storage, sample_planes):
    write_json(save_data_module.FILE_PATH, planes_to_dicts(sample_planes))

    result = storage.load_data({"Страна регистрации": "Spain"})
    assert result == []


def test_load_data_returns_empty_list_for_invalid_json(storage):
    save_data_module.FILE_PATH.write_text("{invalid json", encoding="utf-8")

    result = storage.load_data()
    assert result == []


def test_load_data_returns_empty_list_when_json_is_not_list(storage):
    write_json(save_data_module.FILE_PATH, {"Позывной рейса": "SU123"})

    result = storage.load_data()
    assert result == []


# ===================== del_data =====================

def test_del_data_deletes_matching_records(storage, sample_planes):
    write_json(save_data_module.FILE_PATH, planes_to_dicts(sample_planes))

    result = storage.del_data({"Позывной рейса": "TVF94PD"})

    assert result == "Удалено 1 записей"

    remaining = storage.load_data()
    assert len(remaining) == 2
    assert all(p.callsign != "TVF94PD" for p in remaining)


def test_del_data_deletes_by_multiple_criteria(storage, sample_planes):
    write_json(save_data_module.FILE_PATH, planes_to_dicts(sample_planes))

    result = storage.del_data({
        "Страна регистрации": "Russia",
        "Позывной рейса": "SU123",
    })

    assert result == "Удалено 1 записей"

    remaining = storage.load_data()
    assert len(remaining) == 2
    assert remaining[0].callsign == "TVF94PD"


def test_del_data_returns_message_for_missing_file(storage):
    result = storage.del_data({"Позывной рейса": "SU123"})
    assert result == "Файла не существует или он пуст"


def test_del_data_returns_message_for_empty_file(storage):
    save_data_module.FILE_PATH.touch()
    result = storage.del_data({"Позывной рейса": "SU123"})
    assert result == "Файла не существует или он пуст"


def test_del_data_with_empty_criteria(storage, sample_planes):
    write_json(save_data_module.FILE_PATH, planes_to_dicts(sample_planes))

    result = storage.del_data({})
    assert result == "Критерии удаления не заданы"

    # Данные не должны измениться
    remaining = storage.load_data()
    assert len(remaining) == 3


