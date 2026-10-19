"""Учебный API для преобразования единиц измерения."""

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Query, Request


APP_VERSION = "1.0.0"
APP_NAME = os.getenv("APP_NAME", "Unit Converter")
APP_AUTHOR = os.getenv("APP_AUTHOR", "Rufet Sultanov")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger("unit_converter")
logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Записать в лог запуск и остановку сервиса."""
    logger.info(
        "Service started: name=%s version=%s",
        APP_NAME,
        APP_VERSION,
    )
    yield
    logger.info("Service stopped: name=%s", APP_NAME)


app = FastAPI(
    title=APP_NAME,
    description="Сервис перевода температуры, расстояния и массы.",
    version=APP_VERSION,
    lifespan=lifespan,
)


@app.middleware("http")
async def log_request(request: Request, call_next):
    """Записать метод, путь, статус и время обработки запроса."""
    started = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Request failed: %s %s",
            request.method,
            request.url.path,
        )
        raise

    logger.info(
        "Request: %s %s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        (time.perf_counter() - started) * 1000,
    )

    return response


def conversion_response(
    value: float,
    from_unit: str,
    result: float,
    to_unit: str,
):
    """Округлить результат, записать событие и подготовить ответ."""
    rounded = round(result, 4)

    logger.info(
        "Conversion: %s %s -> %s %s",
        value,
        from_unit,
        rounded,
        to_unit,
    )

    return {
        "input": value,
        "from_unit": from_unit,
        "result": rounded,
        "to_unit": to_unit,
    }


@app.get("/", tags=["Сервис"])
def root():
    """Показать назначение и настройки приложения."""
    return {
        "name": APP_NAME,
        "author": APP_AUTHOR,
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

    return conversion_response(
        celsius,
        "celsius",
        fahrenheit,
        "fahrenheit",
    )


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

    return conversion_response(
        kilometers,
        "kilometers",
        miles,
        "miles",
    )


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

    return conversion_response(
        kilograms,
        "kilograms",
        pounds,
        "pounds",
    )
