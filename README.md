# NLP-Powered Restaurant Data Scraper & Analyzer 📊

An end-to-end automated data pipeline built with Python. This project extracts restaurant data and customer reviews from Google Maps, cleans and processes large datasets, and performs Natural Language Processing (NLP) sentiment analysis to derive actionable insights.

## 🚀 Core Architecture & Files

* **`vakum.py` (High-Performance Scraper):** An advanced, memory-efficient web scraper built with **Playwright** and **Pandas**. Features image-blocking for high speed, automated infinite scrolling, and chunk-based Big Data saving mechanisms to bypass memory limits.
* **`restoran_botu.py` (Automated Extraction Bot):** A **Selenium** based automated scraper with a custom **Tkinter GUI**. It filters and extracts data across 81 cities dynamically and exports them into structured CSV files.
* **`nlp_analiz_programi.py` (NLP & Data Engine):** The brain of the operation. Cleans corrupted dataset rows using an Exact Match algorithm, maps external population data (`il_nufus.csv`), and calculates sentiment scores using a custom NLP weighting algorithm (evaluating positive/negative modifiers and context).

## 🛠️ Tech Stack & Skills Demonstrated
* **Languages & Libraries:** Python 3, Playwright, Selenium, Pandas, Tkinter, threading, re (Regex)
* **Data Engineering:** ETL (Extract, Transform, Load) pipelines, Data Cleaning, and CSV/Excel manipulation
* **Asynchronous Execution:** Background threading for non-blocking GUI operations

> **Note:** This repository demonstrates real-world problem solving, memory optimization during web scraping, and basic NLP integration.
