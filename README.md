# Algorithmic Trading Using Flink

This repository showcases the implementation of a real-time algorithmic trading system. The project integrates advanced tools and technologies to automate trading actions based on real-time market data and sentiment analysis.

---

## 📚 Project Overview

Algorithmic trading is a cornerstone of modern financial markets, allowing traders to make data-driven, real-time decisions at scale. This project focuses on creating a robust and scalable trading system tailored for Apple stock. Key features include:

- Integration of real-time and historical data
- High-performance data streaming using Redpanda
- Data transformation via Apache Flink
- Deployment on AWS EC2 for cloud scalability
- Real-time trade notifications using Slack

---

## 🔠 Objectives

1. Develop a structured data pipeline for real-time stock trade execution.
2. Automate buy and sell actions leveraging:
   - Technical indicators (e.g., SMA20, SMA50)
   - Sentiment analysis of financial news
3. Ensure scalability and reliability through cloud deployment.

---

## 🛠️ Tools and Technologies

- **Redpanda**: High-throughput, low-latency data streaming
- **Apache Flink SQL**: Efficient data processing and transformation
- **NLTK**: Sentiment analysis for news headlines
- **Slack API**: Real-time trade notifications
- **Docker**: Containerization for portability
- **AWS EC2**: Cloud hosting for scalability

---

## 📊 Strategies Implemented

1. **All-Weather Strategy**: Diversifies investments across asset classes to minimize risk.
2. **Golden Cross Strategy**: Uses SMA50 and SMA200 crossovers for trading signals.
3. **Momentum Strategy**: Capitalizes on price momentum to make trading decisions.

---

## 💡 Data Pipeline Design

### Data Ingestion
- Fetches both real-time and historical data via APIs for:
  - Stock prices
  - News headlines
- Streams data through Redpanda for processing.

### Data Transformation
- Calculates technical indicators (e.g., SMA20, SMA50).
- Conducts sentiment analysis of news headlines (scores range from -1 to 1).
- Implements trading strategies:
  - **Pullback Condition**: Generates a buy signal based on defined criteria.
  - **Breakout Condition**: Generates a sell signal based on predefined conditions.

### Trade Execution and Notification
- Automates buy/sell actions using SQL-based conditions.
- Sends real-time Slack notifications including:
  - Stock symbol
  - Action (Buy/Sell)
  - Timestamp

---

## 📺 Deployment

- **Containerization**: Fully containerized application using Docker for portability.
- **Cloud Deployment**: Hosted on AWS EC2 for scalable and efficient management.

---

## 📊 Results

- Achieved seamless integration of automated trade execution and notifications.
- Observed profitability using the SMA crossover strategy combined with sentiment analysis.
- Delivered actionable real-time insights via Slack notifications.

