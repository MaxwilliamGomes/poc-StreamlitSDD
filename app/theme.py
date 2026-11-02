"""Design tokens and global CSS. Dark palette validated against CARD_SURFACE."""

import streamlit as st

CARD_SURFACE = "#101827"
BLUE = "#3987e5"
ORANGE = "#d95926"
AQUA = "#199e70"
YELLOW = "#c98500"
GRID = "#243047"
AXIS = "#3a4760"
INK = "#f0f3f8"
INK_SECONDARY = "#b9c3d3"
INK_MUTED = "#8894a8"
GOOD = "#0ca30c"
WARNING = "#fab219"
CRITICAL = "#e66767"
SEQUENTIAL = ["#14233f", "#104281", "#1c5cab", "#3987e5", "#86b6ef", "#cde2fb"]

_CSS = f"""
<style>
.stApp {{
  background:
    radial-gradient(1100px 520px at 8% -8%, rgba(57,135,229,.20), transparent 62%),
    radial-gradient(900px 480px at 96% 2%, rgba(25,158,112,.11), transparent 60%),
    #0a0f1c;
}}
.block-container {{ padding: 4.4rem 2.2rem 3rem; max-width: 1880px; }}
h1, h2, h3 {{ letter-spacing: -.015em; }}

/* Cards: any container whose key starts with "card" */
[class*="st-key-card"] {{
  background: linear-gradient(160deg, rgba(30,42,66,.72), rgba(16,24,39,.88));
  border: 1px solid rgba(148,163,184,.14);
  border-radius: 18px;
  padding: 1.05rem 1.15rem .8rem;
  box-shadow: 0 10px 30px rgba(2,6,18,.35);
  transition: border-color .18s ease;
}}
[class*="st-key-card"]:hover {{ border-color: rgba(57,135,229,.42); }}

.st-key-filterbar {{
  background: rgba(16,24,39,.72);
  border: 1px solid rgba(148,163,184,.14);
  border-radius: 16px;
  padding: .7rem 1rem .25rem;
  backdrop-filter: blur(10px);
}}

.dash-brand {{ display:flex; align-items:baseline; gap:.65rem; margin-bottom:.15rem; }}
.dash-brand b {{ font-size:1.65rem; font-weight:650; color:{INK}; letter-spacing:-.02em; }}
.dash-brand span {{ color:{INK_MUTED}; font-size:.86rem; }}
.card-title {{ font-size:.98rem; font-weight:600; color:{INK}; margin:0; }}
.card-sub {{ font-size:.78rem; color:{INK_MUTED}; margin:.1rem 0 .45rem; }}

/* Stat tiles */
.tile {{ position:relative; height:100%; min-height:148px; box-sizing:border-box;
  background:linear-gradient(160deg, rgba(30,42,66,.78), rgba(16,24,39,.92));
  border:1px solid rgba(148,163,184,.14); border-radius:18px; padding:1rem 1.1rem .7rem;
  outline:none; transition:transform .18s ease, border-color .18s ease; }}
.tile:hover, .tile:focus {{ transform:translateY(-2px); border-color:rgba(57,135,229,.55); }}
.tile-label {{ color:{INK_SECONDARY}; font-size:.82rem; }}
.tile-value {{ color:{INK}; font-size:1.72rem; font-weight:650; letter-spacing:-.02em; line-height:1.25; }}
.tile.hero {{ background:linear-gradient(135deg, rgba(57,135,229,.34), rgba(16,24,39,.92) 70%);
  border-color:rgba(57,135,229,.40); }}
.tile.hero .tile-value {{ font-size:2.6rem; }}
.tile-row {{ display:flex; align-items:center; gap:.45rem; margin:.15rem 0 .3rem; font-size:.76rem;
  color:{INK_MUTED}; }}
.delta {{ display:inline-flex; align-items:center; gap:.22rem; font-weight:600; border-radius:999px;
  padding:.08rem .5rem; font-size:.76rem; color:{INK}; }}
.delta.good {{ background:rgba(12,163,12,.20); }}
.delta.bad {{ background:rgba(230,103,103,.20); }}
.delta.none {{ background:rgba(148,163,184,.14); color:{INK_SECONDARY}; }}
.spark {{ display:block; width:100%; height:42px; }}

/* Tooltips, shown on hover and keyboard focus */
.tip {{ position:absolute; left:12px; right:12px; top:calc(100% - 6px); z-index:50; visibility:hidden;
  opacity:0; transform:translateY(-4px); transition:opacity .15s ease, transform .15s ease;
  background:#1b2740; border:1px solid rgba(148,163,184,.28); border-radius:12px;
  padding:.55rem .7rem; box-shadow:0 14px 34px rgba(0,0,0,.5); font-size:.78rem; color:{INK_SECONDARY}; }}
.tile:hover .tip, .tile:focus .tip {{ visibility:visible; opacity:1; transform:none; }}
.tip div {{ display:flex; justify-content:space-between; gap:1rem; }}
.tip b {{ color:{INK}; font-weight:650; }}

/* Insights */
.insights {{ display:flex; flex-wrap:wrap; gap:.55rem; margin:.1rem 0 .15rem; }}
.insight {{ flex:1 1 260px; color:{INK_SECONDARY}; font-size:.84rem; border-left:2px solid {BLUE};
  padding:.15rem .7rem; }}

/* Segmented bar */
.seg {{ display:flex; gap:2px; height:28px; margin:.35rem 0 .5rem; }}
.seg > div {{ border-radius:4px; color:#fff; font-size:.74rem; font-weight:600; line-height:28px;
  padding-left:.45rem; white-space:nowrap; overflow:visible; min-width:2px; }}
.legend {{ display:flex; flex-wrap:wrap; gap:.3rem .9rem; font-size:.76rem; color:{INK_SECONDARY}; }}
.legend i {{ display:inline-block; width:9px; height:9px; border-radius:3px; margin-right:.32rem; }}

/* Conditional tables */
.ctable {{ width:100%; border-collapse:collapse; font-size:.83rem; color:{INK_SECONDARY}; }}
.ctable th {{ text-align:right; font-weight:500; color:{INK_MUTED}; font-size:.74rem;
  border-bottom:1px solid {GRID}; padding:.32rem .55rem; }}
.ctable td {{ text-align:right; padding:.36rem .55rem; border-bottom:1px solid rgba(36,48,71,.55);
  font-variant-numeric:tabular-nums; }}
.ctable th:first-child, .ctable td:first-child {{ text-align:left; color:{INK}; }}
.ctable tr:hover td {{ background:rgba(57,135,229,.08); }}
.databar {{ position:relative; display:block; min-width:84px; }}
.databar i {{ position:absolute; inset:2px auto 2px 0; background:rgba(57,135,229,.32); border-radius:0 4px 4px 0; }}
.databar b {{ position:relative; font-weight:500; color:{INK}; }}
.up {{ color:#35c435; }} .down {{ color:#f08a8a; }}
.heat {{ border-radius:5px; padding:.1rem .4rem; color:{INK}; }}
.chip {{ display:inline-block; border:1px solid rgba(148,163,184,.25); border-radius:999px;
  padding:0 .5rem; font-size:.7rem; color:{INK_SECONDARY}; }}

/* Rating ring and comments */
.ring {{ display:flex; align-items:center; gap:1rem; }}
.ring-img {{ width:112px; height:112px; flex:none; }}
.ring-text {{ font-size:.82rem; color:{INK_SECONDARY}; }}
.comment {{ border:1px solid rgba(148,163,184,.13); border-radius:12px; padding:.55rem .75rem;
  margin-bottom:.45rem; background:rgba(10,15,28,.35); }}
.comment p {{ margin:.2rem 0 .3rem; color:{INK}; font-size:.86rem; }}
.comment small {{ color:{INK_MUTED}; font-size:.74rem; }}
.stars {{ color:{WARNING}; letter-spacing:.06em; font-size:.8rem; }}

[data-testid="stTabs"] button p {{ font-size:.76rem; }}
[data-testid="stMetric"] {{ background:none; }}
</style>
"""


def apply_theme() -> None:
    st.html(_CSS)
