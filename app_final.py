"""Учебный API для преобразования единиц измерения."""

from typing import Annotated

from fastapi import FastAPI, Query


APP_VERSION = "1.0.0"

app = FastAPI(
    title="Unit Converter",
    description="Сервис перевода температуры, расстояния и массы.",
    version=APP_VERSION,
)


@app.get("/", tags=["Сервис"])
def root():
    """Показать назначение приложения."""
    return {
        "name": "Unit Converter",
        "description": "Перевод температуры, расстояния и массы.",
        "docs": "/docs",
    }


@app.get("/health", tags=["Сервис"])
def health():
    """Проверить работоспособность приложения."""
    return {"status": "ok"}


@app.get("/version", tags=["Сервис"])
def version():
    """Показать версию приложения."""
    return {"version": APP_VERSION}


@app.get("/convert/temperature", tags=["Преобразования"])
def convert_temperature(
    celsius: Annotated[
        float,
        Query(
            ge=-273.15,
            le=1e12,
            allow_inf_nan=False,
            description="Температура в градусах Цельсия",
        ),
    ],
):
    """Перевести градусы Цельсия в градусы Фаренгейта."""
    fahrenheit = celsius * 9 / 5 + 32

    return {
        "input": celsius,
        "from_unit": "celsius",
        "result": round(fahrenheit, 4),
        "to_unit": "fahrenheit",
    }


@app.get("/convert/distance", tags=["Преобразования"])
def convert_distance(
    kilometers: Annotated[
        float,
        Query(
            ge=0,
            le=1e12,
            allow_inf_nan=False,
            description="Расстояние в километрах",
        ),
    ],
):
    """Перевести километры в международные мили."""
    miles = kilometers / 1.609344

    return {
        "input": kilometers,
        "from_unit": "kilometers",
        "result": round(miles, 4),
        "to_unit": "miles",
    }


@app.get("/convert/weight", tags=["Преобразования"])
def convert_weight(
    kilograms: Annotated[
        float,
        Query(
            ge=0,
            le=1e12,
            allow_inf_nan=False,
            description="Масса в килограммах",
        ),
    ],
):
    """Перевести килограммы в фунты."""
    pounds = kilograms / 0.45359237

    return {
        "input": kilograms,
        "from_unit": "kilograms",
        "result": round(pounds, 4),
        "to_unit": "pounds",
    }
