"""
RPC client layer — the Streamlit side of the RMI/RPC story.

`Pyro5.api.Proxy` is the client STUB: calling `proxy.get_room_state(...)`
looks like a local method call, but Pyro5 serializes the arguments, sends
them over TCP to the server's daemon, runs the method on the remote
object and ships the return value back.

Streamlit re-runs scripts on different threads, so before each call the
proxy "claims ownership" for the current thread (a Pyro5 requirement).
"""

from __future__ import annotations

import os
import time

import Pyro5.api
import Pyro5.errors
import streamlit as st

OBJECT_NAME = "astroquiz.server"
DEFAULT_HOST = os.environ.get("ASTRO_SERVER_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("ASTRO_SERVER_PORT", "9100"))
CALL_TIMEOUT = 4.0


def init_connection_state() -> None:
    ss = st.session_state
    ss.setdefault("server_host", DEFAULT_HOST)
    ss.setdefault("server_port", DEFAULT_PORT)
    ss.setdefault("use_ns", False)
    ss.setdefault("ns_host", DEFAULT_HOST)
    ss.setdefault("last_latency_ms", None)


def server_uri() -> str:
    ss = st.session_state
    if ss.use_ns:
        # Look the object up by NAME in the Pyro5 Name Server (the "RMI registry")
        return f"PYRONAME:{OBJECT_NAME}@{ss.ns_host}"
    # Direct URI: object id @ host : port
    return f"PYRO:{OBJECT_NAME}@{ss.server_host}:{int(ss.server_port)}"


def uplink_label() -> str:
    ss = st.session_state
    return f"Name Server @ {ss.ns_host}" if ss.use_ns else f"{ss.server_host}:{int(ss.server_port)}"


def _proxy() -> Pyro5.api.Proxy:
    ss = st.session_state
    uri = server_uri()
    proxy = ss.get("_proxy")
    if proxy is None or ss.get("_proxy_uri") != uri:
        proxy = Pyro5.api.Proxy(uri)
        proxy._pyroTimeout = CALL_TIMEOUT
        ss["_proxy"] = proxy
        ss["_proxy_uri"] = uri
    proxy._pyroClaimOwnership()
    return proxy


def reset() -> None:
    proxy = st.session_state.pop("_proxy", None)
    if proxy is not None:
        try:
            proxy._pyroClaimOwnership()
            proxy._pyroRelease()
        except Exception:
            pass


def call(method: str, *args) -> dict:
    """Invoke a remote method. Always returns a dict with an 'ok' key."""
    for attempt in range(2):
        try:
            t0 = time.perf_counter()
            result = getattr(_proxy(), method)(*args)
            st.session_state.last_latency_ms = (time.perf_counter() - t0) * 1000
            st.session_state.uplink_ok = True
            return result
        except (Pyro5.errors.CommunicationError, Pyro5.errors.NamingError, OSError) as exc:
            reset()
            if attempt == 1:
                st.session_state.uplink_ok = False
                return {
                    "ok": False,
                    "offline": True,
                    "error": f"Can't reach the game server at {uplink_label()}. "
                             f"Check that it's running and the address is right. ({type(exc).__name__})",
                }
    return {"ok": False, "error": "Unknown RPC failure."}
