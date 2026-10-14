@echo off
cd /d "%~dp0\.."
title AstroQuiz Arena - Streamlit Client
streamlit run client\app.py
pause
