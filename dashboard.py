import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(
    page_title="NBA Draft Predictor",
    page_icon="🏀",
    layout="wide",
)

@st.cache_resource
def get_connection():
    return duckdb.connect(database='curr_season.duckdb', read_only=True)

con = get_connection()

st.title("NBA Draft Predictor")
st.caption("2026 Draft Class")

search = st.text_input(
    label="Search for a player",
    placeholder="e.g. Jeremy Fears Jr.",
)

if search:
    query = """
        SELECT *
        FROM curr
        WHERE LOWER(Player) LIKE LOWER(?)
        ORDER BY Draft_Prob DESC
    """
    results = con.execute(query, [f"%{search}%"]).fetchdf()

    if results.empty:
        st.warning("No players found. Try a different name or partial name.")
    else:
        st.success(f"Found {len(results)} player(s)")
        selected_name = st.selectbox(
            "Select a player",
            options=results["Player"].tolist(),
        )
        player = results[results["Player"] == selected_name].iloc[0]

        # Header row
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader(player["Player"])
            st.write(f"**Team:** {player['Team']}  |  **Position:** {player['Pos']}  |  **Class:** {player['Class']}")
        with col2:
            draft_prob = float(player["Draft_Prob"])
            st.metric(
                label="Draft Probability",
                value=f"{draft_prob:.1%}",
            )

        st.divider()

        # Stats section
        st.subheader("Season Stats")
        stat_cols = st.columns(5)
        stats = {
            "PPG": "PPG",
            "APG": "APG",
            "RPG": "RPG",
            "SPG": "SPG",
            "BPG": "BPG",
        }

        for i, (label, col_name) in enumerate(stats.items()):
            with stat_cols[i]:
                if col_name in player:
                    st.metric(label=label, value=f"{float(player[col_name]):.1f}")

        st.divider()

        # Shooting section
        st.subheader("Shooting")
        shoot_cols = st.columns(3)
        shooting_stats = {
            "FG%": "FG%",
            "3P%": "3P%",
            "FT%": "FT%",
        }
        for i, (label, col_name) in enumerate(shooting_stats.items()):
            with shoot_cols[i]:
                if col_name in player and pd.notna(player[col_name]):
                    st.metric(label=label, value=f"{float(player[col_name]):.1%}")
                else:
                    st.metric(label=label, value="N/A")

        st.divider()

        #Games Played Section
        st.subheader("Games played")
        game_cols = {
            "Games Played": "GP",
            "Games Started": "GS"
        }
        for i, (label, col_name) in enumerate(game_cols.items()):
            if col_name in player and pd.notna(player[col_name]):
                st.metric(label=label, value=f"{float(player[col_name])}")
            else:
                st.metric(label=label, value="N/A")

        st.divider()

        # Full data expander
        with st.expander("View all stats"):
            st.dataframe(player.iloc[1:-3].to_frame().T, hide_index = True, width = 'stretch')



st.divider()
st.header("All Player Stats")

all_query = """
SELECT  * EXCLUDE (Rk, Class_enc, POS_enc) FROM curr ORDER BY Draft_Prob DESC
"""
all_prospects = con.execute(all_query)

with st.expander("View all Player Stats"):
    st.dataframe(all_prospects, width = 'stretch')