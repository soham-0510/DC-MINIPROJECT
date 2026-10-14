@echo off
cd /d "%~dp0\.."
title AstroQuiz Arena - Pyro5 Name Server (RMI registry)
python -m Pyro5.nameserver -n 0.0.0.0
pause
