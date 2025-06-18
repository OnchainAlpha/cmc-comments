@echo off
title Crypto Analysis Monitor

cd /d C:\Users\oncha\Downloads\AutoCrawler\autocrypto_social_bot

:loop
echo.
echo Starting Crypto Analysis Monitor...
echo Press Ctrl+C to stop
echo.

python C:\Users\oncha\Downloads\AutoCrawler\autocrypto_social_bot\scripts\continuous_monitor.py

echo.
echo Monitor stopped or crashed. Restarting in 5 minutes...
timeout /t 300
goto loop 