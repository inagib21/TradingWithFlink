import json
from datetime import datetime
from typing import List

from alpaca.data import StockHistoricalDataClient, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from kafka import KafkaProducer

from alpaca_config.keys import config

def get_producer(brokers: List[str]):
    producer = KafkaProducer(
        bootstrap_servers = brokers,
        key_serializer = str.encode,
        value_serializer =lambda v: json.dumps(v). enccode('utf-8')
    )
    return producer
def  produce_historical_price(
        redpanda_client: KafkaProducer,
        topic: str,
        start_date: str,
        end_date:str,
        symbol: List[str]
):
    api = StockHistoricalDataClient(api_key = config['key_id'], secret_key=config['secret_key'])
    start_date = datetime.strptime(start_date, _format:'%Y-%m-%d')
    end_date = datetime.strptime(end_date, _format:'%Y-%m-%d')
    granularity = TimeFrame.Minute
if __name__ == '__main__':
    redpanda_client = get_producer(config['redpanda_brokers']),
    produce_historical_price(
        redpanda_client,
        topic= 'stock-prices',
        start_date='2024-01-01',
        end_date='2024-12-23',
        symbol='AAPL'
    )

    redpanda_client.close()