@echo off
cd /d "%~dp0\.."
echo Starting the Pyro5 Name Server, the RPC game server and the Streamlit client...
start "Name Server" cmd /k python -m Pyro5.nameserver -n 0.0.0.0
timeout /t 2 /nobreak >nul
start "Game Server" cmd /k python server\game_server.py --ns
timeout /t 2 /nobreak >nul
start "Streamlit Client" cmd /k streamlit run client\app.py
