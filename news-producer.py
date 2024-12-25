import json
from typing import List
from datetime import datetime
from alpaca_trade_api import REST
from alpaca_trade_api.common import URL
from alpaca.common import Sort
from kafka import KafkaProducer

from alpaca_config.keys import config
from utils import get_sentiment


def get_producer(brokers: List[str]):
    # Initialize and configure a KafkaProducer for sending messages to Kafka topics.
    producer = KafkaProducer(
        bootstrap_servers=brokers,  # List of brokers to connect to.
        key_serializer=str.encode,  # Serialize message keys to bytes.
        value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serialize message values to JSON format encoded in UTF-8.
    )
    return producer  # Return the configured KafkaProducer instance.


def produce_historical_news(
        redpanda_client: KafkaProducer,
        start_date: str,
        end_date: str,
        symbols: List[str],
        topic: str
    ):
    # Extract API credentials and base URL from the config file.
    key_id = config['key_id']
    secret_key = config['secret_key']
    base_url = config['base_url']

    # Initialize the Alpaca API client using the provided credentials.
    api = REST(key_id=key_id, secret_key=secret_key, base_url=URL(base_url))

    # Loop through each stock symbol to fetch news.
    for symbol in symbols:
        # Retrieve news articles for the given symbol and date range.
        news = api.get_news(
            symbol=symbol,  # The stock symbol to query.
            start=start_date,  # Start date for news filtering.
            end=end_date,  # End date for news filtering.
            limit=5000,  # Maximum number of news articles to retrieve.
            sort=Sort.ASC,  # Sort news in ascending order by time.
            include_content=False,  # Exclude the full content of the article.
        )

        # Process each news article retrieved for the symbol.
        for i, row in enumerate(news):
            article = row._raw  # Access the raw data of the article.

            # Check if any of the specified symbols appear in the article headline.
            should_proceed = any(term in article['headline'] for term in symbols)
            if not should_proceed:  # Skip the article if the symbol is not mentioned.
                continue

            # Convert the article's timestamp to milliseconds and human-readable format.
            timestamp_ms = int(row.created_at.timestamp() * 1000)  # Milliseconds since epoch.
            timestamp = datetime.fromtimestamp(row.created_at.timestamp())  # Human-readable timestamp.

            # Add metadata and process the article for publishing.
            article['timestamp'] = timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Add formatted timestamp.
            article['timestamp_ms'] = timestamp_ms  # Add timestamp in milliseconds.
            article['data_provider'] = 'alpaca'  # Specify the data provider.
            article['sentiment'] = get_sentiment(article['headline'])  # Perform sentiment analysis on the headline.
            article.pop('symbols')  # Remove the original symbols field from the article.
            article['symbol'] = symbol  # Add the current symbol to the article.

            try:
                # Send the article to the specified Kafka topic.
                future = redpanda_client.send(
                    topic=topic,  # Kafka topic name.
                    key=symbol,  # Message key for Kafka partitioning.
                    value=article,  # Serialized article data.
                    timestamp_ms=timestamp_ms  # Message timestamp.
                )

                _ = future.get(timeout=10)  # Wait for the message to be sent.
                print(f'Sent {i+1} articles to {topic}')  # Log success.
            except Exception as e:
                # Log any errors encountered during message sending.
                print(f'Failed to send article: {article}')
                print(e)


if __name__ == '__main__':
    # Produce historical news for the specified symbols and date range.
    produce_historical_news(
        get_producer(config['redpanda_brokers']),  # Create a Kafka producer using configured brokers.
        topic='market-news',  # Kafka topic to send the articles to.
        start_date='2024-01-01',  # Start date for news retrieval.
        end_date='2024-10-30',  # End date for news retrieval.
        symbols=['AAPL', 'Apple']  # List of stock symbols to retrieve news for.
    )
