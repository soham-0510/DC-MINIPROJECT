@echo off
cd /d "%~dp0\.."
title AstroQuiz Arena - RPC Game Server
python server\game_server.py %*
pause
