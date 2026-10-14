#!/usr/bin/env bash
# Starts the Name Server, the RPC game server and the Streamlit client. Ctrl+C stops everything.
cd "$(dirname "$0")/.."
trap 'kill 0' EXIT
python3 -m Pyro5.nameserver -n 0.0.0.0 &
sleep 2
python3 server/game_server.py --ns &
sleep 2
streamlit run client/app.py
