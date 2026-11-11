# Ultimate CSV Cleaner & Analyzer

A Streamlit app that profiles, cleans and visualizes CSV files, with an optional Gemini AI powered variant.

## What it does

- **Upload** any CSV, with selectable encoding
- **Data profile** - row and column counts, missing values, exact duplicates, data types and a missing-by-column breakdown
- **Smart cleaning options** (pick any combination):
  - Standardize text (trim and title case)
  - Fix common email typos (for example gamil.com -> gmail.com)
  - Fill missing gender from the same name's most common value
  - Fill missing age from the name-group median
  - Remove exact duplicates
- **Visualizations** - histogram, box plot and correlation heatmap for numeric columns
- **Download** the cleaned CSV, or try it out with the built-in sample data

## Variants

- `app.py` - the main cleaner and analyzer
- `index.py` - CSV cleaning assisted by Google's Gemini model (needs a `GEMINI_API_KEY` environment variable)
- `hello.py` - a small utility that lists the Gemini models available to your API key

## Tech stack

Python, Streamlit, pandas, numpy, seaborn, matplotlib, google-generativeai

## Getting started

```bash
pip install -r requirements.txt
streamlit run app.py
```

For the Gemini variant, set `GEMINI_API_KEY` first, then run `streamlit run index.py`.
