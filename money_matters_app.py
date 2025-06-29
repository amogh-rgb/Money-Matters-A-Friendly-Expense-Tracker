import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import plotly.express as px

# ------------------ File Config ------------------
USERFILE = "users.json"

THEMES = {
    "Aurora Borealis": """
    .stApp {
      background: linear-gradient(-45deg, #43cea2, #185a9d, #43cea2, #185a9d);
      background-size: 400% 400%;
      animation: aurora 20s ease infinite;
    }
    @keyframes aurora {
      0% {background-position: 0% 50%;}
      50% {background-position: 100% 50%;}
      100% {background-position: 0% 50%;}
    }
    """,
    "Retro Neon Wave": """
    .stApp {
      background: radial-gradient(circle, #ff00cc, #333399, #ff00cc);
      background-size: 200% 200%;
      animation: neonwave 12s ease-in-out infinite alternate;
    }
    @keyframes neonwave {
      0% {background-position: 0% 0%;}
      100% {background-position: 100% 100%;}
    }
    """,
    "Sunset Beach": """
    .stApp {
      background: linear-gradient(270deg, #fcb69f, #ffecd2, #fcb69f);
      background-size: 400% 400%;
      animation: sunset 16s ease infinite;
    }
    @keyframes sunset {
      0% {background-position: 0% 50%;}
      50% {background-position: 100% 50%;}
      100% {background-position: 0% 50%;}
    }
    """
}

def apply_theme():
    theme_css = THEMES.get(st.session_state.get("theme", "Aurora Borealis"), THEMES["Aurora Borealis"])
    st.markdown(f"""
    <style>
    {theme_css}
    .login-box {{
        background: rgba(255,255,255,0.92);
        border-radius: 16px;
        padding: 2rem;
        max-width: 420px;
        margin: auto;
        box-shadow: 0 12px 48px rgba(0,0,0,0.3);
        backdrop-filter: blur(8px);
        transform: translateY(30px);
        opacity: 0;
        animation: slideIn 1s ease forwards;
    }}
    @keyframes slideIn {{
        to {{ transform: translateY(0); opacity: 1; }}
    }}
    button:hover {{
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }}
    </style>
    """, unsafe_allow_html=True)

# ------------------ File Helpers ------------------
def init_files():
    if not os.path.exists(USERFILE):
        with open(USERFILE, "w") as f:
            json.dump({}, f)

def load_users():
    with open(USERFILE) as f:
        return json.load(f)

def save_users(users):
    with open(USERFILE, "w") as f:
        json.dump(users, f, indent=2)

def user_data_file(username):
    return f"expenses_{username}.json"

def load_data(username):
    file = user_data_file(username)
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)
    with open(file) as f:
        return json.load(f)

def save_data(username, data):
    file = user_data_file(username)
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def emoji(cat):
    return {
        "Food": "🍔", "Travel": "✈️", "Shopping": "🛍️",
        "Rent": "🏠", "Health": "💊", "Utilities": "💡",
        "Entertainment": "🎬"
    }.get(cat, "💰")

def themed_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning, Money Maestro! ☀️"
    elif hour < 18:
        return "Good afternoon, Savvy Spender! 🌈"
    else:
        return "Good evening, Financial Wizard! 🌙"

# ------------------ Login/Register Page ------------------
def login_page():
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>💸 MONEY MATTERS</h1>", unsafe_allow_html=True)

    st.write("🎨 Pick Your Theme")
    col1, col2, col3 = st.columns(3)
    if col1.button("🌌 Aurora"):
        st.session_state.theme = "Aurora Borealis"
        st.rerun()
    if col2.button("🌴 Retro Wave"):
        st.session_state.theme = "Retro Neon Wave"
        st.rerun()
    if col3.button("🌅 Sunset Beach"):
        st.session_state.theme = "Sunset Beach"
        st.rerun()

    if "tab_index" not in st.session_state:
        st.session_state.tab_index = 0

    tab = st.radio("Navigation", ["🔑 Login", "🆕 Register", "🔐 Forgot Password"], index=st.session_state.tab_index)

    if tab == "🔑 Login":
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            users = load_users()
            if username in users and users[username]["password"] == password:
                st.session_state.user = username
                st.success(themed_greeting())
                st.rerun()
            else:
                st.error("🚫 Invalid credentials.")

    elif tab == "🆕 Register":
        new_user = st.text_input("New Username", key="reg_user")
        new_pass = st.text_input("New Password", type="password", key="reg_pass")
        hint = st.text_input("Recovery Hint", key="reg_hint")

        if st.button("Create Account"):
            users = load_users()
            if new_user in users:
                st.warning("⚠️ Username already exists! Try another.")
            elif not new_user or not new_pass:
                st.warning("❗ Please enter both a username and password.")
            else:
                users[new_user] = {"password": new_pass, "hint": hint}
                save_users(users)
                save_data(new_user, [])

                st.session_state.account_created = {
                    "username": new_user,
                    "hint": hint
                }

                st.session_state.tab_index = 0  # Switch to Login tab next
                st.rerun()

        if st.session_state.get("account_created"):
            created = st.session_state.account_created
            st.success(f"✅ **Account Created Successfully!** 🎉\n\n"
                       f"**Username:** `{created['username']}`\n"
                       f"**Recovery Hint:** `{created['hint']}`\n\n"
                       "Now you can log in using your credentials. 🚀")
            st.toast("✅ Registered Successfully!", icon="🎉")
            st.balloons()
            st.session_state.account_created = None

    elif tab == "🔐 Forgot Password":
        recover_user = st.text_input("Username to recover", key="recover_user")
        if st.button("Show Hint"):
            users = load_users()
            hint = users.get(recover_user, {}).get("hint")
            if hint:
                st.info(f"💡 Hint: {hint}")
            else:
                st.warning("No recovery hint found.")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ Main Dashboard ------------------
def main_app():
    username = st.session_state.user
    st.title(f"💸 Welcome, {username}!")
    st.caption(themed_greeting())

    menu = st.sidebar.radio("📂 Menu", ["➕ Add Expense", "📋 View All", "📊 Summary"])
    data = load_data(username)

    if menu == "➕ Add Expense":
        st.header("➕ Add a New Expense")
        category_emojis = {
            "🍔 Food": "Food", "✈️ Travel": "Travel", "🛍️ Shopping": "Shopping",
            "🏠 Rent": "Rent", "💊 Health": "Health", "💡 Utilities": "Utilities",
            "🎬 Entertainment": "Entertainment"
        }
        cat_display = st.selectbox("Category", list(category_emojis.keys()))
        cat_clean = category_emojis[cat_display]
        amt = st.number_input("Amount", min_value=0.0, format="%.2f")
        date = st.date_input("Date", value=datetime.today())
        if st.button("💾 Save Expense"):
            data.append({"amount": amt, "category": cat_clean, "date": date.strftime("%Y-%m-%d")})
            save_data(username, data)
            category_emoji = emoji(cat_clean)
            st.toast(f"{category_emoji} ₹{amt:,.2f} added to {cat_clean}!", icon="✅")
            st.success(f"{category_emoji} Added to {cat_clean} successfully!")

            emoji_rain = "".join(
                f"<div class='falling-emoji' style='left:{10*i}%'> {category_emoji} </div>"
                for i in range(1, 10)
            )
            rain_css = """
            <style>
            @keyframes drop {
              0% { transform: translateY(-100px); opacity: 1; }
              100% { transform: translateY(500px); opacity: 0; }
            }
            .falling-emoji {
              position: fixed;
              top: 0;
              font-size: 50px;
              animation: drop 3s ease-out forwards;
              z-index: 9999;
            }
            </style>
            """
            st.markdown(rain_css + emoji_rain, unsafe_allow_html=True)

    elif menu == "📋 View All":
        st.header("📋 All Expenses")
        if data:
            df = pd.DataFrame(data)
            df["Entry"] = df["category"].map(emoji) + " ₹" + df["amount"].astype(str) + " on " + df["date"]
            st.dataframe(df[["Entry"]])
        else:
            st.info("No expenses yet.")

    elif menu == "📊 Summary":
        st.header("📊 Summary & Insights")
        if data:
            df = pd.DataFrame(data)
            group = df.groupby("category")["amount"].sum().reset_index()
            group["cat_label"] = group["category"].map(emoji) + " " + group["category"]
            total = df["amount"].sum()

            col1, col2 = st.columns(2)

            template = "plotly_dark"

            with col1:
                fig1 = px.pie(group, names="cat_label", values="amount", hole=0.5,
                              title="Spending by Category",
                              template=template,
                              color_discrete_sequence=px.colors.sequential.RdPu)
                fig1.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    legend_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                fig2 = px.bar(group, x="cat_label", y="amount", text_auto=".2s",
                              title="Expense Totals by Category",
                              template=template,
                              color="amount",
                              color_continuous_scale=px.colors.sequential.Magma)
                fig2.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    legend_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown(f"<h4 style='color:#fff;'>💰 Total Spent: ₹{total:,.2f}</h4>", unsafe_allow_html=True)
        else:
            st.warning("No data to summarize.")

# ------------------ Launch ------------------
def launch():
    init_files()
    apply_theme()
    if "user" not in st.session_state:
        login_page()
    else:
        main_app()

launch()
