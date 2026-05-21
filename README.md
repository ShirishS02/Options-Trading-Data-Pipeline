# Options Trading Data Pipeline

A scalable, containerized data engineering pipeline for ingesting, processing, and analyzing options trading data using **Apache Spark**, **PostgreSQL**, and **Docker**.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Pipeline](#running-the-pipeline)
- [Configuration](#configuration)
- [Modules](#modules)
- [Visualizations](#visualizations)
- [License](#license)

---

## Overview

The **Options Trading Data Pipeline** is designed to process and analyze options market data at scale. It automates the flow from raw data ingestion through transformation, storage, and visualization — enabling insights into options trading patterns, pricing, and potential arbitrage opportunities.

---

## Architecture

```
Raw Data (CSV/API)
        │
        ▼
  ┌─────────────┐
  │  Spark Jobs  │  ← PySpark transformations & analysis
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  PostgreSQL  │  ← Structured storage (arbitrage_db)
  └──────┬──────┘
         │
         ▼
  ┌──────────────┐
  │Visualizations│  ← Charts, dashboards, reports
  └──────────────┘
```

All services are orchestrated via **Docker Compose**.

---

## Project Structure

```
Options-Trading-Data-Pipeline/
├── data/                    # Raw and processed data files
├── spark_jobs/              # PySpark job scripts
├── sql/                     # SQL scripts for schema & queries
├── visualizations/          # Visualization outputs and scripts
└── docker-compose.yml       # Docker service definitions
```

---

## Tech Stack

| Component       | Technology            |
|----------------|-----------------------|
| Data Processing | Apache Spark 3.5.0    |
| Database        | PostgreSQL 15         |
| Orchestration   | Docker Compose        |
| Language        | Python (PySpark)      |
| Storage         | Local volume mounts   |

---

## Getting Started

### Prerequisites

Make sure you have the following installed:

- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- Python 3.8+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/ShirishS02/Options-Trading-Data-Pipeline.git
cd Options-Trading-Data-Pipeline
```

### Running the Pipeline

```bash
# Start all services (PostgreSQL + Spark)
docker-compose up -d

# Verify services are running
docker ps
```

Once the containers are up:

- **PostgreSQL** is available at `localhost:5433`
  - User: `admin`
  - Password: `admin123`
  - Database: `arbitrage_db`

- **Spark** container mounts `spark_jobs/` at `/opt/spark_jobs` and `data/` at `/opt/data`

To run a Spark job manually:

```bash
docker exec -it arbitrage_spark spark-submit /opt/spark_jobs/<your_job>.py
```

To stop all services:

```bash
docker-compose down
```

---

## Configuration

The `docker-compose.yml` configures two core services:

**PostgreSQL**
```yaml
POSTGRES_USER: your_user
POSTGRES_PASSWORD: your_password
POSTGRES_DB: your_db
Port: 5433 (host) → 5432 (container)
```

> Set these values in a `.env` file (never commit it). Add `.env` to your `.gitignore`.

**Apache Spark 3.5.0**
- Mounts `./spark_jobs` → `/opt/spark_jobs`
- Mounts `./data` → `/opt/data`
- Depends on PostgreSQL being healthy

---

## Modules

### `spark_jobs/`
PySpark scripts that handle data transformation and analysis tasks such as options pricing calculations, spread analysis, and arbitrage detection.

### `sql/`
SQL scripts for:
- Database schema creation
- Analytical queries on options data
- Aggregations and reporting views

### `data/`
Stores input CSV files or fetched market data used as the source for Spark jobs.

### `visualizations/`
Output charts and scripts for visualizing processed options data — including price trends, volatility surfaces, and P&L analysis.

---

## Visualizations

The `visualizations/` folder contains generated plots and dashboards derived from the pipeline output. These can be used for:

- Options chain analysis
- Implied volatility trends
- Arbitrage opportunity mapping

---

## License

This project is open source. Feel free to use and adapt it for your own data engineering projects.

---

> Built with ❤️ by [ShirishS02](https://github.com/ShirishS02)
