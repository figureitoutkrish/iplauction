import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="IPL Auction", layout="wide")

# -----------------------------
# DARK UI
# -----------------------------

st.markdown("""
<style>

body{
background-color:#0e1117;
}

.card{
background:#1e2228;
padding:20px;
border-radius:12px;
margin-bottom:20px;
}

.bid{
color:#ff4b4b;
font-size:22px;
font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATABASE
# -----------------------------

conn = sqlite3.connect("users.db",check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
username TEXT,
password TEXT,
team TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS bids(
player TEXT,
username TEXT,
team TEXT,
amount INTEGER
)
""")

conn.commit()

# -----------------------------
# LOAD PLAYERS
# -----------------------------

players = pd.read_csv("ipl_players.csv")

# -----------------------------
# GET CURRENT BIDS FROM DB
# -----------------------------

def get_current_bid(player):

    result = c.execute(
    "SELECT MAX(amount) FROM bids WHERE player=?",
    (player,)
    ).fetchone()[0]

    if result:
        return result
    else:
        return 1000000

# -----------------------------
# SESSION STATE
# -----------------------------

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Login"

# -----------------------------
# NAVBAR
# -----------------------------

if st.session_state.user:

    col1,col2,col3,col4 = st.columns([4,1,1,1])

    col1.markdown(f"### IPL Auction — {st.session_state.user[0]} ({st.session_state.user[2]})")

    if col2.button("Marketplace"):
        st.session_state.page = "Marketplace"

    if col3.button("History"):
        st.session_state.page = "History"

    if col4.button("Logout"):
        st.session_state.user = None
        st.session_state.page = "Login"
        st.rerun()

else:

    col1,col2 = st.columns([6,1])

    col1.markdown("### IPL Auction")

    if col2.button("Register"):
        st.session_state.page = "Register"

# -----------------------------
# LOGIN
# -----------------------------

if st.session_state.page == "Login":

    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("Login"):

        result = c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password)
        ).fetchone()

        if result:

            st.session_state.user = result
            st.session_state.page = "Marketplace"
            st.rerun()

        else:

            st.error("Invalid credentials")

# -----------------------------
# REGISTER
# -----------------------------

elif st.session_state.page == "Register":

    st.title("Create Account")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    team = st.selectbox(
    "Select Team",
    ["Mumbai Indians","CSK","RCB","KKR","RR","SRH","GT","PBKS"]
    )

    if st.button("Create Account"):

        c.execute(
        "INSERT INTO users VALUES(?,?,?)",
        (username,password,team)
        )

        conn.commit()

        st.success("Account Created!")

        st.session_state.page = "Login"
        st.rerun()

# -----------------------------
# MARKETPLACE
# -----------------------------

elif st.session_state.page == "Marketplace":

    if not st.session_state.user:
        st.session_state.page = "Login"
        st.rerun()

    st.title("Player Marketplace")

    col1,col2,col3 = st.columns(3)

    country = col1.selectbox(
    "Country",
    ["All"] + list(players["country"].unique())
    )

    role = col2.selectbox(
    "Role",
    ["All"] + list(players["role"].unique())
    )

    team = col3.selectbox(
    "Team",
    ["All"] + list(players["previous_team"].unique())
    )

    filtered = players.copy()

    if country != "All":
        filtered = filtered[filtered["country"]==country]

    if role != "All":
        filtered = filtered[filtered["role"]==role]

    if team != "All":
        filtered = filtered[filtered["previous_team"]==team]

    cols = st.columns(4)

    for idx,row in filtered.iterrows():

        current_bid = get_current_bid(row["name"])

        with cols[idx % 4]:

            st.markdown(f"""
            <div class="card">
            <h4>{row['name']}</h4>
            {row['role']} • {row['country']} <br>
            Team: {row['previous_team']}
            <p class="bid">₹{current_bid}</p>
            </div>
            """, unsafe_allow_html=True)

            bid = st.number_input(
            f"Bid for {row['name']}",
            min_value=0,
            key=f"bid_input_{idx}"
            )

            if st.button("Place Bid",key=f"bid_button_{idx}"):

                if bid > current_bid:

                    c.execute(
                    "INSERT INTO bids VALUES(?,?,?,?)",
                    (
                    row["name"],
                    st.session_state.user[0],
                    st.session_state.user[2],
                    bid
                    )
                    )

                    conn.commit()

                    st.success("Bid placed!")

                    st.rerun()

                else:

                    st.error("Bid must be higher")

# -----------------------------
# HISTORY
# -----------------------------

elif st.session_state.page == "History":

    st.title("Your Bid History")

    bids = c.execute(
    "SELECT * FROM bids WHERE username=?",
    (st.session_state.user[0],)
    ).fetchall()

    for b in bids:

        st.markdown(f"""
        <div class="card">
        Player: {b[0]} <br>
        Team: {b[2]}
        <p class="bid">₹{b[3]}</p>
        </div>
        """, unsafe_allow_html=True)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8501))
    st.run(port=port)