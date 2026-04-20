"""
Mentorship cohort dashboard: mentee vs mentor side-by-side comparison.
"""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

NAVY = "#1A2B4C"
MID_BLUE = "#4A69BD"
LIGHT_BLUE = "#8297D9"
PAGE_BG = "#F2F4F8"
CARD_BG = "#FFFFFF"
TEXT_BLACK = "#000000"

_REPO = Path(__file__).resolve().parent
_DEFAULT_BUNDLED = _REPO / "data" / "sample_survey.csv"
_LOCAL_FALLBACK = Path(
    r"c:\Users\rheam\Downloads\UpdateD Spreadsheet - Sheet1 (1).csv"
)
if os.environ.get("MENTORSHIP_CSV"):
    DEFAULT_CSV = Path(os.environ["MENTORSHIP_CSV"])
elif _DEFAULT_BUNDLED.is_file():
    DEFAULT_CSV = _DEFAULT_BUNDLED
elif _LOCAL_FALLBACK.is_file():
    DEFAULT_CSV = _LOCAL_FALLBACK
else:
    DEFAULT_CSV = _DEFAULT_BUNDLED

MENTOR_LIKERT_SUBSTRINGS = [
    "My mentorship relationship was impactful",
    "I saw growth in my mentee",
    "The structure and expectations of the program were clear",
    "The resources provided by Paragon were helpful",
    "I would recommend this mentorship experience to others",
    "I would be interested in mentoring again in the future",
]

MENTEE_LIKERT_SUBSTRINGS = [
    "My mentorship helped me make meaningful progress",
    "I received practical, helpful guidance from my mentor",
    "My understanding of tech policy and related fields has grown",
    "I feel more confident navigating my next career steps",
    "The structure and communication from Paragon supported my success",
    "I would recommend the program to other fellows",
]


def find_column(columns: list[str], substring: str) -> str | None:
    sub_l = substring.lower()
    for c in columns:
        if sub_l in c.lower():
            return c
    return None


def resolve_survey_columns(columns: list[str]) -> dict:
    cols = [c.strip() for c in columns]
    role_col = cols[0]

    mentor_likert = []
    for s in MENTOR_LIKERT_SUBSTRINGS:
        c = find_column(cols, s)
        if c:
            mentor_likert.append(c)
    mentee_likert = []
    for s in MENTEE_LIKERT_SUBSTRINGS:
        c = find_column(cols, s)
        if c:
            mentee_likert.append(c)

    meet_col = find_column(cols, "How many times did you meet")
    struct_col = find_column(cols, "The structure and expectations of the program were clear")
    resources_col = find_column(cols, "The resources provided by Paragon were helpful")

    month_rating_cols = []
    month_labels = []
    for n, short in [
        (1, "Month 1: Foundations"),
        (2, "Month 2: Career direction"),
        (3, "Month 3: Tech policy landscape"),
        (4, "Month 4: Resume & interviews"),
        (5, "Month 5: Networking & branding"),
    ]:
        pat = re.compile(rf"month\s*{n}\s*:", re.I)
        for c in cols:
            if pat.search(c) and "rate" in c.lower():
                month_rating_cols.append(c)
                month_labels.append(short)
                break

    return {
        "role_col": role_col,
        "mentor_likert": mentor_likert,
        "mentee_likert": mentee_likert,
        "meet_col": meet_col,
        "struct_col": struct_col,
        "resources_col": resources_col,
        "month_rating_cols": month_rating_cols,
        "month_labels": month_labels,
    }


def likert_to_numeric(series: pd.Series) -> pd.Series:
    m = {
        "strongly agree": 5.0,
        "agree": 4.0,
        "neutral": 3.0,
        "disagree": 2.0,
        "strongly disagree": 1.0,
    }
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map(m)
        .astype("float64")
    )


def pct_agree_strong(series: pd.Series) -> float:
    s = likert_to_numeric(series)
    s = s.dropna()
    if s.empty:
        return float("nan")
    return float((s >= 4.0).mean() * 100.0)


def mean_score(series: pd.Series) -> float:
    """Average for word Likert (Agree, …) or numeric 1–5 strings (e.g. monthly ratings)."""
    n = pd.to_numeric(series, errors="coerce")
    if n.notna().any():
        return float(n.dropna().mean())
    s = likert_to_numeric(series).dropna()
    if s.empty:
        return float("nan")
    return float(s.mean())


def horizontal_bar_chart(labels: list[str], values: list[float], title: str, x_max: float = 5.0):
    palette = [NAVY, MID_BLUE, LIGHT_BLUE, MID_BLUE, NAVY]
    bar_colors = [palette[i % len(palette)] for i in range(len(labels))]
    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=bar_colors,
            text=[f"{v:.2f}" if v == v else "—" for v in values],
            textposition="outside",
            textfont=dict(color=TEXT_BLACK),
        )
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=TEXT_BLACK)),
        font=dict(color=TEXT_BLACK),
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        margin=dict(l=10, r=40, t=50, b=10),
        height=max(220, 48 * len(labels) + 80),
        xaxis=dict(
            range=[0, x_max * 1.15],
            showgrid=True,
            gridcolor="#E8ECF2",
            tickfont=dict(color=TEXT_BLACK),
            title=dict(font=dict(color=TEXT_BLACK)),
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=11, color=TEXT_BLACK),
            title=dict(font=dict(color=TEXT_BLACK)),
        ),
        showlegend=False,
    )
    return fig


def pct_horizontal_bar(labels: list[str], values: list[float], title: str):
    palette = [NAVY, MID_BLUE, LIGHT_BLUE, MID_BLUE, NAVY, LIGHT_BLUE]
    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=[palette[i % len(palette)] for i in range(len(labels))],
            text=[f"{v:.0f}%" if v == v else "—" for v in values],
            textposition="outside",
            textfont=dict(color=TEXT_BLACK),
        )
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=TEXT_BLACK)),
        font=dict(color=TEXT_BLACK),
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        margin=dict(l=10, r=48, t=50, b=10),
        height=max(220, 44 * len(labels) + 80),
        xaxis=dict(
            range=[0, 115],
            showgrid=True,
            gridcolor="#E8ECF2",
            ticksuffix="%",
            tickfont=dict(color=TEXT_BLACK),
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=11, color=TEXT_BLACK),
        ),
        showlegend=False,
    )
    return fig


def meeting_distribution(df: pd.DataFrame, col: str | None) -> pd.Series:
    if not col or col not in df.columns:
        return pd.Series(dtype=float)
    s = df[col].astype(str).str.strip()
    s = s[s.isin(["1-4", "5-8", "9-12"])]
    if s.empty:
        return pd.Series(dtype=float)
    return s.value_counts(normalize=True) * 100


def donut_meetings(dist: pd.Series, title: str):
    order = ["1-4", "5-8", "9-12"]
    labels = [k for k in order if k in dist.index]
    vals = [float(dist.get(k, 0)) for k in labels]
    colors = [NAVY, MID_BLUE, LIGHT_BLUE]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=vals,
                hole=0.55,
                marker=dict(colors=colors[: len(labels)]),
                textinfo="label+percent",
                textposition="outside",
                textfont=dict(color=TEXT_BLACK),
            )
        ]
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=TEXT_BLACK)),
        font=dict(color=TEXT_BLACK),
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        margin=dict(t=50, b=20, l=20, r=20),
        height=320,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            font=dict(color=TEXT_BLACK),
        ),
    )
    return fig


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    role_col = df.columns[0]
    df["_role"] = df[role_col].astype(str).str.strip()
    df = df[df["_role"].isin(["Mentee", "Mentor"])].copy()
    return df


def short_label(text: str, max_len: int = 44) -> str:
    t = text.strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"


def main():
    st.set_page_config(
        page_title="Mentorship Cohort Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {PAGE_BG};
            color: {TEXT_BLACK};
        }}
        .hdr {{
            background: {CARD_BG};
            color: {TEXT_BLACK};
            border: 1px solid #DEE2E6;
            border-left: 4px solid {NAVY};
            padding: 1.25rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }}
        .hdr h1 {{
            margin: 0;
            font-size: 1.35rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            color: {TEXT_BLACK} !important;
        }}
        .hdr p {{
            margin: 0.5rem 0 0 0;
            font-size: 0.95rem;
            color: {TEXT_BLACK} !important;
            opacity: 1;
        }}
        .sec {{
            color: {TEXT_BLACK};
            font-weight: 700;
            font-size: 0.95rem;
            letter-spacing: 0.04em;
            border-left: 4px solid {NAVY};
            padding-left: 0.6rem;
            margin: 1.25rem 0 0.75rem 0;
        }}
        [data-testid="stMetric"] label p,
        [data-testid="stMetric"] label div {{
            color: {TEXT_BLACK} !important;
        }}
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: {TEXT_BLACK} !important;
        }}
        [data-testid="stMetric"] [data-testid="stMetricDelta"] svg {{
            color: {TEXT_BLACK} !important;
        }}
        [data-testid="stMetric"] [data-testid="stMetricDelta"] {{
            color: {TEXT_BLACK} !important;
        }}
        [data-testid="stCaption"] {{
            color: {TEXT_BLACK} !important;
        }}
        .stMarkdown h5 {{
            color: {TEXT_BLACK} !important;
        }}
        section[data-testid="stSidebar"] {{
            color: {TEXT_BLACK};
        }}
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stMarkdown {{
            color: {TEXT_BLACK} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Data")
        uploaded = st.file_uploader("Upload CSV (optional)", type=["csv"])
        csv_path: Path | None = None
        if uploaded is not None:
            fd, tmp_name = tempfile.mkstemp(suffix=".csv", prefix="mentorship_")
            os.close(fd)
            csv_path = Path(tmp_name)
            csv_path.write_bytes(uploaded.getvalue())
        elif DEFAULT_CSV.is_file():
            csv_path = DEFAULT_CSV
        else:
            st.warning(
                f"Default file not found:\n`{DEFAULT_CSV}`\n\nUpload a CSV or set env `MENTORSHIP_CSV`."
            )
            st.stop()

    try:
        df = load_data(csv_path)
    except Exception as e:
        st.error(f"Could not load CSV: {e}")
        st.stop()

    meta = resolve_survey_columns(list(df.columns))
    if len(meta["mentee_likert"]) < 4 or len(meta["mentor_likert"]) < 4:
        st.error(
            "Could not map expected survey columns from the header row. "
            "Check that this export matches the mentorship survey template."
        )
        st.write("Columns found:", list(df.columns))
        st.stop()

    n_m = int((df["_role"] == "Mentee").sum())
    n_r = int((df["_role"] == "Mentor").sum())
    df_m = df[df["_role"] == "Mentee"]
    df_r = df[df["_role"] == "Mentor"]

    st.markdown(
        f"""
        <div class="hdr">
            <h1>MENTORSHIP PROGRAM · COHORT DASHBOARD</h1>
            <p>Survey comparison · {n_m} mentees · {n_r} mentors · {len(df)} total respondents</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="sec">AT A GLANCE</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    def kpi_card(col, title: str, value: str, sub: str):
        with col:
            st.metric(title, value, sub)

    rec_m_col = meta["mentee_likert"][-1]
    rec_r_col = meta["mentor_likert"][4] if len(meta["mentor_likert"]) > 4 else None
    m_rec = mean_score(df_m[rec_m_col])
    r_rec_m = mean_score(df_r[rec_r_col]) if rec_r_col else float("nan")
    kpi_card(c1, "Mentees", str(n_m), "respondents")
    kpi_card(c2, "Mentors", str(n_r), "respondents")
    kpi_card(c3, "Mentee recommend (avg)", f"{m_rec:.2f}/5" if m_rec == m_rec else "—", "program to fellows")
    kpi_card(
        c4,
        "Mentor recommend (avg)",
        f"{r_rec_m:.2f}/5" if r_rec_m == r_rec_m else "—",
        "mentorship experience",
    )

    st.markdown(
        '<p class="sec">SIDE-BY-SIDE · PROGRAM & OUTCOMES</p>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("##### Mentees")
        m_labels = [short_label(c) for c in meta["mentee_likert"]]
        m_means = [mean_score(df_m[c]) for c in meta["mentee_likert"]]
        m_pcts = [pct_agree_strong(df_m[c]) for c in meta["mentee_likert"]]
        st.plotly_chart(
            horizontal_bar_chart(m_labels, m_means, "Average rating (1–5)"),
            use_container_width=True,
        )
        st.plotly_chart(
            pct_horizontal_bar(m_labels, m_pcts, "% Agree or Strongly Agree"),
            use_container_width=True,
        )

    with right:
        st.markdown("##### Mentors")
        r_labels = [short_label(c) for c in meta["mentor_likert"]]
        r_means = [mean_score(df_r[c]) for c in meta["mentor_likert"]]
        r_pcts = [pct_agree_strong(df_r[c]) for c in meta["mentor_likert"]]
        st.plotly_chart(
            horizontal_bar_chart(r_labels, r_means, "Average rating (1–5)"),
            use_container_width=True,
        )
        st.plotly_chart(
            pct_horizontal_bar(r_labels, r_pcts, "% Agree or Strongly Agree"),
            use_container_width=True,
        )

    meet_col = meta["meet_col"]
    dm = meeting_distribution(df_m, meet_col)
    dr = meeting_distribution(df_r, meet_col)
    if not dm.empty or not dr.empty:
        st.markdown(
            '<p class="sec">MEETING FREQUENCY · MENTEES VS MENTORS</p>',
            unsafe_allow_html=True,
        )
        ml, mr = st.columns(2)
        with ml:
            if not dm.empty:
                st.plotly_chart(
                    donut_meetings(dm, "Mentees — meetings reported"),
                    use_container_width=True,
                )
                if "1-4" in dm.index and dm.sum() > 0:
                    st.caption(
                        f"{dm.get('1-4', 0):.0f}% met 1–4 times (mentee-reported distribution)."
                    )
        with mr:
            if not dr.empty:
                st.plotly_chart(
                    donut_meetings(dr, "Mentors — meetings reported"),
                    use_container_width=True,
                )
                if "1-4" in dr.index and dr.sum() > 0:
                    st.caption(
                        f"{dr.get('1-4', 0):.0f}% met 1–4 times (mentor-reported distribution)."
                    )

    if meta["month_rating_cols"]:
        st.markdown(
            '<p class="sec">MONTHLY CURRICULUM SUPPORT (AVG 1–5)</p>',
            unsafe_allow_html=True,
        )
        bl, br = st.columns(2)
        mcols = meta["month_rating_cols"]
        mlab = meta["month_labels"][: len(mcols)]
        with bl:
            mv = [mean_score(df_m[c]) for c in mcols]
            palette = [NAVY, MID_BLUE, MID_BLUE, MID_BLUE, LIGHT_BLUE]
            fig_m = go.Figure(
                go.Bar(
                    x=mlab,
                    y=mv,
                    marker=dict(color=palette[: len(mv)]),
                    text=[f"{v:.2f}" if v == v else "—" for v in mv],
                    textposition="outside",
                    textfont=dict(color=TEXT_BLACK),
                )
            )
            fig_m.update_layout(
                title=dict(text="Mentees", font=dict(color=TEXT_BLACK)),
                font=dict(color=TEXT_BLACK),
                paper_bgcolor=CARD_BG,
                plot_bgcolor=CARD_BG,
                yaxis=dict(
                    range=[0, 5.5],
                    showgrid=True,
                    gridcolor="#E8ECF2",
                    tickfont=dict(color=TEXT_BLACK),
                ),
                xaxis=dict(
                    tickangle=-25,
                    tickfont=dict(color=TEXT_BLACK),
                ),
                height=400,
                margin=dict(t=50, b=100),
            )
            st.plotly_chart(fig_m, use_container_width=True)
        with br:
            rv = [mean_score(df_r[c]) for c in mcols]
            fig_r = go.Figure(
                go.Bar(
                    x=mlab,
                    y=rv,
                    marker=dict(color=palette[: len(rv)]),
                    text=[f"{v:.2f}" if v == v else "—" for v in rv],
                    textposition="outside",
                    textfont=dict(color=TEXT_BLACK),
                )
            )
            fig_r.update_layout(
                title=dict(text="Mentors", font=dict(color=TEXT_BLACK)),
                font=dict(color=TEXT_BLACK),
                paper_bgcolor=CARD_BG,
                plot_bgcolor=CARD_BG,
                yaxis=dict(
                    range=[0, 5.5],
                    showgrid=True,
                    gridcolor="#E8ECF2",
                    tickfont=dict(color=TEXT_BLACK),
                ),
                xaxis=dict(
                    tickangle=-25,
                    tickfont=dict(color=TEXT_BLACK),
                ),
                height=400,
                margin=dict(t=50, b=100),
            )
            st.plotly_chart(fig_r, use_container_width=True)

    with st.expander("Sample sizes & column mapping"):
        st.write(
            {
                "mentee_rows": len(df_m),
                "mentor_rows": len(df_r),
                "meeting_column": meet_col,
                "month_rating_columns_found": len(meta["month_rating_cols"]),
            }
        )
        st.subheader("Mentee Likert columns")
        st.code("\n".join(meta["mentee_likert"]), language="text")
        st.subheader("Mentor Likert columns")
        st.code("\n".join(meta["mentor_likert"]), language="text")


if __name__ == "__main__":
    main()
