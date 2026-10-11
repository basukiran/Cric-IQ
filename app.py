import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup

import streamlit as st
import pandas as pd
import os

# -------------------------------
# LOAD DATA
# -------------------------------

@st.cache_data
def load_data(format_name):
    files = {
        "IPL": "ipl_deliveries.csv",
        "ODI": "odis_deliveries.csv",
        "T20I": "t20s_deliveries.csv",
        "TEST": "tests_deliveries.csv"
    }

    df = pd.read_csv(files[format_name])

    # Standardize column names
    if "wicket_player_out" in df.columns:
        df.rename(columns={"wicket_player_out": "player_out"}, inplace=True)

    if "wicket_kind" in df.columns:
        df.rename(columns={"wicket_kind": "dismissal_type"}, inplace=True)

    if "batting_team" in df.columns:
        df.rename(columns={"batting_team": "innings_team"}, inplace=True)

    return df


def numeric_column(frame, column):
    """Return a numeric column, treating missing or unavailable extras as zero."""
    if column not in frame.columns:
        return pd.Series(0, index=frame.index, dtype="float64")
    return pd.to_numeric(frame[column], errors="coerce").fillna(0)


def summarize_bowling(deliveries):
    """Summarize bowler-credit wickets, legal balls and runs charged to bowlers."""
    events = deliveries.copy()
    wides = numeric_column(events, "extras_wides")
    no_balls = numeric_column(events, "extras_noballs")
    events["Legal Balls"] = (wides.eq(0) & no_balls.eq(0)).astype(int)

    runs_charged = numeric_column(events, "runs_total")
    for extra in ("extras_byes", "extras_legbyes", "extras_penalty"):
        runs_charged = runs_charged - numeric_column(events, extra)
    events["Runs"] = runs_charged.clip(lower=0)

    if "player_out" in events.columns:
        dismissed = events["player_out"].notna()
    else:
        dismissed = pd.Series(False, index=events.index)
    if "dismissal_type" in events.columns:
        dismissal_type = (
            events["dismissal_type"].fillna("").astype(str).str.lower()
            .str.replace("_", " ", regex=False)
        )
    else:
        dismissal_type = pd.Series("", index=events.index)
    not_bowler_wickets = {
        "run out", "retired hurt", "retired out",
        "obstructing the field", "timed out"
    }
    events["Wickets"] = (
        dismissed & ~dismissal_type.isin(not_bowler_wickets)
    ).astype(int)

    summary = (
        events.groupby("bowler")
        .agg(
            Balls=("Legal Balls", "sum"),
            Runs=("Runs", "sum"),
            Wickets=("Wickets", "sum")
        )
        .reset_index()
    )
    summary["Overs"] = summary["Balls"].apply(
        lambda balls: f"{int(balls) // 6}.{int(balls) % 6}"
    )
    summary["Economy"] = (
        summary["Runs"] * 6 / summary["Balls"].replace(0, 1)
    ).round(2)
    return summary


# -------------------------------
# SIDEBAR
# -------------------------------



# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("""
    <div style='text-align:center;padding:15px'>
        <h1 style='color:#00D4FF;margin-bottom:0;'>🏏 CricIQ</h1>
        <p style='color:lightgray;font-size:14px;'>
            Cricket Analytics Dashboard
        </p>
    </div>
    """, unsafe_allow_html=True)

    

    format_selected = st.selectbox(
        "🏆 Select Cricket Format",
        ["IPL", "ODI", "T20I", "TEST"]
    )

    

    page = st.radio(
        "📂 Navigation",
        [
            "🏠 Dashboard",
            "📡 Live Scores",
            "📂 Dataset Analyzer",
            "👤 Player Search",
            "🏏 Batting Analytics",
            "🎯 Bowling Analytics",
            "⚔️ Head to Head",
            "🏆 Team Analysis",
            "🏟️ Venue Analysis"
        ]
    )

    

    st.info(
        f"""
**Current Format**

🏏 {format_selected}

**Dataset**

Loaded Successfully ✅
"""
    )

df = load_data(format_selected)
matches_files = {
    "IPL": "ipl_matches.csv",
    "ODI": "odis_matches.csv",
    "T20I": "t20s_matches.csv",
    "TEST": "tests_matches.csv"
}

matches = pd.read_csv(matches_files[format_selected])

winner_col = None
if "winner" in matches.columns:
    winner_col = "winner"
elif "outcome_winner" in matches.columns:
    winner_col = "outcome_winner"

deliveries = df

# -------------------------------
# DASHBOARD
# -------------------------------
if page == "🏠 Dashboard":

    st.markdown("""
<style>

/* Main App */
[data-testid="stAppViewContainer"]{
    background: linear-gradient(135deg,#06121f,#0b1d33,#102842);
}

/* Main Content */
.main{
    background: transparent;
}

/* Sidebar */
[data-testid="stSidebar"]{
    background:#08131f;
}

/* Header */
[data-testid="stHeader"]{
    background:transparent;
}

/* Toolbar */
[data-testid="stToolbar"]{
    background:transparent;
}

/* Metric Cards */
div[data-testid="stMetric"]{
    background:#122033;
    border:1px solid #1dd75b;
    border-radius:15px;
    padding:15px;
    box-shadow:0 0 15px rgba(29,215,91,0.2);
}

/* Buttons */
div.stButton > button{
    background:#122033;
    color:white;
    border:1px solid #1dd75b;
    border-radius:12px;
    height:60px;
    font-weight:bold;
}

div.stButton > button:hover{
    background:#1dd75b;
    color:black;
}

/* Tables */
[data-testid="stDataFrame"]{
    background:#122033;
    border-radius:15px;
}

/* Selectbox */
.stSelectbox > div > div{
    background:#122033;
    color:white;
}

/* Text */
h1,h2,h3,h4,h5,h6,p,label,span{
    color:white;
}

</style>
""", unsafe_allow_html=True)

    ############################################
    # HEADER
    ############################################

    left,right = st.columns([3,1])

    with left:

        col1,col2 = st.columns([1,4])

        with col1:
            st.image("cricket_logo.jpg", width=120)

        with col2:

            st.markdown("""
            <div class="hero-title">
            CRIC<span class="hero-green">IQ</span>
            </div>

            <div style="font-size:30px;color:#57E25F;">
            Cricket Intelligence Quotient
            </div>

            <div class="hero-text">
            Data-driven Cricket Analytics Platform
            <br>
            Analyze player performance, venue trends,
            team strategies and live cricket insights.
            </div>
            """, unsafe_allow_html=True)

    st.caption(
        "Purpose: compare scoring pace and volume, team results, and venue scoring "
        "patterns across IPL, ODI, T20I, and Test data. These pages describe the "
        "historical datasets; they do not predict match outcomes."
    )

    

    ############################################

    st.image(
        "dashboard.jpg",
        use_container_width=True
    )

    ############################################
    # KPI ROW
    ############################################

    c1,c2,c3,c4,c5 = st.columns(5)

    c1.metric(
        "🏏 Matches",
        matches["match_id"].nunique()
    )

    c2.metric(
        "👤 Players",
        df["batter"].nunique()
    )

    c3.metric(
        "🏆 Teams",
        len(
            pd.concat([
                matches["team1"],
                matches["team2"]
            ]).unique()
        )
    )

    c4.metric(
        "🏟 Venues",
        matches["venue"].nunique()
    )

    if "season" in matches.columns:
        seasons = matches["season"].nunique()
    else:
        seasons = "-"

    c5.metric(
        "📅 Seasons",
        seasons
    )

    ############################################
    # QUICK NAVIGATION
    ############################################

    st.markdown("## 🚀 Quick Navigation")

    q1,q2,q3,q4,q5 = st.columns(5)

    with q1:
        st.button("👤 Player Analysis")

    with q2:
        st.button("🏆 Team Analysis")

    with q3:
        st.button("🏟 Venue Insights")

    with q4:
        st.button("⚔ Head to Head")

    with q5:
        st.button("📄 Reports")

    ############################################
    # CHARTS
    ############################################

    left,right = st.columns(2)

    with left:

        st.subheader("🏆 Top Run Scorers")

        top = (
            df.groupby("batter")["runs_batter"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        st.bar_chart(top)

    with right:

        st.subheader("🏆 Team Rankings")

        if winner_col:

            winners = (
                matches[winner_col]
                .value_counts()
                .head(10)
            )

            st.bar_chart(winners)

    top_run_scorer = top.index[0]
    top_run_count = int(top.iloc[0])
    leading_winner = (
        winners.index[0] if winner_col and not winners.empty else "unavailable"
    )
    leader_wins = int(winners.iloc[0]) if winner_col and not winners.empty else 0
    st.info(
        f"**What this shows:** {top_run_scorer} leads this format with "
        f"{top_run_count:,} batter runs across the loaded delivery data. "
        + (
            f"{leading_winner} has the most recorded match wins ({leader_wins}). "
            "These are cumulative totals, so they reflect career length and "
            "match volume as well as performance."
            if winner_col and not winners.empty
            else "Match winner data is not available for this format."
        )
    )

    if "season" in matches.columns:
        match_scores = (
            df.groupby("match_id")["runs_total"]
            .sum()
            .rename("Match Runs")
            .reset_index()
            .merge(matches[["match_id", "season"]], on="match_id", how="inner")
        )
        season_trend = (
            match_scores.groupby("season")
            .agg(
                Average_Match_Runs=("Match Runs", "mean"),
                Matches=("match_id", "nunique")
            )
            .reset_index()
            .sort_values("season")
        )
        if len(season_trend) > 1:
            st.subheader("📈 Scoring Trend by Season")
            trend_fig = px.line(
                season_trend,
                x="season",
                y="Average_Match_Runs",
                markers=True,
                hover_data={"Matches": True},
                labels={
                    "season": "Season",
                    "Average_Match_Runs": "Average total runs per match"
                }
            )
            st.plotly_chart(trend_fig, use_container_width=True)
            first_season = season_trend.iloc[0]
            last_season = season_trend.iloc[-1]
            run_change = (
                last_season["Average_Match_Runs"]
                - first_season["Average_Match_Runs"]
            )
            st.caption(
                f"Average match total changed from {first_season['Average_Match_Runs']:.1f} "
                f"runs in {first_season['season']} ({int(first_season['Matches'])} matches) "
                f"to {last_season['Average_Match_Runs']:.1f} in {last_season['season']} "
                f"({int(last_season['Matches'])} matches), a difference of "
                f"{run_change:+.1f}. Season totals can be affected by match format, "
                "rules, and the number of matches in the sample."
            )

    ############################################
    # RECENT MATCHES
    ############################################

   

    ############################################
    # ABOUT
    ############################################

    st.markdown("""

    <div class="about-box">

    <h2 style="color:#57E25F;">

    ABOUT CRICIQ

    </h2>

    <p style="font-size:18px;color:#d1d5db;">

    CricIQ is a data-driven cricket analytics platform
    built using Streamlit and Python.

    It supports IPL, ODI, T20I and Test datasets,
    allowing users to analyze batting, bowling,
    venue performance, team statistics,
    head-to-head comparisons and live match data
    through interactive visualizations.

    </p>

    </div>

    """, unsafe_allow_html=True)

    ############################################
    # FOOTER
    ############################################

    st.markdown("""

    <div class="footer">

    📧 criciq@gmail.com

    <br>

    🌐 www.criciq.com

    <br>

    Made with ❤️ using Python, Streamlit & Plotly

    <br><br>

    © 2026 CricIQ

    </div>

    """, unsafe_allow_html=True)

    #----Uploaded file option---
elif page == "📂 Dataset Analyzer":

    st.title("📂 Smart Cricket Dataset Analyzer")
    st.caption(
        "Upload a CSV to inspect its structure and distributions. The charts are "
        "descriptive: they show patterns in your file and do not infer causes."
    )

    uploaded_file = st.file_uploader(
        "Upload Cricket CSV Dataset",
        type=["csv"]
    )

    if uploaded_file is not None:

        df_upload = pd.read_csv(uploaded_file)

        st.success("Dataset Loaded Successfully")

        # Dataset Overview
        st.subheader("📊 Dataset Overview")

        c1, c2, c3 = st.columns(3)

        c1.metric("Rows", len(df_upload))
        c2.metric("Columns", len(df_upload.columns))
        c3.metric(
            "Missing Values",
            int(df_upload.isnull().sum().sum())
        )

        st.dataframe(df_upload.head())




      

        # Numeric Columns
        numeric_cols = df_upload.select_dtypes(
            include="number"
        ).columns

        if len(numeric_cols) > 0:

            st.markdown("---")
            st.subheader("📈 Numeric Column Analysis")

            selected_num = st.selectbox(
                "Select Numeric Column",
                numeric_cols
            )

            fig = px.histogram(
                df_upload,
                x=selected_num,
                title=f"Distribution of {selected_num}"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
            selected_values = pd.to_numeric(
                df_upload[selected_num], errors="coerce"
            ).dropna()
            if not selected_values.empty:
                st.caption(
                    f"{selected_num}: median {selected_values.median():,.2f}, "
                    f"mean {selected_values.mean():,.2f}, and "
                    f"{selected_values.nunique():,} distinct observed values. "
                    "A long tail or separated peaks in the histogram may indicate "
                    "outliers or different subgroups worth investigating."
                )

        # Categorical Columns
        categorical_cols = df_upload.select_dtypes(
            include="object"
        ).columns

        if len(categorical_cols) > 0:

        
            st.subheader("📊 Category Analysis")

            selected_cat = st.selectbox(
                "Select Category Column",
                categorical_cols
            )

            cat_data = (
                df_upload[selected_cat]
                .value_counts()
                .head(15)
                .reset_index()
            )

            cat_data.columns = [
                selected_cat,
                "Count"
            ]

            fig = px.bar(
                cat_data,
                x=selected_cat,
                y="Count",
                title=f"Top Values in {selected_cat}"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
            if not cat_data.empty:
                leading_category = cat_data.iloc[0]
                leading_share = (
                    leading_category["Count"] / len(df_upload) * 100
                    if len(df_upload) else 0
                )
                st.caption(
                    f"{leading_category[selected_cat]} is the most common value "
                    f"({int(leading_category['Count']):,} rows, {leading_share:.1f}% "
                    "of the file). A dominant category can make averages or model "
                    "results less representative of smaller groups."
                )

        missing_by_column = (
            df_upload.isna().sum().rename("Missing values")
            .loc[lambda counts: counts > 0]
            .sort_values(ascending=False)
        )
        if not missing_by_column.empty:
            st.subheader("🧩 Missing values by column")
            st.dataframe(
                missing_by_column.to_frame(),
                use_container_width=True
            )

        
        # Dataset Summary
        st.markdown("---")
        st.subheader("🤖 Dataset Insights")

        st.info(f"""
        Dataset contains {len(df_upload):,} rows and
        {len(df_upload.columns)} columns.

        Numeric Columns: {len(numeric_cols)}

        Categorical Columns: {len(categorical_cols)}

        Missing Values: {int(df_upload.isnull().sum().sum())}
        """)
    #--- live matches ---
    
elif page == "📡 Live Scores":

    import requests
    from datetime import datetime

    st.title("🏏 Live Cricket Dashboard")
    st.caption(
        "This page is a live snapshot from the match feed. Scores can change during play; "
        "they describe current matches and are separate from the historical CSV analysis."
    )

    API_KEY = "c7573d34-0187-4b84-89fe-24314ab59685"

    col1, col2 = st.columns([5,1])

    with col2:
        refresh = st.button("🔄 Refresh")

    url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"

    try:

        response = requests.get(url, timeout=15)
        data = response.json()

        if data["status"] != "success":
            st.error(data.get("reason","Unable to fetch matches"))
            st.stop()

        matches = data["data"]

        if len(matches)==0:
            st.warning("No Live Matches Available")
            st.stop()

        # KPI Cards
        total = len(matches)

        international = sum(
            1 for m in matches
            if m.get("matchType","").lower() in
            ["test","odi","t20"]
        )

        domestic = total - international

        c1,c2,c3 = st.columns(3)

        c1.metric("🏏 Live Matches",total)
        c2.metric("🌍 International",international)
        c3.metric("🏆 Domestic",domestic)

        st.markdown("---")

        for match in matches:

            with st.container():

                st.markdown(f"""
                <div style="
                background:#0f172a;
                padding:18px;
                border-radius:15px;
                border:1px solid #22c55e;
                margin-bottom:15px;">

                <h3 style="color:white;">
                🏏 {match.get('name','Match')}
                </h3>

                <p style="color:#22c55e;">
                <b>{match.get('status','')}</b>
                </p>

                <p style="color:white;">
                📍 {match.get('venue','Unknown')}
                </p>

                <p style="color:white;">
                🏆 {match.get('series','N/A')}
                </p>

                <p style="color:white;">
                🎯 {match.get('matchType','N/A').upper()}
                </p>

                </div>
                """,unsafe_allow_html=True)

                if match.get("score"):

                    score = pd.DataFrame(match["score"])

                    with st.expander("📊 View Scorecard"):

                        st.dataframe(
                            score,
                            use_container_width=True
                        )

    except Exception as e:

        st.error(e)
# -------------------------------
# BATTING ANALYTICS
# -------------------------------

elif page == "🏏 Batting Analytics":
    st.title("🏏 Batting Analytics Dashboard")

    batting_events = df.copy()
    batting_events["Ball Faced"] = numeric_column(
        batting_events, "extras_wides"
    ).eq(0).astype(int)
    batting = (
        batting_events.groupby("batter")
        .agg(
            Runs=("runs_batter", "sum"),
            Balls=("Ball Faced", "sum")
        )
        .reset_index()
    )

    batting["Strike Rate"] = (
        batting["Runs"] /
        batting["Balls"] * 100
    ).round(2)

    batting = batting.sort_values(
        "Runs",
        ascending=False
    )

    # ------------------------
    # Search Player
    # ------------------------

    player = st.selectbox(
        "🔍 Select Batter",
        sorted(batting["batter"].unique())
    )

    pdata = batting[
        batting["batter"] == player
    ].iloc[0]

    # ------------------------
    # KPI Cards
    # ------------------------

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "🏏 Runs",
        int(pdata["Runs"])
    )

    c2.metric(
        "🎯 Balls",
        int(pdata["Balls"])
    )

    c3.metric(
        "⚡ Strike Rate",
        pdata["Strike Rate"]
    )

    player_rank = int(
        batting["Runs"].rank(method="min", ascending=False)[
            batting["batter"] == player
        ].iloc[0]
    )
    median_strike_rate = batting["Strike Rate"].median()
    strike_rate_difference = pdata["Strike Rate"] - median_strike_rate
    st.info(
        f"**Interpretation:** {player} ranks {player_rank} of {len(batting)} "
        f"batters by total runs in {format_selected}. Their strike rate is "
        f"{pdata['Strike Rate']:.2f}, {abs(strike_rate_difference):.2f} points "
        f"{'above' if strike_rate_difference >= 0 else 'below'} the format "
        f"median ({median_strike_rate:.2f}). Strike rate is runs per 100 balls; "
        "the ranking is cumulative and does not adjust for matches played."
    )

    

    # ------------------------
    # Gauge Chart
    # ------------------------

    st.subheader("⚡ Strike Rate Gauge")

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pdata["Strike Rate"],
        title={"text":"Strike Rate"},
        gauge={
            "axis":{"range":[0,200]},
            "bar":{"color":"lime"},
            "steps":[
                {"range":[0,100],"color":"red"},
                {"range":[100,130],"color":"orange"},
                {"range":[130,160],"color":"yellow"},
                {"range":[160,200],"color":"green"}
            ]
        }
    ))

    st.plotly_chart(
        gauge,
        use_container_width=True
    )

    

    # ------------------------
    # Bubble Chart
    # ------------------------

    st.subheader("🟢 Bubble Chart")

    fig = px.scatter(
        batting.head(100),
        x="Balls",
        y="Runs",
        size="Runs",
        color="Strike Rate",
        hover_name="batter",
        title="Runs vs Balls",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "How to read it: each point is a batter. Further right means more balls "
        "faced; higher means more runs. Bubble size is runs and color is strike rate."
    )

    

    # ------------------------
    # Interactive Scatter Plot
    # ------------------------

    st.subheader("📈 Strike Rate Analysis")

    fig2 = px.scatter(
        batting.head(150),
        x="Strike Rate",
        y="Runs",
        color="Runs",
        size="Balls",
        hover_name="batter",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.caption(
        "How to read it: the chart separates volume (runs) from scoring pace "
        "(strike rate). Players high on both axes combine large run totals with fast scoring."
    )

    

    # ------------------------
    # Donut Chart
    # ------------------------

    st.subheader("🥧 Top 10 Run Contribution")

    top10 = batting.head(10)

    fig3 = px.pie(
        top10,
        values="Runs",
        names="batter",
        hole=0.55,
        template="plotly_dark"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    

    # ------------------------
    # Treemap
    # ------------------------

    st.subheader("🌳 Runs Distribution")

    fig4 = px.treemap(
        batting.head(30),
        path=["batter"],
        values="Runs",
        color="Strike Rate",
        color_continuous_scale="Viridis"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )



    # ------------------------
    # Interactive Table
    # ------------------------

    st.subheader("🏆 Top Run Scorers")

    st.dataframe(
        batting.head(20),
        use_container_width=True
    )

    # ------------------------
    # Download CSV
    # ------------------------

    csv = batting.to_csv(
        index=False
    ).encode()

    st.download_button(
        "⬇ Download Batting Statistics",
        csv,
        "Batting_Analytics.csv",
        "text/csv"
    )
# -------------------------------
# BOWLING ANALYTICS
# -------------------------------

elif page == "🎯 Bowling Analytics":

    st.title("🎯 Bowling Analytics Dashboard")

    if "bowler" not in df.columns or "player_out" not in df.columns:
        st.error("No wicket data available.")
        st.stop()

    bowling = summarize_bowling(df)

    player=st.selectbox(
        "🔍 Select Bowler",
        sorted(bowling["bowler"].unique())
    )

    pdata=bowling[
        bowling["bowler"]==player
    ].iloc[0]

    c1,c2,c3,c4=st.columns(4)

    c1.metric("🎯 Wickets",int(pdata["Wickets"]))
    c2.metric("🏏 Overs",pdata["Overs"])
    c3.metric("📉 Economy",pdata["Economy"])
    c4.metric("⚾ Balls",int(pdata["Balls"]))

    median_economy = bowling.loc[bowling["Balls"] > 0, "Economy"].median()
    selected_wicket_rank = int(
        bowling["Wickets"].rank(method="min", ascending=False)[
            bowling["bowler"] == player
        ].iloc[0]
    )
    st.info(
        f"**Interpretation:** {player} ranks {selected_wicket_rank} of "
        f"{len(bowling)} bowlers by credited wickets. Their economy is "
        f"{pdata['Economy']:.2f} runs per six legal balls, compared with a "
        f"bowler median of {median_economy:.2f}. Wides and no-balls do not count "
        "as legal balls; byes and leg-byes are excluded from runs charged to the bowler."
    )


    st.subheader("Economy Gauge")

    gauge=go.Figure(go.Indicator(
        mode="gauge+number",
        value=pdata["Economy"],
        title={"text":"Economy"},
        gauge={
            "axis":{"range":[0,12]},
            "bar":{"color":"cyan"},
            "steps":[
                {"range":[0,4],"color":"green"},
                {"range":[4,6],"color":"yellow"},
                {"range":[6,8],"color":"orange"},
                {"range":[8,12],"color":"red"}
            ]
        }
    ))

    st.plotly_chart(gauge,use_container_width=True)



    st.subheader("🎯 Wickets vs Economy")

    fig=px.scatter(
        bowling,
        x="Economy",
        y="Wickets",
        size="Balls",
        color="Wickets",
        hover_name="bowler",
        template="plotly_dark"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.caption(
        "Each point is a bowler. Lower economy and higher credited wickets are "
        "desirable together; bubble size shows legal balls bowled, so small samples need caution."
    )

    st.markdown("---")

    st.subheader("🥧 Top 10 Wicket Share")

    fig2=px.pie(
        bowling.sort_values(
            "Wickets",
            ascending=False
        ).head(10),
        values="Wickets",
        names="bowler",
        hole=0.55,
        template="plotly_dark"
    )

    st.plotly_chart(fig2,use_container_width=True)

    

    st.subheader("🌳 Bowling Treemap")

    fig3=px.treemap(
        bowling.sort_values("Wickets", ascending=False).head(30),
        path=["bowler"],
        values="Wickets",
        color="Economy",
        color_continuous_scale="RdYlGn_r"
    )

    st.plotly_chart(fig3,use_container_width=True)

    

    st.subheader("🏆 Top Bowlers")

    st.dataframe(
        bowling.sort_values(
            "Wickets",
            ascending=False
        ).head(20),
        use_container_width=True
    )

    csv=bowling.to_csv(index=False).encode()

    st.download_button(
        "⬇ Download Bowling Statistics",
        csv,
        "Bowling_Analytics.csv",
        "text/csv"
    )
    
    #--- head to head analytics
    
elif page=="⚔️ Head to Head":

    st.title("⚔️ CricIQ Head-to-Head Analytics")
    st.markdown("Compare batting and bowling performance of two players.")

    # ==============================
    # Player Selection
    # ==============================

    players = sorted(df["batter"].dropna().unique())

    col1, col2 = st.columns(2)

    with col1:
        p1 = st.selectbox(
            "🏏 Player 1",
            players,
            key="player1"
        )

    with col2:
        p2 = st.selectbox(
            "🏏 Player 2",
            players,
            index=1 if len(players) > 1 else 0,
            key="player2"
        )

    

    left, right = st.columns(2)

    with left:

        st.markdown(f"""
        <div style="
        background:#1E293B;
        padding:20px;
        border-radius:18px;
        text-align:center;
        border:2px solid #22c55e;
        ">

        <h2>{p1}</h2>

        </div>
        """, unsafe_allow_html=True)

    with right:

        st.markdown(f"""
        <div style="
        background:#1E293B;
        padding:20px;
        border-radius:18px;
        text-align:center;
        border:2px solid #3b82f6;
        ">

        <h2>{p2}</h2>

        </div>
        """, unsafe_allow_html=True)

    

    tab1, tab2 = st.tabs(["Batting", "Bowling"])
    
    left, right = st.columns(2)

    

    # -------------------------------
    # Batting
    # -------------------------------

    with tab1:

        batting_events = df.copy()
        batting_events["Ball Faced"] = numeric_column(
            batting_events, "extras_wides"
        ).eq(0).astype(int)
        batting = (
            batting_events.groupby("batter")
            .agg(
                Runs=("runs_batter","sum"),
                Balls=("Ball Faced","sum"),
                Fours=("runs_batter",lambda x:(x==4).sum()),
                Sixes=("runs_batter",lambda x:(x==6).sum())
            )
            .reset_index()
        )

        batting["Strike Rate"] = (
            batting["Runs"] /
            batting["Balls"] *100
        ).round(2)

        b1 = batting[
            batting["batter"]==p1
        ]

        b2 = batting[
            batting["batter"]==p2
        ]

        compare = pd.DataFrame({

            "Metric":[
                "Runs",
                "Balls",
                "Strike Rate",
                "Fours",
                "Sixes"
            ],

            p1:[
                b1["Runs"].iloc[0],
                b1["Balls"].iloc[0],
                b1["Strike Rate"].iloc[0],
                b1["Fours"].iloc[0],
                b1["Sixes"].iloc[0]
            ],

            p2:[
                b2["Runs"].iloc[0],
                b2["Balls"].iloc[0],
                b2["Strike Rate"].iloc[0],
                b2["Fours"].iloc[0],
                b2["Sixes"].iloc[0]
            ]

        })

        st.subheader("Comparison Table")

        st.dataframe(compare,use_container_width=True)

        

        
    # -------------------------------
    # Bowling
    # -------------------------------

        with tab2:

          bowling = summarize_bowling(df)

          bowl = bowling[
            bowling["bowler"].isin([p1,p2])
        ]

          st.subheader("Bowling Comparison")

          st.dataframe(
            bowl,
            use_container_width=True
        )

          
# ============================================================
# 🫧 Bubble Chart
# ============================================================

    
    st.subheader("🫧 Batting Bubble Comparison")

    bubble = pd.DataFrame({

    "Player":[p1,p2],

    "Runs":[
        b1["Runs"].iloc[0],
        b2["Runs"].iloc[0]
    ],

    "Strike Rate":[
        b1["Strike Rate"].iloc[0],
        b2["Strike Rate"].iloc[0]
    ],

    "Balls":[
        b1["Balls"].iloc[0],
        b2["Balls"].iloc[0]
    ],

    "Fours":[
        b1["Fours"].iloc[0],
        b2["Fours"].iloc[0]
    ]

})

    fig = px.scatter(

    bubble,

    x="Strike Rate",

    y="Runs",

    size="Balls",

    color="Player",

    hover_name="Player",

    hover_data=["Fours"],

    size_max=60,

    title="Runs vs Strike Rate"

)

    st.plotly_chart(fig,use_container_width=True)

# ============================================================
# 🍩 Donut Charts
# ============================================================
    

    c1, c2 = st.columns(2)

# ==========================
# Runs Share
# ==========================
    with c1:

     st.subheader("🏏 Runs Share")

     fig1 = px.pie(
        bubble,
        names="Player",
        values="Runs",
        hole=0.65
    )

     fig1.update_traces(textinfo="percent+label")

     st.plotly_chart(
        fig1,
        use_container_width=True,
        key="runs_share"
    )

# ==========================
# Wickets Share
# ==========================
    with c2:

     st.subheader("🎯 Wickets Share")

     wicket_df = pd.DataFrame({
        "Player": [p1, p2],
        "Wickets": [
            bowl.loc[bowl["bowler"] == p1, "Wickets"].sum(),
            bowl.loc[bowl["bowler"] == p2, "Wickets"].sum()
        ]
    })

     fig2 = px.pie(
        wicket_df,
        names="Player",
        values="Wickets",
        hole=0.65
    )

     fig2.update_traces(textinfo="percent+label")

     st.plotly_chart(
        fig2,
        use_container_width=True,
        key="wickets_share"
    )
# ============================================================
# 🌳 Treemap
# ============================================================

    
    st.subheader("🌳 Overall Statistics Treemap")

    tree = pd.DataFrame({

    "Player":[

        p1,p1,p1,p1,

        p2,p2,p2,p2

    ],

    "Metric":[

        "Runs",

        "Strike Rate",

        "Fours",

        "Sixes",

        "Runs",

        "Strike Rate",

        "Fours",

        "Sixes"

    ],

    "Value":[

        b1["Runs"].iloc[0],

        b1["Strike Rate"].iloc[0],

        b1["Fours"].iloc[0],

        b1["Sixes"].iloc[0],

        b2["Runs"].iloc[0],

        b2["Strike Rate"].iloc[0],

        b2["Fours"].iloc[0],

        b2["Sixes"].iloc[0]

    ]

})

    fig = px.treemap(

    tree,

    path=["Player","Metric"],

    values="Value",

    color="Value",

    color_continuous_scale="Viridis"

)

    st.plotly_chart(
    fig,
    use_container_width=True
)
# ============================================================
# ☀️ Sunburst Chart
# ============================================================

    

# ============================================================
# 🎛 Parallel Coordinates
# ============================================================

    
    st.subheader("🎛 Parallel Coordinates Comparison")

    w1 = bowl.loc[bowl["bowler"]==p1,"Wickets"].sum()
    w2 = bowl.loc[bowl["bowler"]==p2,"Wickets"].sum()

    parallel = pd.DataFrame({
        "ID":[1,2],
        "Player":[p1,p2],
        "Runs":[b1["Runs"].iloc[0],b2["Runs"].iloc[0]],
        "Balls":[b1["Balls"].iloc[0],b2["Balls"].iloc[0]],
        "Strike Rate":[b1["Strike Rate"].iloc[0],b2["Strike Rate"].iloc[0]],
        "Fours":[b1["Fours"].iloc[0],b2["Fours"].iloc[0]],
        "Sixes":[b1["Sixes"].iloc[0],b2["Sixes"].iloc[0]],
        "Wickets":[w1,w2]
    })

    

# ============================================================
# Data-based Summary
# ============================================================

    
    st.subheader("📊 Data-based Match-up Summary")

    summary=[]

    if b1["Runs"].iloc[0] > b2["Runs"].iloc[0]:
     summary.append(f"🏏 {p1} has scored more runs.")
    else:
     summary.append(f"🏏 {p2} has scored more runs.")

    if b1["Strike Rate"].iloc[0] > b2["Strike Rate"].iloc[0]:
     summary.append(f"⚡ {p1} has a better strike rate.")
    else:
     summary.append(f"⚡ {p2} has a better strike rate.")

    w1 = bowl.loc[bowl["bowler"]==p1,"Wickets"].sum()
    w2 = bowl.loc[bowl["bowler"]==p2,"Wickets"].sum()

    if w1 > w2:
     summary.append(f"🎯 {p1} has taken more wickets.")
    elif w2 > w1:
     summary.append(f"🎯 {p2} has taken more wickets.")
    else:
     summary.append("🎯 Both players have taken the same number of wickets.")

    for item in summary:
     st.success(item)

    st.caption(
        "These are career-to-date totals in the selected format, not a prediction "
        "or a comparison adjusted for matches played. Economy uses legal balls and "
        "bowler-charged runs; the summary above is descriptive and is not a trained model."
    )

# ============================================================
# Metric comparison
# ============================================================

    
    st.subheader("📊 How to interpret this comparison")
    st.info(
        f"{p1}: {int(b1['Runs'].iloc[0]):,} runs at a strike rate of "
        f"{b1['Strike Rate'].iloc[0]:.2f}, with {int(w1)} credited wickets. "
        f"{p2}: {int(b2['Runs'].iloc[0]):,} runs at a strike rate of "
        f"{b2['Strike Rate'].iloc[0]:.2f}, with {int(w2)} credited wickets. "
        "Runs, strike rate and wickets measure different things, so the app shows "
        "them separately instead of combining them into an arbitrary winner score."
    )

# ============================================================
# 📥 Download Report
# ============================================================

    

    report = parallel.drop(columns=["ID"])

    csv = report.to_csv(index=False).encode()

    st.download_button(

    "📥 Download Comparison Report",

    csv,

    "head_to_head_report.csv",

    "text/csv"

)
    
    #----- team analysis-------
elif page == "🏆 Team Analysis":

    st.title("🏆 Team Analysis Dashboard")

    # ----------------------------
    # Prepare Data
    # ----------------------------
    team1 = matches["team1"].value_counts()
    team2 = matches["team2"].value_counts()

    team_matches = team1.add(team2, fill_value=0)

    team_df = pd.DataFrame({
        "Team": team_matches.index,
        "Matches": team_matches.values
    }).sort_values("Matches", ascending=False)

    # ----------------------------
    # Dashboard Cards
    # ----------------------------

    total_teams = team_df.shape[0]
    total_matches = int(team_df["Matches"].sum() / 2)
    top_team = team_df.iloc[0]["Team"]

    c1, c2, c3 = st.columns(3)

    c1.metric("🏏 Teams", total_teams)
    c2.metric("📅 Matches", total_matches)
    c3.metric("🥇 Top Team", top_team)

    

    # ----------------------------
    # Treemap
    # ----------------------------

    st.subheader("🌳 Team Distribution")

    fig_tree = px.treemap(
        team_df,
        path=["Team"],
        values="Matches",
        color="Matches",
        color_continuous_scale="Viridis"
    )

    st.plotly_chart(
        fig_tree,
        use_container_width=True
    )

    # ----------------------------
    # Donut Chart + Horizontal Bar
    # ----------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🍩 Match Share")

        fig_pie = px.pie(
            team_df.head(10),
            names="Team",
            values="Matches",
            hole=0.6
        )

        fig_pie.update_traces(
            textinfo="percent+label"
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

    with col2:

        st.subheader("📊 Matches Played")

        fig_bar = px.bar(
            team_df.head(10),
            y="Team",
            x="Matches",
            orientation="h",
            color="Matches",
            text="Matches",
            color_continuous_scale="Turbo"
        )

        fig_bar.update_layout(
            yaxis=dict(categoryorder="total ascending")
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )

    

    # ----------------------------
    # Interactive Table
    # ----------------------------

    
# =====================================================
# ⚔️ Team Comparison
# =====================================================


    st.subheader("⚔️ Team Comparison")

    col1, col2 = st.columns(2)

    with col1:
     team_a = st.selectbox(
        "Select Team 1",
        sorted(team_df["Team"]),
        key="teamA"
    )

    with col2:
     team_b = st.selectbox(
        "Select Team 2",
        sorted(team_df["Team"]),
        index=1,
        key="teamB"
    )

    def team_stats(team):

     played = matches[
        (matches["team1"] == team) |
        (matches["team2"] == team)
    ]

     wins = 0

     if winner_col:
        wins = (
            played[winner_col] == team
        ).sum()

     return {

        "Team": team,

        "Played": len(played),

        "Wins": wins,

        "Losses": len(played)-wins,

        "Win %": round(
            wins/len(played)*100,
            2
        ) if len(played)>0 else 0

    }

    s1 = team_stats(team_a)
    s2 = team_stats(team_b)

    compare = pd.DataFrame({

    "Metric":[
        "Played",
        "Wins",
        "Losses",
        "Win %"
    ],

    team_a:[
        s1["Played"],
        s1["Wins"],
        s1["Losses"],
        s1["Win %"]
    ],

    team_b:[
        s2["Played"],
        s2["Wins"],
        s2["Losses"],
        s2["Win %"]
    ]

})
    st.dataframe(
    compare,
    use_container_width=True,
    hide_index=True
)

    

    

# =====================================================
# 🏟 Venue Analysis
# =====================================================

    
    st.subheader("🏟 Favourite Venues")

    venue_team = (

    matches[
        (matches["team1"]==team_a) |
        (matches["team2"]==team_a)
    ]

    .groupby("venue")

    .size()

    .reset_index(name="Matches")

    .sort_values(
        "Matches",
        ascending=False
    )

    .head(10)

)

    fig = px.bar(

    venue_team,

    x="venue",

    y="Matches",

    color="Matches",

    text="Matches",

    title=f"{team_a} Most Played Venues"

)

    st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# 🏆 Win Percentage Gauge
# =====================================================

    
    st.subheader("🏆 Win Percentage")

    fig = go.Figure()

    fig.add_trace(go.Indicator(

    mode="gauge+number",

    value=s1["Win %"],

    title={"text":team_a},

    domain={"x":[0,0.45],"y":[0,1]}

))

    fig.add_trace(go.Indicator(

    mode="gauge+number",

    value=s2["Win %"],

    title={"text":team_b},

    domain={"x":[0.55,1],"y":[0,1]}

))

    fig.update_layout(height=350)

    st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# Team insights
# =====================================================

    
    st.subheader("📊 Team Insights")

    if s1["Win %"] > s2["Win %"]:
     better = team_a
    elif s2["Win %"] > s1["Win %"]:
     better = team_b
    else:
     better = None

    if better:
     st.success(f"🏆 {better} has the higher recorded win percentage.")
    else:
     st.info("🏆 The teams have the same recorded win percentage.")

    win_rate_gap = abs(s1["Win %"] - s2["Win %"])
    st.info(
        f"**Interpretation:** {team_a} has {s1['Win %']:.1f}% wins from "
        f"{s1['Played']} matches; {team_b} has {s2['Win %']:.1f}% from "
        f"{s2['Played']} matches. The gap is {win_rate_gap:.1f} percentage "
        "points. A larger match sample gives a more stable comparison; seasons "
        "and opponent strength are not adjusted here."
    )

    if s1["Wins"] > s2["Wins"]:
     st.info(f"✅ {team_a} has won more matches.")
    elif s2["Wins"] > s1["Wins"]:
     st.info(f"✅ {team_b} has won more matches.")
    else:
     st.info("🤝 Both teams have the same number of wins.")

# =====================================================
# ⭐ Team Rankings
# =====================================================

    
    st.subheader("⭐ Team Rankings")

    ranking = []

    for team in sorted(team_df["Team"]):

     played = matches[
        (matches["team1"]==team) |
        (matches["team2"]==team)
    ]

     wins = (
        (played[winner_col]==team).sum()
        if winner_col else 0
    )

     ranking.append({

        "Team":team,

        "Played":len(played),

        "Wins":wins,

        "Win %":round(
            wins/len(played)*100,
            2
        ) if len(played)>0 else 0

    })

    ranking = pd.DataFrame(ranking)

    ranking = ranking.sort_values(
    "Win %",
    ascending=False
)

    st.dataframe(
    ranking,
    use_container_width=True,
    hide_index=True
)


# =====================================================
# 📈 Season-wise Matches
# =====================================================

    
# =====================================================
# 🏟 Venue Analysis
# =====================================================

elif page == "🏟️ Venue Analysis":

    st.title("🏟️ Venue Intelligence Dashboard")

    winner_col = None

    if "winner" in matches.columns:
        winner_col = "winner"
    elif "outcome_winner" in matches.columns:
        winner_col = "outcome_winner"

    # ======================================
    # Filters
    # ======================================

    c1, c2 = st.columns([2,1])

    with c1:

        venue_search = st.selectbox(
            "🏟 Select Venue",
            sorted(matches["venue"].dropna().unique())
        )

    with c2:

        if "city" in matches.columns:

            city_list = ["All"] + sorted(
                matches["city"].dropna().unique()
            )

            city_filter = st.selectbox(
                "📍 City",
                city_list
            )

        else:
            city_filter = "All"

    venue_df = matches[
        matches["venue"] == venue_search
    ]

    if city_filter != "All":
        venue_df = venue_df[
            venue_df["city"] == city_filter
        ]

    # ======================================
    # KPI Cards
    # ======================================

    matches_played = venue_df["match_id"].nunique()

    teams = pd.concat([
        venue_df["team1"],
        venue_df["team2"]
    ]).nunique()

    avg_runs = 0

    if len(venue_df) > 0:

        venue_runs = (
            df.groupby("match_id")["runs_total"]
            .sum()
            .reset_index()
        )

        venue_runs = venue_runs.merge(
            venue_df[["match_id"]],
            on="match_id"
        )

        avg_runs = round(
            venue_runs["runs_total"].mean(),
            1
        )

    top_team = "-"

    if winner_col and len(venue_df) > 0:

        top_team = (
            venue_df[winner_col]
            .value_counts()
            .idxmax()
        )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🏏 Matches",
        matches_played
    )

    c2.metric(
        "👥 Teams",
        teams
    )

    c3.metric(
        "🔥 Avg Runs",
        avg_runs
    )

    c4.metric(
        "🏆 Best Team",
        top_team
    )

    format_average = (
        df.groupby("match_id")["runs_total"].sum().mean()
        if not df.empty else 0
    )
    venue_difference = avg_runs - format_average
    st.info(
        f"**Interpretation:** this venue has {matches_played} matches in the "
        f"selected data and averages {avg_runs:.1f} total runs per match, "
        f"{abs(venue_difference):.1f} {'above' if venue_difference >= 0 else 'below'} "
        f"the format-wide average of {format_average:.1f}. {top_team} is the "
        "most frequent winner in this venue sample. This describes past results; "
        "it does not establish that the venue caused the outcomes."
    )



    # ======================================
    # Venue Profile Card
    # ======================================

    city = "-"

    if "city" in venue_df.columns and len(venue_df):

        city = venue_df["city"].iloc[0]

    season_text = "-"

    if "season" in venue_df.columns:

        season_text = (
            f"{venue_df['season'].min()} - "
            f"{venue_df['season'].max()}"
        )

    st.markdown(f"""
    <div style="
    background:#0F172A;
    padding:25px;
    border-radius:18px;
    border:1px solid #334155;
    ">

    <h2 style="color:#38BDF8;">
    🏟 {venue_search}
    </h2>

    <hr>

    <h4>📍 City : {city}</h4>

    <h4>🏏 Matches : {matches_played}</h4>

    <h4>🔥 Average Runs : {avg_runs}</h4>

    <h4>🏆 Most Successful Team : {top_team}</h4>

    <h4>📅 Seasons : {season_text}</h4>

    </div>

    """, unsafe_allow_html=True)

    
    
    # ==========================================================
# 🫧 Bubble Chart
# ==========================================================

    st.subheader("🫧 Venue Performance Analysis")

    venue_stats = (
    df.groupby("match_id")["runs_total"]
    .sum()
    .reset_index()
)

    venue_stats = venue_stats.merge(
    matches[["match_id", "venue"]],
    on="match_id",
    how="left"
)

    venue_stats = (
    venue_stats
    .groupby("venue")
    .agg(
        Average_Runs=("runs_total", "mean"),
        Matches=("runs_total", "count"),
        Highest_Score=("runs_total", "max")
    )
    .reset_index()
)

    fig = px.scatter(

    venue_stats,

    x="Average_Runs",

    y="Matches",

    size="Highest_Score",

    color="Average_Runs",

    hover_name="venue",

    size_max=60,

    color_continuous_scale="Turbo",

    title="Venue Performance Bubble Chart"
)

    fig.update_layout(height=650)

    st.plotly_chart(fig, use_container_width=True)



    

# ==========================================================
# 🍩 Match Share
# ==========================================================

    

    col1, col2 = st.columns(2)

    with col1:

     st.subheader("🍩 Match Share")

     fig1 = px.pie(

        venue_stats.sort_values(
            "Matches",
            ascending=False
        ).head(10),

        names="venue",

        values="Matches",

        hole=0.6

    )

     fig1.update_traces(
        textinfo="percent+label"
    )

     st.plotly_chart(
        fig1,
        use_container_width=True
    )

    with col2:

     st.subheader("🥇 Highest Scoring Venues")

     fig2 = px.bar(

        venue_stats

        .sort_values(
            "Average_Runs",
            ascending=False
        )

        .head(10),

        y="venue",

        x="Average_Runs",

        orientation="h",

        color="Average_Runs",

        text_auto=".1f",

        color_continuous_scale="Turbo"

    )

     fig2.update_layout(
        yaxis=dict(
            categoryorder="total ascending"
        ),
        height=550
    )

     st.plotly_chart(
        fig2,
        use_container_width=True
    )
    

# ==========================================================
# 🌳 Venue Treemap
# ==========================================================

    st.markdown("---")
    st.subheader("🌳 Venue Importance")

    tree = venue_stats.copy()

    fig = px.treemap(

    tree,

    path=["venue"],

    values="Matches",

    color="Average_Runs",

    color_continuous_scale="Viridis"

)

    fig.update_layout(height=650)

    st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# 📦 Runs Distribution (Box Plot)
# ==========================================================

    
    st.subheader("📦 Runs Distribution Across Venues")

    runs_box = (
    df.groupby("match_id")["runs_total"]
    .sum()
    .reset_index()
)

    runs_box = runs_box.merge(
    matches[["match_id", "venue"]],
    on="match_id",
    how="left"
)

    top10 = (
    runs_box["venue"]
    .value_counts()
    .head(10)
    .index
)

    runs_box = runs_box[
    runs_box["venue"].isin(top10)
]

    fig = px.box(

    runs_box,

    x="venue",

    y="runs_total",

    color="venue",

    points="all"

)

    fig.update_layout(
    height=650,
    xaxis_title="Venue",
    yaxis_title="Total Match Runs"
)

    st.plotly_chart(
    fig,
    use_container_width=True
)
    # ==========================================================
# ⚔️ Venue Comparison Dashboard
# ==========================================================

    
    st.title("⚔️ Venue Comparison")

    col1, col2 = st.columns(2)

    with col1:
     venue1 = st.selectbox(
        "🏟 Venue 1",
        sorted(venue_stats["venue"]),
        key="venue1_compare"
    )

    with col2:
     venue2 = st.selectbox(
        "🏟 Venue 2",
        sorted(venue_stats["venue"]),
        index=1,
        key="venue2_compare"
    )


    def venue_summary(name):

     venue_matches = matches[
        matches["venue"] == name
    ]

     played = len(venue_matches)

     runs = (
        df[df["match_id"].isin(
            venue_matches["match_id"]
        )]
        .groupby("match_id")["runs_total"]
        .sum()
        .mean()
    )

     highest = (
        df[df["match_id"].isin(
            venue_matches["match_id"]
        )]
        .groupby("match_id")["runs_total"]
        .sum()
        .max()
    )

     best_team = "-"

     if winner_col:

         if len(venue_matches) > 0:

            best_team = (
                venue_matches[winner_col]
                .value_counts()
                .idxmax()
            )

     return {

        "Venue": name,

        "Matches": played,

        "Average Runs": round(runs,1),

        "Highest Score": highest,

        "Best Team": best_team

    }


    v1 = venue_summary(venue1)
    v2 = venue_summary(venue2)
    
    compare = pd.DataFrame({

    "Metric":[
        "Matches",
        "Average Runs",
        "Highest Score",
        "Best Team"
    ],

    venue1:[
        v1["Matches"],
        v1["Average Runs"],
        v1["Highest Score"],
        v1["Best Team"]
    ],

    venue2:[
        v2["Matches"],
        v2["Average Runs"],
        v2["Highest Score"],
        v2["Best Team"]
    ]

})

    st.dataframe(
    compare,
    use_container_width=True,
    hide_index=True
)
    chart = pd.DataFrame({

    "Venue":[
        venue1,
        venue2
    ],

    "Average Runs":[
        v1["Average Runs"],
        v2["Average Runs"]
    ],

    "Highest Score":[
        v1["Highest Score"],
        v2["Highest Score"]
    ]

})

    fig = px.bar(

    chart,

    x="Venue",

    y=[
        "Average Runs",
        "Highest Score"
    ],

    barmode="group",

    text_auto=True,

    color_discrete_sequence=[
        "#00C9A7",
        "#FF8066"
    ]

)

    st.plotly_chart(
    fig,
    use_container_width=True
)
    
    st.subheader("📊 Venue Insights")

    if v1["Average Runs"] > v2["Average Runs"]:

     st.success(
        f"🔥 {venue1} is the higher scoring venue."
    )

    elif v2["Average Runs"] > v1["Average Runs"]:

     st.success(
        f"🔥 {venue2} is the higher scoring venue."
    )
    else:
     st.info("The two venues have the same average match total in this dataset.")

    if v1["Matches"] > v2["Matches"]:

     st.info(
        f"📅 {venue1} has hosted more matches."
    )

    elif v2["Matches"] > v1["Matches"]:

     st.info(
        f"📅 {venue2} has hosted more matches."
    )
    else:
     st.info("The two venues have the same number of matches in this dataset.")

    st.caption(
        f"Average match total: {venue1} {v1['Average Runs']:.1f} from "
        f"{v1['Matches']} matches; {venue2} {v2['Average Runs']:.1f} from "
        f"{v2['Matches']} matches. Differences may reflect different sample sizes "
        "and seasons, so use match count alongside the averages."
    )

    st.warning(
    f"🏆 Most successful team at {venue1}: {v1['Best Team']}"
)

    st.warning(
    f"🏆 Most successful team at {venue2}: {v2['Best Team']}"
)
    # ==========================================================
    # 🗺️ Interactive Venue Map
    # ==========================================================

    st.subheader("🗺️ Interactive Cricket Venue Map")
    st.caption(
        "Each marker represents a mapped IPL ground. Marker size shows matches "
        "in the selected format; color shows average total runs per match. The "
        "venue table below keeps the ground names and statistics visible without hovering."
    )

    venue_locations = pd.DataFrame({
        "Venue": [
            "Wankhede Stadium", "Eden Gardens", "M Chinnaswamy Stadium",
            "MA Chidambaram Stadium, Chepauk", "Arun Jaitley Stadium",
            "Rajiv Gandhi International Stadium, Uppal", "Narendra Modi Stadium"
        ],
        "lat": [19.0176, 22.5646, 12.9788, 13.0627, 28.6379, 17.4065, 23.0910],
        "lon": [72.8562, 88.3433, 77.5996, 80.2794, 77.2433, 78.5500, 72.5970]
    })

    def map_venue_name(name):
        normalized = str(name).lower().replace(".", "")
        if "wankhede" in normalized:
            return "Wankhede Stadium"
        if "eden gardens" in normalized:
            return "Eden Gardens"
        if "chinnaswamy" in normalized:
            return "M Chinnaswamy Stadium"
        if "chidambaram" in normalized or "chepauk" in normalized:
            return "MA Chidambaram Stadium, Chepauk"
        if "feroz shah kotla" in normalized or "arun jaitley" in normalized:
            return "Arun Jaitley Stadium"
        if "rajiv gandhi" in normalized:
            return "Rajiv Gandhi International Stadium, Uppal"
        if "narendra modi" in normalized or "sardar patel" in normalized:
            return "Narendra Modi Stadium"
        return None

    if "venue" in matches.columns:
        map_runs = (
            df.groupby("match_id")["runs_total"]
            .sum()
            .rename("Match_Runs")
            .reset_index()
            .merge(matches[["match_id", "venue"]], on="match_id", how="inner")
            .dropna(subset=["venue"])
        )
        map_runs["Mapped_Venue"] = map_runs["venue"].map(map_venue_name)
        map_runs = map_runs.dropna(subset=["Mapped_Venue"])
        map_venue_stats = (
            map_runs.groupby("Mapped_Venue")
            .agg(
                Matches=("match_id", "nunique"),
                Average_Runs=("Match_Runs", "mean"),
                Highest_Score=("Match_Runs", "max")
            )
            .reset_index()
        )
        map_points = venue_locations.merge(
            map_venue_stats,
            left_on="Venue",
            right_on="Mapped_Venue",
            how="inner"
        )

        if map_points.empty:
            st.info("No matches in this format are recorded at the grounds currently mapped.")
        else:
            map_points["Map_Label"] = map_points["Venue"].replace({
                "M Chinnaswamy Stadium": "Chinnaswamy",
                "MA Chidambaram Stadium, Chepauk": "Chepauk",
                "Rajiv Gandhi International Stadium, Uppal": "Rajiv Gandhi",
                "Arun Jaitley Stadium": "Arun Jaitley",
                "Narendra Modi Stadium": "Narendra Modi"
            })
            map_fig = px.scatter_map(
                map_points,
                lat="lat",
                lon="lon",
                text="Map_Label",
                hover_name="Venue",
                hover_data={
                    "Matches": True,
                    "Average_Runs": ":.1f",
                    "Highest_Score": ":.0f",
                    "lat": False,
                    "lon": False
                },
                size="Matches",
                size_max=32,
                color="Average_Runs",
                center={"lat": 22.5, "lon": 78.5},
                zoom=3,
                height=600,
                color_continuous_scale="Turbo",
                map_style="open-street-map",
                labels={
                    "Matches": "Matches",
                    "Average_Runs": "Average runs per match",
                    "Highest_Score": "Highest match total"
                }
            )
            map_fig.update_layout(margin=dict(l=0, r=0, t=20, b=0))
            map_fig.update_traces(
                marker={"opacity": 0.85},
                textposition="top center",
                textfont={"size": 11, "color": "#111827"}
            )
            st.plotly_chart(map_fig, use_container_width=True)
            st.markdown("**Mapped venue details**")
            visible_venue_stats = map_points[[
                "Venue", "Matches", "Average_Runs", "Highest_Score"
            ]].sort_values("Matches", ascending=False).rename(columns={
                "Venue": "Stadium",
                "Matches": "Matches in selected format",
                "Average_Runs": "Average runs per match",
                "Highest_Score": "Highest match total"
            })
            st.dataframe(
                visible_venue_stats,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Average runs per match": st.column_config.NumberColumn(format="%.1f"),
                    "Highest match total": st.column_config.NumberColumn(format="%.0f")
                }
            )
    else:
        st.info("Venue data is unavailable, so the venue map cannot be drawn for this format.")

    st.subheader("🎯 Venue Rating")

    rating = min(

    100,

    round(avg_runs/4)

)

    fig = go.Figure(go.Indicator(

    mode="gauge+number",

    value=rating,

    title={"text":"Batting Friendly Rating"},

    gauge={

        "axis":{"range":[0,100]},

        "bar":{"color":"limegreen"},

        "steps":[

            {"range":[0,40],"color":"red"},

            {"range":[40,70],"color":"orange"},

            {"range":[70,100],"color":"green"}

        ]

    }

))

    fig.update_layout(height=350)

    st.plotly_chart(fig,use_container_width=True)
    


    st.subheader("📊 Venue Data Summary")

    highest = venue_stats.loc[
    venue_stats["Average_Runs"].idxmax()
]

    lowest = venue_stats.loc[
    venue_stats["Average_Runs"].idxmin()
]

    most_matches = venue_stats.loc[
    venue_stats["Matches"].idxmax()
]

    st.success(
f"""
🔥 Highest Scoring Venue

{highest['venue']}

Average Runs : {highest['Average_Runs']:.1f}
"""
)

    st.info(
f"""
📅 Most Active Venue

{most_matches['venue']}

Matches Hosted : {int(most_matches['Matches'])}
"""
)

    st.warning(
f"""
🛡️ Lowest Scoring Venue

{lowest['venue']}

Average Runs : {lowest['Average_Runs']:.1f}
"""
)
    

    csv = venue_stats.to_csv(index=False).encode()

    st.download_button( 

    "📥 Download Venue Report",

    csv,

    "Venue_Report.csv",

    "text/csv"

)
    
    st.subheader("🏆 Top Cricket Venues")

    top = venue_stats.sort_values(
    "Average_Runs",
    ascending=False
).head(10)

    for i, row in top.iterrows():

     medal = ""

    if i == top.index[0]:
        medal = "🥇"

    elif i == top.index[1]:
        medal = "🥈"

    elif i == top.index[2]:
        medal = "🥉"

    st.markdown(f"""
### {medal} {row['venue']}

🏏 Matches : **{int(row['Matches'])}**

🔥 Average Runs : **{row['Average_Runs']:.1f}**

🏆 Highest Score : **{int(row['Highest_Score'])}**

---
""")
#--player search---
elif page == "👤 Player Search":

    st.title("🔍 Player Search & Performance Analytics")

    player = st.selectbox(
        "Select Player",
        sorted(df["batter"].dropna().unique())
    )

    batting = df[df["batter"] == player]

    runs = batting["runs_batter"].sum()
    balls = int(numeric_column(batting, "extras_wides").eq(0).sum())

    sr = round((runs / balls) * 100, 2) if balls > 0 else 0

    bowling_summary = summarize_bowling(df)
    player_bowling = bowling_summary[
        bowling_summary["bowler"] == player
    ]
    wickets = int(player_bowling["Wickets"].sum())
    economy = (
        float(player_bowling["Economy"].iloc[0])
        if not player_bowling.empty else 0
    )

    st.subheader(f"🏏 {player}")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Runs", int(runs))
    c2.metric("Balls", int(balls))
    c3.metric("Strike Rate", sr)
    c4.metric("Wickets", wickets)
    c5.metric("Economy", economy)

    batter_totals = df.groupby("batter")["runs_batter"].sum().sort_values(ascending=False)
    batter_rank = int(batter_totals.rank(method="min", ascending=False)[
        batter_totals.index == player
    ].iloc[0])
    format_median_sr = (
        (df.groupby("batter")["runs_batter"].sum()
         / df.assign(_balls=numeric_column(df, "extras_wides").eq(0).astype(int))
         .groupby("batter")["_balls"].sum().replace(0, 1) * 100)
        .median()
    )
    st.info(
        f"**Player profile:** {player} ranks {batter_rank} by runs among "
        f"{len(batter_totals)} batters in {format_selected}. Their strike rate "
        f"is {sr:.2f}, against a format median of {format_median_sr:.2f}; they "
        f"have {wickets} credited wickets. These totals cover the loaded data "
        "and are not adjusted for appearances or role."
    )

    st.markdown("---")

    # =============================
    # Donut + Boundary Analysis
    # =============================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🏏 Scoring vs Dot Deliveries")

        dot_balls = int(
            (batting["runs_batter"].eq(0)
             & numeric_column(batting, "extras_wides").eq(0)).sum()
        )
        scoring_balls = max(balls - dot_balls, 0)

        fig = px.pie(
            names=["Scoring Deliveries", "Dot Deliveries"],
            values=[scoring_balls, dot_balls],
            hole=0.6,
            color_discrete_sequence=[
                "#00CC96",
                "#EF553B"
            ]
        )

        fig.update_traces(
            textinfo="percent+label"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        st.subheader("🚀 Boundary Analysis")

        fours = (batting["runs_batter"] == 4).sum()
        sixes = (batting["runs_batter"] == 6).sum()

        boundary_df = pd.DataFrame({

            "Boundary": [
                "Fours",
                "Sixes"
            ],

            "Count": [
                fours,
                sixes
            ]

        })

        fig = px.bar(

            boundary_df,

            x="Boundary",

            y="Count",

            color="Boundary",

            text="Count"

        )

        fig.update_layout(showlegend=False)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    

    # =============================
    # Match-wise Runs
    # =============================

    st.subheader("📈 Match-wise Runs")

    player_runs = (

        batting.groupby("match_id")["runs_batter"]

        .sum()

        .reset_index()

    )

    fig = px.area(

        player_runs,

        x="match_id",

        y="runs_batter",

        markers=True,

        title=f"{player} Match Performance"

    )

    fig.update_traces(
        line_color="#00CC96",
        fill="tozeroy"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("---")

    

    col1, col2 = st.columns(2)

# =============================
# Runs Distribution
# =============================
    with col1:

     st.subheader("🎯 Runs Distribution")

     fig1 = px.histogram(
        batting,
        x="runs_batter",
        nbins=8,
        color_discrete_sequence=["#636EFA"]
    )

     fig1.update_layout(
        xaxis_title="Runs Scored",
        yaxis_title="Frequency"
    )

     st.plotly_chart(
        fig1,
        use_container_width=True
    )

# =============================
# Scoring Pattern
# =============================
    with col2:

     st.subheader("🏏 Scoring Pattern")

     score_df = pd.DataFrame({

        "Runs": [
            "1 Run",
            "2 Runs",
            "3 Runs",
            "Four",
            "Six"
        ],

        "Count": [
            (batting["runs_batter"] == 1).sum(),
            (batting["runs_batter"] == 2).sum(),
            (batting["runs_batter"] == 3).sum(),
            (batting["runs_batter"] == 4).sum(),
            (batting["runs_batter"] == 6).sum()
        ]

    })

     fig2 = px.pie(
        score_df,
        names="Runs",
        values="Count",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2
    )

     fig2.update_traces(textinfo="percent+label")

     st.plotly_chart(
        fig2,
        use_container_width=True
    )

    

    # =============================
    # Data-based interpretation
    # =============================

    st.subheader("📊 Data-based Interpretation")
    boundary_runs = int(4 * fours + 6 * sixes)
    boundary_share = boundary_runs / runs * 100 if runs else 0
    dot_rate = dot_balls / balls * 100 if balls else 0
    st.info(
        f"In {format_selected}, boundaries account for {boundary_share:.1f}% "
        f"of {player}'s runs ({fours} fours and {sixes} sixes). Dot deliveries "
        f"make up {dot_rate:.1f}% of balls faced. Together, these show how the "
        "player builds scoring output; they do not account for match conditions "
        "or opposition quality."
    )
    if not player_bowling.empty:
        st.caption(
            f"Bowling context: {player} has {wickets} credited wickets at an "
            f"economy of {economy:.2f} runs per six legal balls in this dataset."
        )
    else:
        st.caption("No bowling deliveries for this player appear in the selected format data.")
    
