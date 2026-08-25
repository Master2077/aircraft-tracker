import json
import pytest

from src.top import TopPlanes
from src.plane import Plane


@pytest.fixture
def sample_planes():
     return [
     Plane(
     country="Russia",
     callsign="PlaneA",
     velocity=800,
     vertical_velocity=0.0,
     geo_altitude=10000,
     baro_altitude=9900,
     longitude=37.6,
     latitude=55.7,
     ),
     Plane(
     country="Germany",
     callsign="PlaneB",
     velocity=1200,
     vertical_velocity=-1.5,
     geo_altitude=15000,
     baro_altitude=14800,
     longitude=13.4,
     latitude=52.5,
     ),
     Plane(
     country="France",
     callsign="PlaneC",
     velocity=600,
     vertical_velocity=2.0,
     geo_altitude=20000,
     baro_altitude=19800,
     longitude=2.3,
     latitude=48.8,
     ),
     Plane(
     country="Spain",
     callsign="PlaneD",
     velocity=None, # нет скорости
     vertical_velocity=0.0,
     geo_altitude=5000,
     baro_altitude=4900,
     longitude=-3.7,
     latitude=40.4,
     ),
     Plane(
     country="Italy",
     callsign="PlaneE",
     velocity=900,
     vertical_velocity=0.5,
     geo_altitude=None, # нет высоты
     baro_altitude=None,
     longitude=12.5,
     latitude=41.9,
     ),
     ]


@pytest.fixture
def top_service():
 return TopPlanes()


def test_top_velocity(top_service, sample_planes):
 result = top_service.top_velocity(sample_planes, 3)
 data = json.loads(result)

 assert len(data) == 3
 assert [plane["Позывной рейса"] for plane in data] == [
 "PlaneB", # 1200
 "PlaneE", # 900
 "PlaneA", # 800
 ]


def test_top_altitude(top_service, sample_planes):
 result = top_service.top_altitude(sample_planes, 3)
 data = json.loads(result)

 assert len(data) == 3
 assert [plane["Позывной рейса"] for plane in data] == [
 "PlaneC", # 20000
 "PlaneB", # 15000
 "PlaneA", # 10000
 ]


def test_top_velocity_excludes_none_values(top_service, sample_planes):
 result = top_service.top_velocity(sample_planes, 10)
 data = json.loads(result)

 callsigns = [plane["Позывной рейса"] for plane in data]
 assert "PlaneD" not in callsigns # velocity = None
 assert len(data) == 4 # все, кроме PlaneD


def test_top_altitude_excludes_none_values(top_service, sample_planes):
 result = top_service.top_altitude(sample_planes, 10)
 data = json.loads(result)

 callsigns = [plane["Позывной рейса"] for plane in data]
 assert "PlaneE" not in callsigns # geo_altitude = None
 assert len(data) == 4


def test_top_velocity_returns_n_planes(top_service, sample_planes):
 result = top_service.top_velocity(sample_planes, 2)
 data = json.loads(result)

 assert len(data) == 2
 assert data[0]["Позывной рейса"] == "PlaneB"


def test_top_altitude_returns_n_planes(top_service, sample_planes):
 result = top_service.top_altitude(sample_planes, 2)
 data = json.loads(result)

 assert len(data) == 2
 assert data[0]["Позывной рейса"] == "PlaneC"


def test_top_velocity_zero(top_service, sample_planes):
 result = top_service.top_velocity(sample_planes, 0)
 assert json.loads(result) == []


def test_top_altitude_zero(top_service, sample_planes):
 result = top_service.top_altitude(sample_planes, 0)
 assert json.loads(result) == []


def test_top_velocity_negative_number(top_service, sample_planes):
 with pytest.raises(ValueError, match="Количество самолетов не может быть отрицательным"):
    top_service.top_velocity(sample_planes, -1)


def test_top_altitude_negative_number(top_service, sample_planes):
 with pytest.raises(ValueError, match="Количество самолетов не может быть отрицательным"):
    top_service.top_altitude(sample_planes, -1)


def test_top_velocity_not_int(top_service, sample_planes):
 with pytest.raises(TypeError, match="Количество самолетов должно быть целым числом"):
    top_service.top_velocity(sample_planes, "3")


def test_top_altitude_not_int(top_service, sample_planes):
 with pytest.raises(TypeError, match="Количество самолетов должно быть целым числом"):
    top_service.top_altitude(sample_planes, 2.5)


def test_top_velocity_empty_list(top_service):
 result = top_service.top_velocity([], 5)
 assert json.loads(result) == []


def test_top_altitude_empty_list(top_service):
 result = top_service.top_altitude([], 5)
 assert json.loads(result) == []

