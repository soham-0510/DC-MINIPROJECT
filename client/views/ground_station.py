"""
Ground Station — a live monitor of the RPC game server.

Great for demos and the viva: it shows the remote object, the rooms it is
hosting, which clients are connected, and every remote method call as it
arrives (method name, caller address, latency).
"""

from __future__ import annotations

import datetime as dt

import plotly.graph_objects as go_
import streamlit as st
import streamlit_shadcn_ui as ui

import rpc
from components import widgets as W

PHASE_LABEL = {"lobby": "🟣 Lobby", "launch": "🚀 Launching", "question": "❓ Question live",
               "reveal": "✨ Revealing", "finished": "🏁 Finished"}
POLL_METHODS = {"get_room_state", "get_server_stats", "ping"}


def _uptime(sec: int) -> str:
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m:02d}m" if h else f"{m}m {s:02d}s"


def render() -> None:
    st.markdown(W.one_line("""<div class="gs-head"><div><h2>Ground Station</h2>
        <div class="section-sub" style="margin:4px 0 0">Live telemetry from the AstroQuiz RPC server.
        Everything below is fetched with one remote call: <span class="mono">get_server_stats()</span>.</div></div></div>"""),
        unsafe_allow_html=True)

    with st.container(key="card_arch"):
        st.markdown(W.one_line(f"""<div class="arch">
          <div class="node"><b>Streamlit clients</b>Each browser tab holds a Pyro5 <span class="mono">Proxy</span> (the stub)</div>
          <div class="wire"></div>
          <div class="node"><b>Pyro5 Daemon</b>Listens on TCP, unpacks the call, dispatches it (the skeleton)</div>
          <div class="wire"></div>
          <div class="node"><b>AstroQuizServer</b>One shared remote object holding every room · <span class="mono">{W.esc(rpc.uplink_label())}</span></div>
        </div>"""), unsafe_allow_html=True)
    st.write("")
    hide_polls = ui.switch("Hide polling calls (get_room_state, ping…)", value=True, key="gs_hide_polls")

    @st.fragment(run_every=1.5)
    def telemetry():
        res = rpc.call("get_server_stats")
        if not res.get("ok"):
            st.markdown(W.alert(res.get("error", "No telemetry.")), unsafe_allow_html=True)
            return
        m = st.columns(4)
        metrics = [
            (_uptime(res["uptime_s"]), "server uptime"),
            (f"{res['total_calls']:,}", "remote calls served"),
            (str(res["active_clients"]), "client connections (10 s)"),
            (f"{len(res['rooms'])} · {res['players_online']}", "missions · astronauts online"),
        ]
        for col, (value, label) in zip(m, metrics):
            col.markdown(f'<div class="metric"><b>{W.esc(value)}</b><span>{W.esc(label)}</span></div>',
                         unsafe_allow_html=True)
        st.write("")

        left, right = st.columns([1.35, 1], gap="large")
        with left:
            with st.container(key="card_log"):
                st.markdown(W.section("Live RPC log", "Newest first · method · caller · latency"),
                            unsafe_allow_html=True)
                log = list(reversed(res.get("events", []) if hide_polls else res["log"]))
                lines = []
                for e in log[:60]:
                    ts = dt.datetime.fromtimestamp(e["t"]).strftime("%H:%M:%S")
                    cls = "m" + (" poll" if e["method"] in POLL_METHODS else "") + ("" if e["ok"] else " err")
                    fresh = " new" if res["server_time"] - e["t"] < 1.6 else ""
                    lines.append(
                        f'<div class="ln{fresh}"><span class="t">{ts}</span><span class="c">{W.esc(e["client"])}</span>'
                        f'<span class="{cls}">{W.esc(e["method"])}(<span style="color:var(--muted)">{W.esc(e["args"])}</span>)</span>'
                        f'<span class="ms">{e["ms"]:.2f} ms</span></div>'
                    )
                body = "".join(lines) or '<div class="t">No calls yet — host or join a mission to see traffic.</div>'
                st.markdown(f'<div class="log">{body}</div>', unsafe_allow_html=True)
        with right:
            with st.container(key="card_rooms"):
                st.markdown(W.section("Active missions", "Rooms held in the remote object's memory"),
                            unsafe_allow_html=True)
                if not res["rooms"]:
                    st.markdown('<div class="section-sub">No missions in flight. Host one from the launch pad.</div>',
                                unsafe_allow_html=True)
                for r in res["rooms"]:
                    st.markdown(W.one_line(f"""<div class="crew-card" style="animation:none;margin-bottom:8px">
                        <div class="av">{W.esc(r['icon'])}</div><div style="flex:1">
                        <div class="nm"><span class="mono">{W.esc(r['code'])}</span> · Sector {W.esc(r['sector'])}</div>
                        <span class="tag">{PHASE_LABEL.get(r['phase'], r['phase'])} · Q {W.esc(r['question'])} ·
                        {r['online']}/{r['players']} online</span></div></div>"""), unsafe_allow_html=True)
            with st.container(key="card_calls"):
                st.markdown(W.section("Calls by method"), unsafe_allow_html=True)
                calls = sorted(res["calls_by_method"].items(), key=lambda kv: kv[1])
                if calls:
                    fig = go_.Figure(go_.Bar(
                        x=[v for _, v in calls], y=[k for k, _ in calls], orientation="h",
                        marker=dict(color=["#334155" if k in POLL_METHODS else "#8B5CF6" for k, _ in calls]),
                        text=[f"{v:,}" for _, v in calls], textposition="outside", cliponaxis=False,
                    ))
                    fig.update_layout(
                        height=40 + 34 * len(calls), margin=dict(l=0, r=40, t=0, b=0),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="ui-monospace, Menlo, monospace", color="#C7CCEB", size=12),
                        xaxis=dict(visible=False), yaxis=dict(gridcolor="rgba(0,0,0,0)"), bargap=0.35,
                    )
                    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False, "staticPlot": True},
                                    key="calls_chart")

    telemetry()
