@echo off
echo Installing dependencies...
pip install -r requirements.txt --quiet
echo.
echo Starting Stock Notifier...
streamlit run app.py
pause
