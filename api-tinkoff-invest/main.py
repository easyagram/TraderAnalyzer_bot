from flask import Flask, request, jsonify
import os
import asyncio
import logging
from investpy import Client, CandleInterval
from datetime import datetime, timedelta

app = Flask(__name__)

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен Tinkoff API из переменной окружения
TINKOFF_TOKEN = os.getenv("TINKOFF_TOKEN")
if not TINKOFF_TOKEN:
    logger.error("TINKOFF_TOKEN не установлен в переменных окружения!")
    exit()

# --- Функции для работы с Tinkoff Invest API ---
async def get_candles(ticker: str, from_date: datetime, to_date: datetime, interval: CandleInterval):
    """Получает исторические свечи для указанного тикера."""
    try:
        async with Client(TINKOFF_TOKEN) as client:
            instruments = await client.instruments.find_instrument(query=ticker)
            if not instruments.instruments:
                logger.warning(f"Инструмент {ticker} не найден")
                return []
            instrument = instruments.instruments[0]
            candles = await client.market_data.get_candles(
                instrument_id=instrument.uid,
                from_=from_date,
                to=to_date,
                interval=interval
            )
            logger.info(f"Получены свечи для {ticker} с {from_date} по {to_date}")
            return candles.candles
    except Exception as e:
        logger.exception(f"Ошибка при получении свечей для {ticker}: {e}")
        return []

# --- Функции анализа ---
async def calculate_anomalous_volumes(ticker: str):
    """Вычисляет аномальные объемы."""
    try:
        now = datetime.utcnow()
        candles = await get_candles(
            ticker,
            from_date=now - timedelta(days=30),  # Исторические данные за 30 дней
            to_date=now,
            interval=CandleInterval.CANDLE_INTERVAL_HOUR  # Hourly interval
        )

        if not candles:
            logger.warning(f"Не удалось получить данные для расчета аномальных объемов для {ticker}")
            return {"anomalous_volume": "Недостаточно данных"}

        # 1. calculate the volume for this time
        total_volume = sum(candle.volume for candle in candles)
        average_volume = total_volume / len(candles) if candles else 0
        candles_now = await get_candles(
            ticker,
            from_date=now - timedelta(hours=1),  # Volume за последний час
            to_date=now,
            interval=CandleInterval.CANDLE_INTERVAL_HOUR
        )
        current_volume = 0
        if(candles_now):
            current_volume=candles_now[0].volume
        anomalous_volume = True if (current_volume>average_volume * 2) else False  # Set anomalous volume

        logger.info(f"Рассчитаны аномальные объемы для {ticker}")
        return {"anomalous_volume": anomalous_volume, "current_volume":current_volume, "average_volume":average_volume}

    except Exception as e:
        logger.exception(f"Ошибка при расчете аномальных объемов для {ticker}: {e}")
        return {"anomalous_volume": "Ошибка при расчете"}

async def analyze_anomalous_limits(ticker: str):
    """Анализирует аномальные лимитки."""
    # TODO: Implement the logic here
    logger.warning(f"Анализ аномальных лимиток не реализован (требуется доступ к стакану заявок)")
    return {"anomalous_limits": "Не реализовано"}

async def calculate_net_flow(ticker: str):
    """Вычисляет индикатор чистых покупок и продаж."""
    try:
        now = datetime.utcnow()
        candles = await get_candles(
            ticker,
            from_date=now - timedelta(days=7),  # Исторические данные за 7 дней
            to_date=now,
            interval=CandleInterval.CANDLE_INTERVAL_HOUR  # Hourly interval
        )

        if not candles:
            logger.warning(f"Не удалось получить данные для расчета чистого потока для {ticker}")
            return {"net_flow": "Недостаточно данных"}

        # TODO: calculate the indicator 
        net_flow = 'not calculated'

        logger.info(f"Рассчитан чистый поток для {ticker}: {net_flow}")
        return {"net_flow": net_flow}

    except Exception as e:
        logger.exception(f"Ошибка при расчете чистого потока для {ticker}: {e}")
        return {"net_flow": "Ошибка при расчете"}

async def calculate_short_squeeze(ticker: str):
    """Вычисляет индикатор шорт-сквиза."""
    # TODO: Требуется анализировать количество шортов, но это нереально. Нужны другие варианты.
    logger.warning(f"Расчет шорт-сквиза не реализован (требуются данные о шортах)")
    return {"short_squeeze": "Не реализовано"}

# --- API endpoints ---
@app.route('/anomalous_volumes')
async def anomalous_volumes():
    ticker = request.args.get('ticker')
    if not ticker:
        logger.warning("Не указан тикер в запросе /anomalous_volumes")
        return jsonify({'error': 'Ticker is required'}), 400
    result = await calculate_anomalous_volumes(ticker)
    return jsonify(result)

@app.route('/anomalous_limits')
async def anomalous_limits():
    ticker = request.args.get('ticker')
    if not ticker:
        logger.warning("Не указан тикер в запросе /anomalous_limits")
        return jsonify({'error': 'Ticker is required'}), 400
    result = await analyze_anomalous_limits(ticker)
    return jsonify(result)

@app.route('/net_flow')
async def net_flow():
    ticker = request.args.get('ticker')
    if not ticker:
        logger.warning("Не указан тикер в запросе /net_flow")
        return jsonify({'error': 'Ticker is required'}), 400
    result = await calculate_net_flow(ticker)
    return jsonify(result)

@app.route('/short_squeeze')
async def short_squeeze():
    ticker = request.args.get('ticker')
    if not ticker:
        logger.warning("Не указан тикер в запросе /short_squeeze")
        return jsonify({'error': 'Ticker is required'}), 400
    result = await calculate_short_squeeze(ticker)
    return jsonify(result)

# Обработчик для Yandex Cloud Functions
def handler(event, context):
    with app.request_context(environ=event['requestContext']):
        return app.full_dispatch_request()
