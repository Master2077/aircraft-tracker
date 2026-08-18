import json
import pytest

from src.top import TopPlanes
import src.top as top_module


@pytest.fixture
def info_file(tmp_path, monkeypatch):
    file_path = tmp_path / "info.json"

    # Подменяем FILE_PATH внутри src.top
    monkeypatch.setattr(top_module, "FILE_PATH", file_path)

    return file_path


@pytest.fixture
def planes_data():
    return [
        {
            "Название": "Самолёт A",
            "Горизонтальная скорость": 800,
            "Геометрическая высота": 10_000,
        },
        {
            "Название": "Самолёт B",
            "Горизонтальная скорость": 1_200,
            "Геометрическая высота": 15_000,
        },
        {
            "Название": "Самолёт C",
            "Горизонтальная скорость": 600,
            "Геометрическая высота": 20_000,
        },
        {
            "Название": "Самолёт D",
            "Горизонтальная скорость": None,
            "Геометрическая высота": 5_000,
        },
    ]


def save_json(file_path, data):
    file_path.write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
    )


def test_load_data(info_file, planes_data):
    save_json(info_file, planes_data)

    result = TopPlanes()._load_data()

    assert result == planes_data


def test_load_data_empty_file(info_file):
    info_file.touch()

    with pytest.raises(TypeError):
        TopPlanes()._load_data()

def test_load_data_file_does_not_exist(info_file):
    with pytest.raises(TypeError):
        TopPlanes()._load_data()


def test_load_data_invalid_json(info_file):
    info_file.write_text("{invalid json", encoding="utf-8")

    result = TopPlanes()._load_data()

    assert result == []


def test_load_data_json_is_not_list(info_file):
    save_json(info_file, {"airplane": "Самолёт"})

    result = TopPlanes()._load_data()

    assert result == []


def test_top_velocity(info_file, planes_data):
    save_json(info_file, planes_data)

    result = TopPlanes().top_velocity(3)
    result = json.loads(result)

    assert [plane["Название"] for plane in result] == [
        "Самолёт B",
        "Самолёт A",
        "Самолёт C",
    ]


def test_top_altitude(info_file, planes_data):
    save_json(info_file, planes_data)

    result = TopPlanes().top_altitude(3)
    result = json.loads(result)

    assert [plane["Название"] for plane in result] == [
        "Самолёт C",
        "Самолёт B",
        "Самолёт A",
    ]


def test_top_velocity_excludes_empty_values(info_file, planes_data):
    save_json(info_file, planes_data)

    result = TopPlanes().top_velocity(10)
    result = json.loads(result)

    names = [plane["Название"] for plane in result]

    assert "Самолёт D" not in names
    assert len(result) == 3


def test_top_velocity_returns_n_planes(info_file, planes_data):
    save_json(info_file, planes_data)

    result = TopPlanes().top_velocity(2)
    result = json.loads(result)

    assert len(result) == 2
    assert result[0]["Название"] == "Самолёт B"


def test_top_altitude_returns_n_planes(info_file, planes_data):
    save_json(info_file, planes_data)

    result = TopPlanes().top_altitude(2)
    result = json.loads(result)

    assert len(result) == 2
    assert result[0]["Название"] == "Самолёт C"


def test_top_velocity_zero(info_file, planes_data):
    save_json(info_file, planes_data)

    result = TopPlanes().top_velocity(0)

    assert json.loads(result) == []


def test_top_altitude_zero(info_file, planes_data):
    save_json(info_file, planes_data)

    result = TopPlanes().top_altitude(0)

    assert json.loads(result) == []


def test_top_velocity_negative_number(info_file):
    save_json(info_file, [])

    with pytest.raises(
        ValueError,
        match="Количество самолётов не может быть отрицательным",
    ):
        TopPlanes().top_velocity(-1)


def test_top_altitude_negative_number(info_file):
    save_json(info_file, [])

    with pytest.raises(
        ValueError,
        match="Количество самолётов не может быть отрицательным",
    ):
        TopPlanes().top_altitude(-1)


