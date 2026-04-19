# Fundamental-health-screener
A Python-based stock screener that fetches live financial statements via yFinance, computes fundamental ratios (P/E, D/E, ROE, Current Ratio), and ranks equities within a sector using a customisable weighted scoring system. Built with a Streamlit frontend and a decoupled backend module.


Backend.py - This file contains all the logic. No UI code here at all.

What it does: 

    Stores the list of stocks for each sector (Tech, Finance, Energy etc.)
    Stores the 4 preset investor profiles (Conservative, Growth, Value, Balanced)
    Fetches live financial data from Yahoo Finance using yfinance
    Calculates 4 ratios for each stock:

          P/E ratio
          D/E ratio 
          ROE 
          Current Ratio


    Ranks all stocks in a sector based on those ratios
    Applies your custom weights so ratios you care about matter more


Dependencies

    yfinance — fetches live financial statements
    pandas — handles the data as tables
    numpy — used for number calculations


Notes

    If a stock is missing data on Yahoo Finance, it gets silently skipped
    Weights don't need to add up to 100 — they get auto-normalised
    This file has zero Streamlit code in it — it's pure Python logic



Frontend.py - This file contains all the UI. No data fetching or calculation logic here at all. The UI design has been assisted by claude.ai

What it does

    Shows a sidebar where the user can:
    
        Pick a sector (Tech, Finance, Energy etc.)
        Pick an investor profile (or go fully custom)
        Adjust sliders to set how much each ratio matters
    
    
    Shows all the tickers in the selected sector as badges
    When the user hits Run Screener, it calls the backend and displays results
    Shows the Top 3 stocks as medal cards (🥇🥈🥉)
    Shows the full ranked table with a score bar for every stock
    Has an expandable section explaining what each ratio means

Dependencies

    streamlit — builds the entire UI in Python, no HTML or JavaScript needed

How to run locally

    streamlit run fontend.py
    Then open http://localhost:8501 in your browser


