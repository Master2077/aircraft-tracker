import json
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.postgres import DBManager


class FakePlane:
    def __init__(
        self,
        country,
        callsign,
        velocity,
        vertical_velocity,
        geo_altitude,
        baro_altitude,
        longitude,
        latitude,
    ):
        self.country = country
        self.callsign = callsign
        self.velocity = velocity
        self.vertical_velocity = vertical_velocity
        self.geo_altitude = geo_altitude
        self.baro_altitude = baro_altitude
        self.longitude = longitude
        self.latitude = latitude


@pytest.fixture
def db_manager():
    with patch("src.postgres.psycopg2.connect") as mock_connect:
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        db = DBManager()
        db.connection = mock_connection
        yield db


def test_create_tables(db_manager):
    cursor = MagicMock()
    db_manager.connection.cursor.return_value.__enter__.return_value = cursor

    db_manager.create_tables()

    assert cursor.execute.call_count == 2
    db_manager.connection.commit.assert_not_called()


@patch("builtins.input", side_effect=["Россия", "стоп"])
def test_get_countries_and_aeroplanes_count(mock_input, db_manager):
    db_manager.country.get_information = MagicMock()
    db_manager.country.get_information.return_value = []
    db_manager.country.country = "Россия"
    db_manager.country.aeroplanes_count = 5

    cursor = MagicMock()
    db_manager.connection.cursor.return_value.__enter__.return_value = cursor

    rows = db_manager.get_countries_and_aeroplanes_count()

    assert rows == [("Россия", 5)]
    cursor.executemany.assert_called_once_with(
        "INSERT INTO countries_and_aeroplanes (country, aeroplanes_count) VALUES (%s, %s)",
        [("Россия", 5)],
    )
    db_manager.connection.commit.assert_called_once()


def test_get_all_aeroplanes(db_manager):
    db_manager.country.get_information = MagicMock()
    db_manager.country.get_information.side_effect = [
        [FakePlane("Россия", "ABC123", 100.0, 1.0, 10000.0, 9500.0, 30.1, 59.9)]
    ]
    db_manager.country.country = "Россия"

    cursor = MagicMock()
    cursor.fetchall.return_value = [("Россия",)]
    db_manager.connection.cursor.return_value.__enter__.return_value = cursor

    m = mock_open()
    with patch("builtins.open", m), patch("src.postgres.FILE_PATH", "dummy.json"):
        rows = db_manager.get_all_aeroplanes()

    assert rows == [("Россия", "ABC123", 100.0, 1.0, 10000.0, 9500.0, 30.1, 59.9)]
    cursor.executemany.assert_called_once()
    db_manager.connection.commit.assert_called_once()

    written = "".join(call.args[0] for call in m().write.call_args_list)
    assert json.loads(written)[0]["country"] == "Россия"


def test_get_avg_speed(db_manager):
    cursor = MagicMock()
    cursor.fetchone.return_value = (123.45,)
    db_manager.connection.cursor.return_value.__enter__.return_value = cursor

    avg = db_manager.get_avg_speed()

    assert avg == 123.45
    cursor.execute.assert_called_once_with("SELECT AVG(velocity) FROM aeroplanes")


def test_get_aeroplanes_with_higher_speed(db_manager):
    db_manager.avg_velocity = 200.0

    cursor = MagicMock()
    cursor.fetchall.return_value = [("row1",), ("row2",)]
    db_manager.connection.cursor.return_value.__enter__.return_value = cursor

    result = db_manager.get_aeroplanes_with_higher_speed()

    assert result == [("row1",), ("row2",)]
    cursor.execute.assert_called_once_with(
        "SELECT * FROM aeroplanes WHERE velocity > %s",
        (200.0,),
    )


@patch("builtins.input", return_value="abc")
def test_get_aeroplanes_with_keyword(mock_input, db_manager):
    cursor = MagicMock()
    cursor.fetchall.return_value = [("row1",)]
    db_manager.connection.cursor.return_value.__enter__.return_value = cursor

    result = db_manager.get_aeroplanes_with_keyword()

    assert result == [("row1",)]
    cursor.execute.assert_called_once_with(
        "SELECT * FROM aeroplanes WHERE callsign ILIKE %s",
        ("%Abc%",),
    )
