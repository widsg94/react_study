@echo off
REM Navigate to backend directory and run the Python scripts
cd backend
start python ocr.py
start python translator.py
start python hiragana.py

REM Navigate to the translator directory to run npm start
cd ../translator
npm start
