import json
from datetime import datetime
from typing import List

from alpaca.data import StockHistoricalDataClient, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from kafka import KafkaProducer

from alpaca_config.keys import config


def get_producer(brokers: List[str]):
    # Initialize and configure a KafkaProducer for sending messages to Kafka topics.
    producer = KafkaProducer(
        bootstrap_servers=brokers,  # List of brokers to connect to.
        key_serializer=str.encode,  # Serialize message keys to bytes.
        value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serialize message values to JSON format encoded in UTF-8.
    )
    return producer  # Return the configured KafkaProducer instance.


def produce_historical_price(
        redpanda_client: KafkaProducer,
        topic: str,
        start_date: str,
        end_date: str,
        symbol: str
):
    # Initialize the Alpaca StockHistoricalDataClient with API credentials.
    api = StockHistoricalDataClient(api_key=config['key_id'], secret_key=config['secret_key'])

    # Parse the start and end dates into datetime objects.
    start_date = datetime.strptime(start_date, '%Y-%m-%d')  # Convert start date string to datetime.
    end_date = datetime.strptime(end_date, '%Y-%m-%d')  # Convert end date string to datetime.

    # Define the granularity of price data (e.g., minute-level data).
    granularity = TimeFrame.Minute

    # Create a request object to fetch historical stock price data.
    request_params = StockBarsRequest(
        symbol_or_symbols=symbol,  # The stock symbol to query.
        timeframe=granularity,  # The granularity of the price data.
        start=start_date,  # The start date for data retrieval.
        end=end_date  # The end date for data retrieval.
    )

    # Fetch historical stock prices as a pandas DataFrame and reset its index.
    prices_df = api.get_stock_bars(request_params).df
    prices_df.reset_index(inplace=True)  # Reset index to convert the DataFrame into flat records.

    # Convert the DataFrame into a list of dictionaries for processing.
    records = json.loads(prices_df.to_json(orient='records'))
    for idx, record in enumerate(records):
        record['provider'] = 'alpaca'  # Add metadata indicating the data provider.

        try:
            # Send each record as a message to the specified Kafka topic.
            future = redpanda_client.send(
                topic=topic,  # Kafka topic name.
                key=record['symbol'],  # Message key for Kafka partitioning.
                value=record,  # Serialized price data record.
                timestamp_ms=record['timestamp']  # Timestamp of the record in milliseconds.
            )

            _ = future.get(timeout=10)  # Wait for the message to be sent successfully.
            print(f'Record sent successfully')  # Log success.
        except Exception as e:
            # Log any errors encountered while sending the message.
            print(f'Error sending message for symbol {symbol}: {e.__class__.__name__} - {e}')


if __name__ == '__main__':
    # Initialize a Kafka producer using configured brokers.
    redpanda_client = get_producer(config['redpanda_brokers'])

    # Produce historical price data for the specified stock symbol and date range.
    produce_historical_price(
        redpanda_client,
        topic='stock-prices',  # Kafka topic to send the price data to.
        start_date='2024-01-01',  # Start date for price data retrieval.
        end_date='2024-10-30',  # End date for price data retrieval.
        symbol='AAPL'  # The stock symbol to retrieve price data for.
    )

    # Close the Kafka producer connection after use.
    redpanda_client.close()
