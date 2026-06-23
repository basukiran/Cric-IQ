import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup

import streamlit as st
import pandas as pd
import os

# -----------------------------
# SESSION STATE
# -----------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# -----------------------------
# CREATE USERS FILE
# -----------------------------

if not os.path.exists("users.csv"):

    users_df = pd.DataFrame(
        columns=["username", "password"]
    )

    users_df.to_csv(
        "users.csv",
        index=False
    )

# -----------------------------
# LOGIN / SIGNUP PAGE
# -----------------------------

def auth_page():

    st.title("🏏 CricIQ Authentication")

    menu = st.selectbox(
        "Select Option",
        ["Login", "Signup"]
    )

    # -----------------------------
    # LOGIN
    # -----------------------------

    if menu == "Login":

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            users = pd.read_csv(
                "users.csv"
            )

            valid_user = users[
                (users["username"] == username)
                &
                (users["password"] == password)
            ]

            if len(valid_user) > 0:

                st.session_state.logged_in = True
                st.session_state.username = username

                st.success(
                    "Login Successful"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid Username or Password"
                )

    # -----------------------------
    # SIGNUP
    # -----------------------------

    elif menu == "Signup":

        new_user = st.text_input(
            "Create Username"
        )

        new_pass = st.text_input(
            "Create Password",
            type="password"
        )

        if st.button("Create Account"):

            users = pd.read_csv(
                "users.csv"
            )

            if new_user in users["username"].values:

                st.warning(
                    "Username already exists"
                )

            else:

                users.loc[len(users)] = [
                    new_user,
                    new_pass
                ]

                users.to_csv(
                    "users.csv",
                    index=False
                )

                st.success(
                    "Account Created Successfully"
                )

# -----------------------------
# SHOW LOGIN PAGE
# -----------------------------

if not st.session_state.logged_in:

    auth_page()
    st.stop()

# -----------------------------
# SIDEBAR USER INFO
# -----------------------------

st.sidebar.success(
    f"👋 Welcome {st.session_state.username}"
)

# -----------------------------
# LOGOUT BUTTON
# -----------------------------

if st.sidebar.button("🚪 Logout"):

    st.session_state.logged_in = False
    st.session_state.username = ""

    st.rerun()
    

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


# -------------------------------
# SIDEBAR
# -------------------------------

st.sidebar.title("🏏 CricIQ")

format_selected = st.sidebar.selectbox(
    "Select Format",
    ["IPL", "ODI", "T20I", "TEST"]
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Live Scores",
        "Dataset Analyzer",
        "Player Search",
        "Batting Analytics",
        "Bowling Analytics",
        "Head to Head",
        "Team Analysis",
        "Venue Analysis",
        "Season Trends",
        "Match Explorer"
    ]
    
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

if page == "Dashboard":

    st.markdown("""
    <style>

    .hero-title{
        font-size:70px;
        font-weight:800;
        color:white;
        line-height:1;
    }

    .hero-green{
        color:#57E25F;
    }

    .hero-text{
        font-size:24px;
        color:#d1d5db;
        margin-top:20px;
    }

    .about-box{
        background:#111827;
        padding:30px;
        border-radius:20px;
        border:1px solid #374151;
        margin-top:40px;
    }

    .footer{
        text-align:center;
        color:gray;
        margin-top:60px;
        padding:20px;
    }

    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.2,1])

    with col1:

        st.markdown("""
        <div class="hero-title">
        CRIC<span class="hero-green">IQ</span>
        </div>

        <div style="font-size:28px;color:#57E25F;
        margin-top:10px;">
        Cricket Intelligence Quotient
        </div>

        <div class="hero-text">
        AI-Powered Cricket Analytics Platform
        <br><br>

        Analyze player performance,
        team strategies, venue trends,
        match insights and live cricket scores
        across IPL, ODI, T20I and Test formats.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.success(
            "🚀 Use the sidebar to explore analytics, rankings, venue insights and live scores."
        )

    with col2:

        st.image(
            "dashboard.jpg",
            use_container_width=True
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="about-box">

    <h2 style="color:#57E25F;">
    ABOUT CRICIQ
    </h2>

    <p style="font-size:18px;color:#d1d5db;">

    CricIQ is a multi-format cricket analytics platform
    designed to provide intelligent insights from
    cricket datasets and live match information.

    The platform enables users to analyze batting,
    bowling, venue performance, team records,
    head-to-head comparisons and live cricket data
    through interactive visualizations.

    </p>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    

    st.markdown("""
    <div class="footer">

    📧 Email: criciq@gmail.com

    <br>

    📞 Contact: +91 XXXXX XXXXX

    <br>

    🔒 Privacy Policy

    <br><br>

    © 2026 CricIQ - Cricket Intelligence Quotient

    </div>
    """, unsafe_allow_html=True)
    #----Uploaded file option---
elif page == "Dataset Analyzer":

    st.title("📂 Smart Cricket Dataset Analyzer")

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

        st.markdown("---")

        # Column Information
        st.subheader("📋 Columns")

        st.write(list(df_upload.columns))

        st.markdown("---")

        # Missing Values Chart
        st.subheader("⚠️ Missing Values")

        missing = (
            df_upload.isnull()
            .sum()
            .reset_index()
        )

        missing.columns = [
            "Column",
            "Missing"
        ]

        fig = px.bar(
            missing,
            x="Column",
            y="Missing",
            title="Missing Values by Column"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

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

        # Categorical Columns
        categorical_cols = df_upload.select_dtypes(
            include="object"
        ).columns

        if len(categorical_cols) > 0:

            st.markdown("---")
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

        # Correlation Heatmap
        if len(numeric_cols) > 1:

            st.markdown("---")
            st.subheader("🔥 Correlation Analysis")

            corr = df_upload[
                numeric_cols
            ].corr()

            fig = px.imshow(
                corr,
                text_auto=True,
                aspect="auto",
                title="Correlation Matrix"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # AI-like Summary
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
    
elif page == "Live Scores":

    st.title("🏏 Live Cricket Scores")

    import requests

    API_KEY = "API_KEY"

    try:
        url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"

        response = requests.get(url)
        data = response.json()

        if data["status"] == "success":

            st.metric(
                "Live Matches",
                len(data["data"])
            )

            for match in data["data"]:

                st.markdown("---")

                st.markdown(f"""
                <div style="
                background:#1E293B;
                padding:20px;
                border-radius:15px;
                border:1px solid #374151;
                ">
                <h3>🏏 {match.get('name','Match')}</h3>
                <p><b>Status:</b> {match.get('status','N/A')}</p>
                <p><b>Match Type:</b> {match.get('matchType','N/A')}</p>
                <p><b>Venue:</b> {match.get('venue','N/A')}</p>
                </div>
                """, unsafe_allow_html=True)

                if "score" in match and match["score"]:

                    score_df = pd.DataFrame(match["score"])

                    st.dataframe(
                        score_df,
                        use_container_width=True
                    )

        else:
            st.error(data.get("reason", "No data found"))

    except Exception as e:
        st.error(f"Error: {e}")

# -------------------------------
# BATTING ANALYTICS
# -------------------------------

elif page == "Batting Analytics":

    st.title("🏏 Batting Analytics")

    batting = (
        df.groupby("batter")
        .agg(
            Runs=("runs_batter", "sum"),
            Balls=("ball", "count")
        )
        .reset_index()
    )

    batting["Strike Rate"] = (
        batting["Runs"] / batting["Balls"] * 100
    ).round(2)

    player = st.selectbox(
        "Select Batter",
        sorted(batting["batter"].unique())
    )

    pdata = batting[batting["batter"] == player]

    col1, col2, col3 = st.columns(3)

    col1.metric("Runs", int(pdata["Runs"].iloc[0]))
    col2.metric("Balls", int(pdata["Balls"].iloc[0]))
    col3.metric("Strike Rate", pdata["Strike Rate"].iloc[0])

    st.markdown("---")

    st.subheader("Top Run Scorers")

    st.dataframe(
        batting.sort_values(
            "Runs",
            ascending=False
        ).head(20),
        use_container_width=True
    )

# -------------------------------
# BOWLING ANALYTICS
# -------------------------------

elif page == "Bowling Analytics":

    st.title("🎯 Bowling Analytics")

    if "player_out" not in df.columns:
        st.error("No wicket column found in dataset.")
        st.stop()

    bowling = (
        df.groupby("bowler")
        .agg(
            Balls=("ball", "count"),
            Runs=("runs_total", "sum"),
            Wickets=("player_out", lambda x: x.notna().sum())
        )
        .reset_index()
    )

    bowling["Overs"] = (
        bowling["Balls"] / 6
    ).round(1)

    bowling["Economy"] = (
        bowling["Runs"] /
        bowling["Overs"].replace(0, 1)
    ).round(2)

    player = st.selectbox(
        "Select Bowler",
        sorted(bowling["bowler"].unique())
    )

    pdata = bowling[bowling["bowler"] == player]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Wickets",
        int(pdata["Wickets"].iloc[0])
    )

    col2.metric(
        "Overs",
        pdata["Overs"].iloc[0]
    )

    col3.metric(
        "Economy",
        pdata["Economy"].iloc[0]
    )

    st.markdown("---")

    st.subheader("Top Wicket Takers")

    st.dataframe(
        bowling.sort_values(
            "Wickets",
            ascending=False
        ).head(20),
        use_container_width=True
    )

    fig = px.bar(
        bowling.sort_values(
            "Wickets",
            ascending=False
        ).head(10),
        x="bowler",
        y="Wickets",
        title="Top 10 Wicket Takers"
    )

    st.plotly_chart(fig, use_container_width=True)
    
    #--- head to head analytics
    
elif page == "Head to Head":

    st.title("⚔️ Head to Head Comparison")

    players = sorted(df["batter"].dropna().unique())

    p1 = st.selectbox("Player 1", players)
    p2 = st.selectbox("Player 2", players)

    batting = (
        df.groupby("batter")
        .agg(
            Runs=("runs_batter","sum"),
            Balls=("ball","count")
        )
        .reset_index()
    )

    batting["Strike Rate"] = (
        batting["Runs"] /
        batting["Balls"] * 100
    ).round(2)

    bowling = (
        df.groupby("bowler")
        .agg(
            Wickets=("player_out", lambda x: x.notna().sum()),
            Runs=("runs_total","sum"),
            Balls=("ball","count")
        )
        .reset_index()
    )

    bowling["Overs"] = bowling["Balls"]/6
    bowling["Economy"] = (
        bowling["Runs"] /
        bowling["Overs"].replace(0,1)
    ).round(2)

    st.subheader("Batting Comparison")

    b1 = batting[batting["batter"]==p1]
    b2 = batting[batting["batter"]==p2]

    compare_bat = pd.DataFrame({
        "Player":[p1,p2],
        "Runs":[b1["Runs"].iloc[0], b2["Runs"].iloc[0]],
        "Strike Rate":[
            b1["Strike Rate"].iloc[0],
            b2["Strike Rate"].iloc[0]
        ]
    })

    st.dataframe(compare_bat)

    fig = px.bar(
        compare_bat,
        x="Player",
        y="Runs",
        color="Player"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Bowling Comparison")

    bowl_compare = bowling[
        bowling["bowler"].isin([p1,p2])
    ]

    if len(bowl_compare)>0:
        st.dataframe(
            bowl_compare[
                ["bowler","Wickets","Economy"]
            ]
        )

        fig2 = px.bar(
            bowl_compare,
            x="bowler",
            y="Wickets",
            color="bowler"
        )

        st.plotly_chart(fig2, use_container_width=True)
    
    #----- team analysis-------
elif page == "Team Analysis":

    st.title("🏆 Team Analysis")

    team1 = matches["team1"].value_counts()
    team2 = matches["team2"].value_counts()

    team_matches = team1.add(team2, fill_value=0)

    team_df = pd.DataFrame({
        "Team": team_matches.index,
        "Matches": team_matches.values
    })

    st.dataframe(
        team_df.sort_values(
            "Matches",
            ascending=False
        ),
        use_container_width=True
    )

    fig = px.bar(
        team_df.sort_values(
            "Matches",
            ascending=False
        ),
        x="Team",
        y="Matches",
        title="Matches Played by Team"
    )

    st.plotly_chart(fig, use_container_width=True)
    
    tdf = pd.DataFrame({
    "Team": matches["team1"].value_counts().index,
    "Matches": matches["team1"].value_counts().values
})
    csv = tdf.to_csv(index=False).encode()

    st.download_button(
    "Download Team Stats",
    csv,
    "team_stats.csv",
    "text/csv"
)
    #----- venue analysis------
    
elif page == "Venue Analysis":

    st.title("🏟️ Venue Analysis")

    # -------------------------
    # Winner Column Detection
    # -------------------------

    winner_col = None

    if "winner" in matches.columns:
        winner_col = "winner"

    elif "outcome_winner" in matches.columns:
        winner_col = "outcome_winner"

    # -------------------------
    # Venue Search
    # -------------------------

    venues = sorted(
        matches["venue"]
        .dropna()
        .unique()
    )

    venue_search = st.selectbox(
        "🔍 Search Venue",
        venues
    )

    venue_df = matches[
        matches["venue"] == venue_search
    ]

    st.subheader(f"🏟️ {venue_search}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Matches",
        venue_df["match_id"].nunique()
    )

    col2.metric(
        "Teams",
        pd.concat([
            venue_df["team1"],
            venue_df["team2"]
        ]).nunique()
    )

    season_col = None

    if "season" in matches.columns:
        season_col = "season"

    elif "date_start" in matches.columns:
        season_col = "date_start"

    if season_col:
        col3.metric(
            "Seasons",
            venue_df[season_col].nunique()
        )

    else:
        col3.metric("Seasons", "-")

    if "city" in venue_df.columns:
        col4.metric(
            "City",
            venue_df["city"].iloc[0]
            if len(venue_df) > 0 else "-"
        )

    # -------------------------
    # Most Matches Venue
    # -------------------------

    st.markdown("---")
    st.subheader("🏏 Most Matches By Venue")

    venue_matches = (
        matches["venue"]
        .value_counts()
        .reset_index()
    )

    venue_matches.columns = [
        "Venue",
        "Matches"
    ]

    fig1 = px.bar(
        venue_matches.head(15),
        x="Venue",
        y="Matches",
        color="Matches",
        title="Top 15 Venues By Matches"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    # -------------------------
    # Highest Scoring Venue
    # -------------------------

    st.markdown("---")
    st.subheader("🔥 Highest Scoring Venues")

    venue_runs = (
        df.groupby("match_id")
        ["runs_total"]
        .sum()
        .reset_index()
    )

    venue_runs = venue_runs.merge(
        matches[
            ["match_id", "venue"]
        ],
        on="match_id",
        how="left"
    )

    venue_stats = (
        venue_runs
        .groupby("venue")
        ["runs_total"]
        .mean()
        .reset_index()
    )

    venue_stats.columns = [
        "Venue",
        "Average Match Runs"
    ]

    fig2 = px.bar(
        venue_stats
        .sort_values(
            "Average Match Runs",
            ascending=False
        )
        .head(15),
        x="Venue",
        y="Average Match Runs",
        color="Average Match Runs",
        title="Highest Scoring Venues"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # -------------------------
    # Most Successful Team
    # -------------------------

    st.markdown("---")
    st.subheader("🏆 Most Successful Teams At Venues")

    if winner_col:

        venue_team = (
            matches.groupby(
                ["venue", winner_col]
            )
            .size()
            .reset_index(name="Wins")
        )

        st.dataframe(
            venue_team
            .sort_values(
                "Wins",
                ascending=False
            )
            .head(25),
            use_container_width=True
        )

    # -------------------------
    # Team Win Percentage
    # -------------------------

    st.markdown("---")
    st.subheader("📈 Venue-wise Team Win %")

    all_teams = sorted(
        pd.concat([
            matches["team1"],
            matches["team2"]
        ])
        .dropna()
        .unique()
    )

    team_name = st.selectbox(
        "Select Team",
        all_teams
    )

    if winner_col:

        played = matches[
            (matches["team1"] == team_name)
            |
            (matches["team2"] == team_name)
        ]

        wins = matches[
            matches[winner_col]
            == team_name
        ]

        venue_played = (
            played.groupby("venue")
            .size()
            .reset_index(name="Played")
        )

        venue_wins = (
            wins.groupby("venue")
            .size()
            .reset_index(name="Wins")
        )

        venue_pct = venue_played.merge(
            venue_wins,
            on="venue",
            how="left"
        )

        venue_pct["Wins"] = (
            venue_pct["Wins"]
            .fillna(0)
        )

        venue_pct["Win %"] = (
            venue_pct["Wins"]
            /
            venue_pct["Played"]
            * 100
        ).round(2)

        st.dataframe(
            venue_pct.sort_values(
                "Win %",
                ascending=False
            ),
            use_container_width=True
        )

    # -------------------------
    # Venue Comparison
    # -------------------------

    st.markdown("---")
    st.subheader("⚔️ Venue Comparison")

    colA, colB = st.columns(2)

    with colA:
        v1 = st.selectbox(
            "Venue 1",
            venues,
            key="v1"
        )

    with colB:
        v2 = st.selectbox(
            "Venue 2",
            venues,
            key="v2"
        )

    compare = venue_stats[
        venue_stats["Venue"]
        .isin([v1, v2])
    ]

    fig3 = px.bar(
        compare,
        x="Venue",
        y="Average Match Runs",
        color="Venue",
        title="Venue Comparison"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    # -------------------------
    # Interactive Venue Map
    # -------------------------

    st.markdown("---")
    st.subheader("🗺️ Cricket Venues Map")

    venue_map = pd.DataFrame({
        "Venue":[
            "Wankhede Stadium",
            "Eden Gardens",
            "M Chinnaswamy Stadium",
            "MA Chidambaram Stadium",
            "Arun Jaitley Stadium",
            "Rajiv Gandhi Stadium",
            "Narendra Modi Stadium"
        ],
        "City":[
            "Mumbai",
            "Kolkata",
            "Bangalore",
            "Chennai",
            "Delhi",
            "Hyderabad",
            "Ahmedabad"
        ],
        "lat":[
            19.0176,
            22.5646,
            12.9788,
            13.0627,
            28.6379,
            17.4065,
            23.0910
        ],
        "lon":[
            72.8562,
            88.3433,
            77.5996,
            80.2794,
            77.2433,
            78.5500,
            72.5970
        ]
    })

    fig_map = px.scatter_mapbox(
        venue_map,
        lat="lat",
        lon="lon",
        hover_name="Venue",
        hover_data=["City"],
        zoom=4,
        height=600
    )

    fig_map.update_layout(
        mapbox_style="open-street-map"
    )

    st.plotly_chart(
        fig_map,
        use_container_width=True
    )
    #----- season trends------
    
elif page == "Season Trends":

    st.title("📈 Season Trends")

    season_df = (
        matches.groupby("season")
        .size()
        .reset_index(name="Matches")
    )

    fig = px.line(
        season_df,
        x="season",
        y="Matches",
        markers=True,
        title="Matches Played Per Season"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        season_df,
        use_container_width=True
    )
    

    
#--player search---
elif page == "Player Search":

    player = st.selectbox(
    "🔍 Search Player",
    sorted(df["batter"].dropna().unique())
)

    batting = df[df["batter"] == player]

    runs = batting["runs_batter"].sum()
    balls = len(batting)

    sr = round(
    (runs / balls) * 100,
    2
)   if balls > 0 else 0

    wickets = 0
    economy = 0

    if "bowler" in df.columns:

      bowling = df[
        df["bowler"] == player
    ]

    if "player_out" in df.columns:

        wickets = bowling[
            bowling["player_out"]
            .notna()
        ].shape[0]

    overs = len(bowling) / 6

    if overs > 0:

        economy = round(
            bowling["runs_total"].sum()
            / overs,
            2
        )

    st.subheader(f"🏏 {player}")

    c1,c2,c3,c4,c5 = st.columns(5)

    c1.metric("Runs", int(runs))
    c2.metric("Balls", int(balls))
    c3.metric("Strike Rate", sr)
    c4.metric("Wickets", wickets)
    c5.metric("Economy", economy)

    st.markdown("---")
    summary = pd.DataFrame({
    "Statistic":[
        "Runs",
        "Balls",
        "Strike Rate",
        "Wickets",
        "Economy"
    ],
    "Value":[
        runs,
        balls,
        sr,
        wickets,
        economy
    ]
})

    st.dataframe(
    summary,
    use_container_width=True
)
    st.subheader("📈 Performance")

    player_runs = (
    batting.groupby("match_id")
    ["runs_batter"]
    .sum()
    .reset_index()
)

    fig = px.line(
    player_runs,
    x="match_id",
    y="runs_batter",
    markers=True,
    title=f"{player} Match-wise Runs"
)

    st.plotly_chart(
    fig,
    use_container_width=True
)
    
    #--Match explorer---
elif page == "Match Explorer":

    st.title("📅 Match Explorer")

    season_col = "season"

    if season_col in matches.columns:

        season = st.selectbox(
            "Season",
            sorted(matches[season_col].dropna().unique())
        )

        filtered = matches[
            matches[season_col]==season
        ]

        st.dataframe(
            filtered,
            use_container_width=True
        )

    else:
        st.warning("Season column not found")
    
#------ winner analysis------

