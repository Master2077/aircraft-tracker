import json
from pathlib import Path

import psycopg2

from src.plane_info import InformationAboutPlanes


FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "aeroplanes.json"


class DBManager:
    """Класс для работы с базой данных и хранения информации о самолетах."""

    def __init__(self):
        """Инициализирует подключение к базе данных и вспомогательные атрибуты."""
        self.connection = psycopg2.connect(
            host="localhost",
            database="aircraft",
            user="postgres",
            password="Star002_Jinx",
        )
        self.country = InformationAboutPlanes()
        self.avg_velocity = None

    def create_tables(self):
        """Создает таблицы в базе данных, если они еще не существуют."""
        with self.connection.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS countries_and_aeroplanes (
                    id SERIAL PRIMARY KEY,
                    country VARCHAR(50),
                    aeroplanes_count INT
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS aeroplanes (
                    id SERIAL PRIMARY KEY,
                    country VARCHAR(50),
                    callsign VARCHAR(50),
                    velocity REAL,
                    vertical_velocity REAL,
                    geo_altitude REAL,
                    baro_altitude REAL,
                    longitude REAL,
                    latitude REAL
                )
                """
            )

    def get_countries_and_aeroplanes_count(self):
        """
        Запрашивает у пользователя список стран, получает для них количество
        самолетов и сохраняет результат в таблицу countries_and_aeroplanes.
        """
        rows = []

        while True:
            country_name = input(
                'Введите название страны (или "стоп" для завершения): '
            ).strip().capitalize()

            if country_name.lower() == "стоп":
                break

            try:
                self.country.get_information(country_name)
                rows.append((self.country.country, self.country.aeroplanes_count))
            except Exception as e:
                print(e)

        with self.connection.cursor() as cur:
            cur.executemany(
                "INSERT INTO countries_and_aeroplanes "
                "(country, aeroplanes_count) VALUES (%s, %s)",
                rows,
            )
        self.connection.commit()

        return rows

    def get_all_aeroplanes(self):
        """
        Получает список стран из базы, затем для каждой страны загружает
        данные о самолетах, сохраняет их в таблицу aeroplanes и в JSON-файл.
        """
        rows = []

        with self.connection.cursor() as cur:
            cur.execute("SELECT country FROM countries_and_aeroplanes")
            countries = [row[0] for row in cur.fetchall()]

        for country_name in countries:
            try:
                planes = self.country.get_information(country_name)

                for plane in planes:
                    rows.append(
                        (
                            self.country.country,
                            plane.callsign,
                            plane.velocity,
                            plane.vertical_velocity,
                            plane.geo_altitude,
                            plane.baro_altitude,
                            plane.longitude,
                            plane.latitude,
                        )
                    )
            except Exception as e:
                print(e)

        if rows:
            with self.connection.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO aeroplanes
                    (country, callsign, velocity, vertical_velocity, geo_altitude,
                    baro_altitude, longitude, latitude)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    rows,
                )
            self.connection.commit()

            data = []
            for row in rows:
                data.append(
                    {
                        "country": row[0],
                        "callsign": row[1],
                        "velocity": row[2],
                        "vertical_velocity": row[3],
                        "geo_altitude": row[4],
                        "baro_altitude": row[5],
                        "longitude": row[6],
                        "latitude": row[7],
                    }
                )

            with open(FILE_PATH, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

        return rows

    def get_avg_speed(self):
        """Вычисляет среднюю скорость самолетов в таблице aeroplanes."""
        with self.connection.cursor() as cur:
            cur.execute("SELECT AVG(velocity) FROM aeroplanes")
            self.avg_velocity = cur.fetchone()[0]
            return self.avg_velocity

    def get_aeroplanes_with_higher_speed(self):
        """Возвращает самолеты, скорость которых выше среднего значения."""
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT * FROM aeroplanes WHERE velocity > %s",
                (self.avg_velocity,),
            )
            return cur.fetchall()

    def get_aeroplanes_with_keyword(self):
        """Ищет самолеты по части позывного, введенной пользователем."""
        keyword = input("Введите позывной или известные символы в нем: ").strip().capitalize()
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT * FROM aeroplanes WHERE callsign ILIKE %s",
                (f"%{keyword}%",),
            )
            return cur.fetchall()


if __name__ == "__main__":
    db = DBManager()
    db.create_tables()
    print(db.get_countries_and_aeroplanes_count())
    print(db.get_all_aeroplanes())
    print(db.get_avg_speed())
    print(db.get_aeroplanes_with_higher_speed())
    print(db.get_aeroplanes_with_keyword())
