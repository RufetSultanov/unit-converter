"""Учебный API для преобразования единиц измерения."""

from fastapi import FastAPI


APP_VERSION = "1.0.0"

app = FastAPI(
    title ="Unit Converter",
    description="Сервис перевода температуры, расстояния и массы",
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
