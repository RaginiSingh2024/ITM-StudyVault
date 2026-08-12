"""
Discord Sharding Simulator — SaaS Dashboard UI
Run: streamlit run ui/app.py
"""

import streamlit as st
import time, random, os, sys, hashlib, pandas as pd
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from day5_shards import Shard, ShardManager
from day8_hash_sharding import HashShardRouter
from day10_cross_shard import CrossShardQueryEngine

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Discord Sharding Simulator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global reset ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1221 40%, #0a1628 100%) !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1221 0%, #111827 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.2) !important;
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* ── Remove default padding ── */
.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }

/* ── Hero header ── */
.hero-wrap {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(168,85,247,0.1), rgba(59,130,246,0.1));
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 28px;
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
}
.hero-wrap::before {
    content:'';
    position:absolute; top:-40px; right:-40px;
    width:180px; height:180px;
    background: radial-gradient(circle, rgba(168,85,247,0.25), transparent 70%);
    border-radius:50%;
}
.hero-title {
    font-size: 2.4rem; font-weight: 800; margin: 0;
    background: linear-gradient(135deg, #818cf8, #a78bfa, #38bdf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}
.hero-sub { color: #94a3b8; font-size: 14px; margin-top: 6px; font-weight: 400; }
.hero-badges { display:flex; gap:8px; margin-top:14px; flex-wrap:wrap; }
.badge {
    font-size:11px; font-weight:600; padding:4px 10px; border-radius:20px;
    letter-spacing:.4px;
}
.badge-purple { background:rgba(139,92,246,.2); color:#a78bfa; border:1px solid rgba(139,92,246,.3); }
.badge-blue   { background:rgba(59,130,246,.2);  color:#60a5fa; border:1px solid rgba(59,130,246,.3); }
.badge-green  { background:rgba(16,185,129,.2);  color:#34d399; border:1px solid rgba(16,185,129,.3); }
.badge-orange { background:rgba(245,158,11,.2);  color:#fbbf24; border:1px solid rgba(245,158,11,.3); }

/* ── Section headers ── */
.section-title {
    font-size:13px; font-weight:700; text-transform:uppercase;
    letter-spacing:1.2px; color:#6366f1; margin:0 0 14px 2px;
    display:flex; align-items:center; gap:8px;
}
.section-title::after {
    content:''; flex:1; height:1px;
    background:linear-gradient(90deg,rgba(99,102,241,.4),transparent);
}

/* ── Glass metric card ── */
.metric-glass {
    background: linear-gradient(135deg,rgba(255,255,255,.04),rgba(255,255,255,.01));
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 16px;
    padding: 20px 22px;
    backdrop-filter: blur(20px);
    transition: transform .2s, border-color .2s, box-shadow .2s;
    position: relative;
    overflow: hidden;
}
.metric-glass:hover { transform:translateY(-3px); border-color:rgba(99,102,241,.4); box-shadow:0 8px 32px rgba(99,102,241,.15); }
.metric-glass::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    border-radius:16px 16px 0 0;
}
.mg-purple::before { background:linear-gradient(90deg,#6366f1,#8b5cf6); }
.mg-blue::before   { background:linear-gradient(90deg,#3b82f6,#06b6d4); }
.mg-green::before  { background:linear-gradient(90deg,#10b981,#34d399); }
.mg-red::before    { background:linear-gradient(90deg,#ef4444,#f97316); }
.mg-yellow::before { background:linear-gradient(90deg,#f59e0b,#fbbf24); }

.m-icon  { font-size:22px; margin-bottom:8px; }
.m-label { font-size:11px; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:.6px; }
.m-value { font-size:32px; font-weight:800; color:#f1f5f9; margin:4px 0; line-height:1; }
.m-sub   { font-size:12px; color:#475569; margin-top:4px; }
.m-sub-ok   { color:#34d399; }
.m-sub-warn { color:#fbbf24; }
.m-sub-err  { color:#f87171; }

/* ── Shard card ── */
.shard-card {
    background: linear-gradient(135deg,rgba(255,255,255,.035),rgba(255,255,255,.01));
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 12px;
    transition: all .25s;
    position: relative;
    overflow: hidden;
}
.shard-card:hover { border-color: rgba(99,102,241,.35); transform:translateX(3px); }
.sc-alive  { border-left: 3px solid #10b981; }
.sc-dead   { border-left: 3px solid #ef4444; opacity:.65; }
.sc-hot    { border-left: 3px solid #f59e0b; }
.sc-crit   { border-left: 3px solid #ef4444; }

.sc-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
.sc-name   { font-size:15px; font-weight:700; color:#e2e8f0; }
.sc-pill   { font-size:10px; font-weight:700; padding:3px 10px; border-radius:20px; }
.pill-alive { background:rgba(16,185,129,.15); color:#34d399; border:1px solid rgba(16,185,129,.3); }
.pill-dead  { background:rgba(239,68,68,.15);  color:#f87171; border:1px solid rgba(239,68,68,.3); }
.pill-hot   { background:rgba(245,158,11,.15); color:#fbbf24; border:1px solid rgba(245,158,11,.3); }
.pill-crit  { background:rgba(239,68,68,.2);   color:#f87171; border:1px solid rgba(239,68,68,.4); }

.sc-stats { display:flex; gap:16px; margin-bottom:10px; }
.sc-stat  { font-size:12px; color:#64748b; }
.sc-stat span { color:#cbd5e1; font-weight:600; }

.bar-bg   { background:rgba(255,255,255,.06); border-radius:6px; height:6px; margin-bottom:6px; overflow:hidden; }
.bar-fill { height:6px; border-radius:6px; transition:width .6s ease; }
.bf-ok   { background:linear-gradient(90deg,#10b981,#34d399); }
.bf-warn { background:linear-gradient(90deg,#f59e0b,#fbbf24); }
.bf-hot  { background:linear-gradient(90deg,#ef4444,#f97316); }
.sc-pct  { font-size:11px; color:#475569; }

.sc-channels { margin-top:8px; display:flex; flex-wrap:wrap; gap:5px; }
.ch-tag { font-size:10px; padding:2px 8px; border-radius:10px; background:rgba(99,102,241,.12); color:#818cf8; border:1px solid rgba(99,102,241,.2); }

/* ── Message feed ── */
.feed-item {
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.06);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: background .2s;
    font-size: 13px;
}
.feed-item:hover { background: rgba(99,102,241,.08); }
.shard-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.dot-0 { background:#6366f1; box-shadow:0 0 6px #6366f1; }
.dot-1 { background:#10b981; box-shadow:0 0 6px #10b981; }
.dot-2 { background:#f59e0b; box-shadow:0 0 6px #f59e0b; }
.feed-user { color:#818cf8; font-weight:600; flex-shrink:0; }
.feed-ch   { color:#64748b; font-size:11px; flex-shrink:0; }
.feed-msg  { color:#94a3b8; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.feed-time { color:#334155; font-size:10px; flex-shrink:0; }

/* ── Log box ── */
.log-box {
    background: #050810;
    border: 1px solid rgba(99,102,241,.2);
    border-radius: 12px;
    padding: 14px 16px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    max-height: 220px;
    overflow-y: auto;
    line-height: 1.7;
}
.log-ok   { color:#34d399; }
.log-info { color:#60a5fa; }
.log-warn { color:#fbbf24; }
.log-err  { color:#f87171; }

/* ── Alert banners ── */
.alert-critical {
    background: linear-gradient(135deg,rgba(239,68,68,.15),rgba(249,115,22,.1));
    border: 1px solid rgba(239,68,68,.4);
    border-radius: 12px;
    padding: 14px 18px;
    color: #f87171;
    font-weight: 600;
    font-size: 14px;
    margin: 8px 0;
    animation: pulse-red 2s infinite;
}
.alert-warn {
    background: linear-gradient(135deg,rgba(245,158,11,.12),rgba(251,191,36,.08));
    border: 1px solid rgba(245,158,11,.35);
    border-radius: 12px;
    padding: 14px 18px;
    color: #fbbf24;
    font-weight: 600;
    font-size: 14px;
    margin: 8px 0;
}
.alert-ok {
    background: linear-gradient(135deg,rgba(16,185,129,.12),rgba(52,211,153,.08));
    border: 1px solid rgba(16,185,129,.35);
    border-radius: 12px;
    padding: 14px 18px;
    color: #34d399;
    font-weight: 600;
    font-size: 14px;
    margin: 8px 0;
}
@keyframes pulse-red {
    0%,100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
    50%      { box-shadow: 0 0 12px 4px rgba(239,68,68,.2); }
}

/* ── Simulation buttons ── */
.stButton > button {
    background: linear-gradient(135deg,rgba(99,102,241,.15),rgba(139,92,246,.1)) !important;
    border: 1px solid rgba(99,102,241,.3) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: all .2s !important;
    padding: 10px 16px !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg,rgba(99,102,241,.3),rgba(139,92,246,.2)) !important;
    border-color: rgba(99,102,241,.6) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,.25) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Form fields ── */
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stSlider { 
    background: rgba(255,255,255,.04) !important;
    border: 1px solid rgba(255,255,255,.1) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}
.stTextInput label, .stSelectbox label, .stSlider label {
    color: #94a3b8 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: .5px !important;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,.06) !important; margin: 20px 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:rgba(99,102,241,.4); border-radius:4px; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────
def init():
    if "mgr" not in st.session_state:
        st.session_state.mgr = ShardManager(num_shards=3)
    if "router" not in st.session_state:
        st.session_state.router = HashShardRouter(st.session_state.mgr, key_type="channel_id")
    if "qe" not in st.session_state:
        st.session_state.qe = CrossShardQueryEngine(st.session_state.mgr, st.session_state.router)
    if "feed" not in st.session_state:
        st.session_state.feed = []
    if "syslog" not in st.session_state:
        st.session_state.syslog = [{"t": time.strftime("%H:%M:%S"), "lvl": "info", "m": "System initialised · 3 shards online"}]
    if "dropped" not in st.session_state:
        st.session_state.dropped = 0
    if "strategy" not in st.session_state:
        st.session_state.strategy = "channel_id"

init()

CHANNELS  = ["general","memes","gaming","music","random","announcements"]
USERS_PRE = ["alice","bob","charlie","spam_king","streamer_fan","mod_zero"]
DOT_CLS   = ["dot-0","dot-1","dot-2"]
SC_CLS    = ["sc-crit" if (s.write_count/s.max_messages)>0.8 else
             "sc-hot"  if (s.write_count/s.max_messages)>0.5 else
             "sc-dead" if not s.is_alive else "sc-alive"
             for s in st.session_state.mgr.shards.values()]


def add_log(lvl, msg):
    st.session_state.syslog.append({"t": time.strftime("%H:%M:%S"), "lvl": lvl, "m": msg})
    st.session_state.syslog = st.session_state.syslog[-60:]

def pill(shard):
    load = shard.write_count / shard.max_messages
    if not shard.is_alive:         return "pill-dead",  "💀 OFFLINE"
    elif load > 0.80:              return "pill-crit",  "🔥 CRITICAL"
    elif load > 0.50:              return "pill-hot",   "⚠️ HOT"
    else:                          return "pill-alive", "✅ HEALTHY"

def bar_cls(pct):
    return "bf-hot" if pct > 75 else ("bf-warn" if pct > 40 else "bf-ok")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("### ⚡ Sharding Config")
    st.markdown("---")

    strategy_label = st.selectbox(
        "Routing Strategy",
        ["channel_id — channel-based", "user_id — user-based", "composite — hash blend"],
        index=0,
    )
    new_strategy = strategy_label.split(" ")[0]
    if new_strategy != st.session_state.strategy:
        st.session_state.strategy = new_strategy
        st.session_state.router = HashShardRouter(st.session_state.mgr, key_type=new_strategy)
        st.session_state.qe = CrossShardQueryEngine(st.session_state.mgr, st.session_state.router)
        add_log("info", f"Strategy → {new_strategy}")

    info = {
        "channel_id": "✅ Fast channel reads\n⚠️ Viral channel = hotspot",
        "user_id":    "✅ Easy user history\n⚠️ Active user = hotspot",
        "composite":  "✅ Most balanced\n⚠️ No consistency guarantee",
    }
    st.info(info[st.session_state.strategy])

    st.markdown("---")
    st.markdown("### 🖥️ Shard Controls")

    for i, shard in st.session_state.mgr.shards.items():
        c1, c2 = st.columns([3,2])
        pclass, ptext = pill(shard)
        c1.markdown(f"**Shard-{i}** &nbsp; <span style='font-size:11px;color:#94a3b8'>{ptext}</span>", unsafe_allow_html=True)
        if shard.is_alive:
            if c2.button("Kill", key=f"k{i}", use_container_width=True):
                shard.kill()
                add_log("err", f"Shard-{i} KILLED — channels on it are now DARK")
                st.rerun()
        else:
            if c2.button("Revive", key=f"r{i}", use_container_width=True):
                shard.revive()
                add_log("ok", f"Shard-{i} revived and back online ✅")
                st.rerun()

    st.markdown("---")
    if st.button("🔄 Full Reset", use_container_width=True):
        for key in ["mgr","router","qe","feed","syslog","dropped","strategy"]:
            if key in st.session_state: del st.session_state[key]
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='font-size:11px;color:#334155;text-align:center;line-height:1.8'>
    ⚡ Discord Sharding Simulator<br>
    System Design · 10-Day Course<br>
    <span style='color:#6366f1'>localhost:8501</span>
    </div>
    """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HERO HEADER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
alive_count  = len(st.session_state.mgr.get_alive_shards())
total_msgs   = sum(s.write_count for s in st.session_state.mgr.shards.values())
overloaded   = sum(1 for s in st.session_state.mgr.shards.values() if s.write_count/s.max_messages > 0.5 and s.is_alive)
dropped_msgs = st.session_state.dropped

st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-title">🚀 Discord Sharding Simulator</div>
  <div class="hero-sub">Visualizing how systems break at scale · Watch shards overload, fail, and recover in real time</div>
  <div class="hero-badges">
    <span class="badge badge-purple">⚡ {st.session_state.strategy} routing</span>
    <span class="badge badge-{'green' if alive_count==3 else 'orange'}">{alive_count}/3 shards alive</span>
    <span class="badge badge-blue">{total_msgs:,} messages stored</span>
    {'<span class="badge badge-orange">⚠️ ' + str(overloaded) + ' shard(s) hot</span>' if overloaded else '<span class="badge badge-green">✅ System balanced</span>'}
  </div>
</div>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 1 — SYSTEM OVERVIEW (metric cards)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="section-title">📊 &nbsp; System Overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    (c1, "mg-purple", "💬", "TOTAL MESSAGES", f"{total_msgs:,}", "Across all shards", "ok"),
    (c2, "mg-blue",   "🖥️", "LIVE SHARDS",    f"{alive_count}/3",
        "🟢 All healthy" if alive_count==3 else "🔴 Degraded!",
        "ok" if alive_count==3 else "err"),
    (c3, "mg-yellow",  "🔥", "OVERLOADED",    str(overloaded),
        "No hotspots" if overloaded==0 else f"{overloaded} shard(s) hot",
        "ok" if overloaded==0 else "warn"),
    (c4, "mg-red",    "❌", "DROPPED MSGS",   f"{dropped_msgs:,}",
        "✅ No loss" if dropped_msgs==0 else "⚠️ Messages lost",
        "ok" if dropped_msgs==0 else "err"),
    (c5, "mg-green",  "📡", "ROUTING KEY",    st.session_state.strategy.upper().replace("_","·")[:8], "Active strategy","ok"),
]
for col, mg, icon, label, val, sub, sub_cls in metrics:
    with col:
        st.markdown(f"""
        <div class="metric-glass {mg}">
          <div class="m-icon">{icon}</div>
          <div class="m-label">{label}</div>
          <div class="m-value">{val}</div>
          <div class="m-sub m-sub-{sub_cls}">{sub}</div>
        </div>
        """, unsafe_allow_html=True)


# ── Global alerts ────────────────────────
for i, shard in st.session_state.mgr.shards.items():
    load_pct = (shard.write_count / shard.max_messages) * 100
    if not shard.is_alive:
        st.markdown(f'<div class="alert-critical">💀 Shard-{i} is OFFLINE — All traffic to its channels is being dropped. Kill/Revive in the sidebar to manage.</div>', unsafe_allow_html=True)
    elif load_pct > 75:
        st.markdown(f'<div class="alert-critical">🔥 ⚠️ System Imbalance Detected! — Shard-{i} is at {load_pct:.0f}% capacity. Performance will degrade immediately.</div>', unsafe_allow_html=True)
    elif load_pct > 45:
        st.markdown(f'<div class="alert-warn">⚠️  Shard-{i} is warming up ({load_pct:.0f}% load). Consider distributing traffic.</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 2 — SHARD STATUS + ANALYTICS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
left, right = st.columns([1.1, 1])

with left:
    st.markdown('<div class="section-title">🖥️ &nbsp; Shard Cluster Status</div>', unsafe_allow_html=True)
    for i, shard in st.session_state.mgr.shards.items():
        load_pct = (shard.write_count / shard.max_messages) * 100
        pclass, ptext = pill(shard)
        sc = "sc-dead" if not shard.is_alive else ("sc-crit" if load_pct>80 else ("sc-hot" if load_pct>45 else "sc-alive"))
        b  = bar_cls(load_pct)
        chs= list(shard.channel_index.keys())
        ch_html = "".join(f'<span class="ch-tag">#{c}</span>' for c in chs[:6])
        ch_more = f'<span class="ch-tag">+{len(chs)-6}</span>' if len(chs)>6 else ""

        st.markdown(f"""
        <div class="shard-card {sc}">
          <div class="sc-header">
            <span class="sc-name">🖥️&nbsp; Shard-{i}</span>
            <span class="sc-pill {pclass}">{ptext}</span>
          </div>
          <div class="sc-stats">
            <div class="sc-stat">Msgs&nbsp;<span>{shard.write_count:,}</span></div>
            <div class="sc-stat">Channels&nbsp;<span>{len(shard.channel_index)}</span></div>
            <div class="sc-stat">Reads&nbsp;<span>{shard.read_count:,}</span></div>
            <div class="sc-stat">Users&nbsp;<span>{len(shard.user_index)}</span></div>
          </div>
          <div class="bar-bg"><div class="bar-fill {b}" style="width:{min(load_pct,100):.1f}%"></div></div>
          <div class="sc-pct">Load: {load_pct:.1f}% / 100%</div>
          {('<div class="sc-channels">' + ch_html + ch_more + '</div>') if chs else ''}
        </div>
        """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-title">📈 &nbsp; Shard Load Analytics</div>', unsafe_allow_html=True)

    # Build chart data
    chart_df = pd.DataFrame({
        "Shard": [f"Shard-{i}" for i in range(3)],
        "Messages": [s.write_count for s in st.session_state.mgr.shards.values()],
    }).set_index("Shard")

    st.bar_chart(chart_df, color="#6366f1", height=220)

    # Per-channel distribution
    st.markdown('<div class="section-title" style="margin-top:16px">📡 &nbsp; Channel Distribution</div>', unsafe_allow_html=True)
    ch_counts = defaultdict(int)
    for s in st.session_state.mgr.shards.values():
        for ch, msgs in s.channel_index.items():
            ch_counts[ch] += len(msgs)
    if ch_counts:
        ch_df = pd.DataFrame({"Messages": dict(sorted(ch_counts.items(), key=lambda x:-x[1]))})
        st.bar_chart(ch_df, color="#8b5cf6", height=180)
    else:
        st.markdown('<div style="color:#334155;font-size:13px;text-align:center;padding:40px 0">Send messages to see channel distribution</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 3 — SEND MESSAGE + SIMULATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
msg_col, sim_col = st.columns([1, 1.1])

with msg_col:
    st.markdown('<div class="section-title">💬 &nbsp; Send Message</div>', unsafe_allow_html=True)

    uid  = st.selectbox("👤 User ID",    options=USERS_PRE + [f"user_{i}" for i in range(10)], key="uid")
    chan = st.selectbox("📢 Channel",    options=CHANNELS, key="chan")
    text = st.text_input("✉️ Message",  placeholder="Type your message here...", value="Hello Discord! 👋", key="msg_text")

    b1, b2, b3 = st.columns(3)
    send_one  = b1.button("📤 Send",         use_container_width=True)
    send_spam = b2.button("🔥 Spam ×100",    use_container_width=True)
    send_burst= b3.button("💥 Burst ×1000",  use_container_width=True)

    count = 1000 if send_burst else (100 if send_spam else (1 if send_one else 0))
    if count > 0:
        with st.spinner(f"Sending {count} message(s) via **{st.session_state.strategy}** routing..."):
            ok = fail = 0
            for j in range(count):
                content = text if count == 1 else f"{'SPAM' if count==100 else 'BURST'}_{j}: {random.choice(['gg','lol','hey','yo','!'])}"
                shard, res = st.session_state.router.send_message(uid, chan, content)
                if shard:
                    ok += 1
                    st.session_state.feed.append({"user":uid,"channel":chan,"content":content,"shard":shard.shard_id,"time":time.strftime("%H:%M:%S")})
                else:
                    fail += 1
                    st.session_state.dropped += 1
            st.session_state.feed = st.session_state.feed[-120:]
            if ok:
                add_log("ok", f"[{uid}] → #{chan}: {ok} msg(s) ✅  via Shard-{hash(chan if st.session_state.strategy=='channel_id' else uid) % 3}")
            if fail:
                add_log("err", f"[{uid}] → #{chan}: {fail} DROPPED — shard down!")
        if fail:
            st.markdown(f'<div class="alert-critical">❌ {fail} message(s) dropped — target shard is OFFLINE!</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-ok">✅ {ok} message(s) delivered successfully → #{chan}</div>', unsafe_allow_html=True)
        st.rerun()

    # Query
    st.markdown("---")
    st.markdown('<div class="section-title">🔍 &nbsp; Cross-Shard Query</div>', unsafe_allow_html=True)
    q_ch = st.selectbox("Query channel", CHANNELS, key="qch")
    q_n  = st.slider("Results", 5, 30, 10)
    if st.button("🔎 Fetch Messages", use_container_width=True):
        with st.spinner("Querying all shards (scatter-gather)..."):
            time.sleep(0.4)
            results = st.session_state.qe.query_channel_messages(q_ch, limit=q_n)
        if results:
            add_log("info", f"Cross-shard query #{q_ch}: {len(results)} msgs from {len(st.session_state.mgr.get_alive_shards())} shards")
            st.markdown(f'<div class="alert-ok">✅ Found {len(results)} messages in #{q_ch} via scatter-gather across {len(st.session_state.mgr.get_alive_shards())} shards</div>', unsafe_allow_html=True)
            for m in results[:8]:
                dot = DOT_CLS[m.get("shard",0)%3]
                st.markdown(f"""<div class="feed-item">
                    <div class="shard-dot {dot}"></div>
                    <span class="feed-user">{m['user_id']}</span>
                    <span class="feed-ch">#{m['channel']}</span>
                    <span class="feed-msg">{m['content'][:55]}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-warn">⚠️  No messages found — shard may be down or no data yet</div>', unsafe_allow_html=True)


with sim_col:
    st.markdown('<div class="section-title">⚙️ &nbsp; Simulation Controls</div>', unsafe_allow_html=True)

    sims = [
        ("🟢 Normal Load (1K msgs)",     "normal",   "1,000 balanced messages across all channels"),
        ("🔥 Viral Spike — #general 80%","viral",    "2,000 messages · 80% flood into #general"),
        ("👑 spam_king Attack 5K",        "spam",     "5,000 messages from a single viral user"),
        ("💀 Kill Shard-0 mid-traffic",   "kill0",    "Crash Shard-0 and continue sending traffic"),
        ("💚 Revive All Shards",          "revive",   "Bring all offline shards back online"),
        ("🌊 Mass Chaos (all at once)",   "chaos",    "Viral spike + shard failure simultaneously"),
    ]

    for label, key, desc in sims:
        c_btn, c_desc = st.columns([2,3])
        run = c_btn.button(label, key=f"sim_{key}", use_container_width=True)
        c_desc.markdown(f"<div style='font-size:11px;color:#475569;padding:10px 0'>{desc}</div>", unsafe_allow_html=True)

        if run:
            users = [f"user_{i}" for i in range(100)]
            with st.spinner(f"Running: {label}"):
                time.sleep(0.5)

                if key == "normal":
                    ok=fail=0
                    for i in range(1000):
                        s,r = st.session_state.router.send_message(random.choice(users), random.choice(CHANNELS), f"norm_{i}")
                        (ok if s else [fail])[0 if s else -1] if s else None
                        ok += 1 if s else 0; fail += 0 if s else 1
                        st.session_state.dropped += 0 if s else 1
                    add_log("ok", f"Normal load: 1,000 msgs processed · {fail} dropped")

                elif key == "viral":
                    ok=fail=0
                    for i in range(2000):
                        ch = "general" if random.random()<.8 else random.choice(CHANNELS[1:])
                        s,r = st.session_state.router.send_message(random.choice(users), ch, f"viral_{i}")
                        ok += 1 if s else 0; fail += 0 if s else 1
                        st.session_state.dropped += 0 if s else 1
                    add_log("warn", f"🔥 Viral spike: 2,000 msgs · 80% → #general · {fail} dropped")

                elif key == "spam":
                    ok=fail=0
                    for i in range(5000):
                        s,r = st.session_state.router.send_message("spam_king", random.choice(CHANNELS), f"SPAM_{i}")
                        ok += 1 if s else 0; fail += 0 if s else 1
                        st.session_state.dropped += 0 if s else 1
                    add_log("warn", f"👑 spam_king: 5,000 msgs · {fail} dropped")

                elif key == "kill0":
                    st.session_state.mgr.shards[0].kill()
                    for i in range(500):
                        st.session_state.router.send_message(random.choice(users), random.choice(CHANNELS), f"post_kill_{i}")
                    add_log("err", "Shard-0 KILLED mid-traffic · channels on it are now DARK")

                elif key == "revive":
                    for s in st.session_state.mgr.shards.values():
                        if not s.is_alive: s.revive()
                    add_log("ok", "All shards revived ✅")

                elif key == "chaos":
                    st.session_state.mgr.shards[1].kill()
                    for i in range(3000):
                        ch = "general" if random.random()<.8 else random.choice(CHANNELS[1:])
                        st.session_state.router.send_message(random.choice(users), ch, f"chaos_{i}")
                    add_log("err", "🌊 CHAOS: Viral spike + Shard-1 offline simultaneously!")

            st.rerun()

    st.markdown("---")

    # Message Feed
    st.markdown('<div class="section-title">💬 &nbsp; Live Message Feed</div>', unsafe_allow_html=True)
    if st.session_state.feed:
        for m in reversed(st.session_state.feed[-18:]):
            dot = DOT_CLS[m["shard"] % 3]
            st.markdown(f"""<div class="feed-item">
                <div class="shard-dot {dot}"></div>
                <span class="feed-user">{m['user']}</span>
                <span class="feed-ch">#{m['channel']}</span>
                <span class="feed-msg">{m['content'][:48]}</span>
                <span class="feed-time">{m['time']}</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#334155;font-size:13px;text-align:center;padding:30px 0">No messages yet — send one or run a simulation ↑</div>', unsafe_allow_html=True)

    # System Log
    st.markdown("---")
    st.markdown('<div class="section-title">📋 &nbsp; System Log</div>', unsafe_allow_html=True)
    icons = {"ok":"✅","info":"ℹ️","warn":"⚠️","err":"❌"}
    rows = "".join(
        f'<div class="log-{e["lvl"]}">[{e["t"]}] {icons.get(e["lvl"],"•")} {e["m"]}</div>'
        for e in reversed(st.session_state.syslog[-22:])
    )
    st.markdown(f'<div class="log-box">{rows}</div>', unsafe_allow_html=True)

# ── Footer ───────────────────────────────
st.markdown("""
<div style='text-align:center;color:#1e293b;font-size:12px;padding:24px 0 8px'>
  ⚡ Discord Sharding Simulator &nbsp;·&nbsp; System Design at Scale &nbsp;·&nbsp;
  <span style='color:#6366f1'>localhost:8501</span>
</div>
""", unsafe_allow_html=True)
