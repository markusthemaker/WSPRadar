"""Execute frozen-source reference queries with a bounded ClickHouse adapter.

Scientific SELECT expressions and predicates run unchanged in SQLite; only the
output FORMAT clause is removed. This is not native ClickHouse engine or
geographic-distance validation. Keep fixture expectations independent of this
adapter and application code.
"""

from contextlib import closing
from datetime import datetime, timezone
import math
import re
import sqlite3

import pandas as pd


class _AnyValue:
    def __init__(self):
        self.value = None

    def step(self, value):
        if self.value is None:
            self.value = value

    def finalize(self):
        return self.value


class _MaximumIf(_AnyValue):
    def step(self, value, condition):
        if condition and (self.value is None or value > self.value):
            self.value = value

    def finalize(self):
        return 0 if self.value is None else self.value


class _CountIf:
    def __init__(self):
        self.count = 0

    def step(self, condition):
        self.count += bool(condition)

    def finalize(self):
        return self.count


class _ArgMaximumIf(_AnyValue):
    def __init__(self):
        super().__init__()
        self.maximum = None
        self.default = 0

    def step(self, argument, value, condition):
        self.default = "" if isinstance(argument, str) else 0
        if condition and (self.maximum is None or value > self.maximum):
            self.maximum, self.value = value, argument

    def finalize(self):
        return self.default if self.maximum is None else self.value


def _spherical_distance_m(longitude_a, latitude_a, longitude_b, latitude_b):
    """Diagnostic distance only; this is not ClickHouse geoDistance validation."""
    longitude_a, latitude_a, longitude_b, latitude_b = map(
        math.radians, (longitude_a, latitude_a, longitude_b, latitude_b)
    )
    haversine = math.sin((latitude_b - latitude_a) / 2) ** 2 + (
        math.cos(latitude_a) * math.cos(latitude_b)
        * math.sin((longitude_b - longitude_a) / 2) ** 2
    )
    return 6371000 * 2 * math.asin(min(1, math.sqrt(haversine)))


def execute_generated_sql(query, source_rows):
    # Only the output serialization directive is removed. Scientific SQL is
    # neither reconstructed from expected values nor translated into Python.
    assert re.search(r"\sFORMAT CSVWithNames\s*$", query)
    statement = re.sub(r"\sFORMAT CSVWithNames\s*$", "", query)
    with closing(sqlite3.connect(":memory:")) as connection:
        connection.execute("ATTACH DATABASE ':memory:' AS wspr")
        connection.create_function("toUnixTimestamp", 1, lambda value: float(
            datetime.fromisoformat(value).replace(tzinfo=timezone.utc).timestamp()
        ))
        connection.create_function("floor", 1, math.floor)
        connection.create_function("geoDistance", 4, _spherical_distance_m)
        for name, argument_count, aggregate in (
            ("any", 1, _AnyValue), ("maxIf", 2, _MaximumIf),
            ("countIf", 1, _CountIf), ("argMaxIf", 3, _ArgMaximumIf),
        ):
            connection.create_aggregate(name, argument_count, aggregate)
        prepared = source_rows.copy()
        prepared["time"] = pd.to_datetime(prepared["time"], utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")
        # The attached table keeps the production schema-qualified name intact.
        declarations = [
            f'"{column}" ' + ("INTEGER" if column in {"id", "band", "code", "snr", "power"}
                             else "REAL" if column.endswith(("_lat", "_lon")) else "TEXT")
            for column in prepared.columns
        ]
        connection.execute("CREATE TABLE wspr.rx (" + ",".join(declarations) + ")")
        connection.executemany(
            "INSERT INTO wspr.rx VALUES (" + ",".join("?" for _ in prepared.columns) + ")",
            prepared.itertuples(index=False, name=None),
        )
        return pd.read_sql_query(statement, connection)
