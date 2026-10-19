"""Проверки вычислений, параметров, настроек и логирования."""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app_final import app


@pytest.fixture
def client():
    """Создать клиент и выполнить запуск и остановку приложения."""
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version(client):
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": "1.0.0"}


@pytest.mark.parametrize(
    "path,parameter,value,expected,from_unit,to_unit",
    [
        ("temperature", "celsius", 20, 68, "celsius", "fahrenheit"),
        ("temperature", "celsius", -40, -40, "celsius", "fahrenheit"),
        (
            "temperature",
            "celsius",
            -273.15,
            -459.67,
            "celsius",
            "fahrenheit",
        ),
        ("distance", "kilometers", 10, 6.2137, "kilometers", "miles"),
        ("distance", "kilometers", 0, 0, "kilometers", "miles"),
        ("distance", "kilometers", 1.609344, 1, "kilometers", "miles"),
        ("weight", "kilograms", 5, 11.0231, "kilograms", "pounds"),
        ("weight", "kilograms", 0, 0, "kilograms", "pounds"),
        ("weight", "kilograms", 0.45359237, 1, "kilograms", "pounds"),
    ],
)
def test_conversion(
    client,
    path,
    parameter,
    value,
    expected,
    from_unit,
    to_unit,
):
    response = client.get(
        f"/convert/{path}",
        params={parameter: value},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["input"] == value
    assert data["from_unit"] == from_unit
    assert data["to_unit"] == to_unit
    assert data["result"] == pytest.approx(
        expected,
        rel=0,
        abs=0.00005,
    )


@pytest.mark.parametrize(
    "path,parameter,value",
    [
        ("temperature", "celsius", -273.16),
        ("distance", "kilometers", -1),
        ("weight", "kilograms", -5),
        ("temperature", "celsius", "abc"),
        ("distance", "kilometers", "abc"),
        ("weight", "kilograms", "abc"),
        ("temperature", "celsius", "nan"),
        ("distance", "kilometers", "inf"),
        ("weight", "kilograms", "-inf"),
        ("temperature", "celsius", 1e13),
        ("distance", "kilometers", 1e13),
        ("weight", "kilograms", 1e13),
    ],
)
def test_invalid_parameter(client, path, parameter, value):
    response = client.get(
        f"/convert/{path}",
        params={parameter: value},
    )

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["query", parameter]
        for error in errors
    )


@pytest.mark.parametrize(
    "path",
    ["temperature", "distance", "weight"],
)
def test_missing_parameter(client, path):
    response = client.get(f"/convert/{path}")

    assert response.status_code == 422


def test_docs(client):
    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_environment_configuration():
    """Проверить чтение настроек при новом запуске Python."""
    env = {
        **os.environ,
        "APP_NAME": "Test Converter",
        "APP_AUTHOR": "Test Author",
    }

    script = (
        "import json; "
        "from app_final import root, app; "
        "print(json.dumps({'root': root(), 'title': app.title}))"
    )

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).parent,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)

    assert data["root"]["name"] == "Test Converter"
    assert data["title"] == "Test Converter"
    assert data["root"]["author"] == "Test Author"


def test_lifecycle_and_request_logs(caplog):
    with caplog.at_level(logging.INFO, logger="unit_converter"):
        with TestClient(app) as client:
            response = client.get(
                "/convert/weight",
                params={"kilograms": 1},
            )

    assert response.status_code == 200

    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == "unit_converter"
    ]

    assert any(
        "Service started:" in message
        for message in messages
    )

    assert any(
        "Conversion:" in message and "pounds" in message
        for message in messages
    )

    assert any(
        "GET /convert/weight status=200" in message
        for message in messages
    )

    assert any(
        "Service stopped:" in message
        for message in messages
    )
