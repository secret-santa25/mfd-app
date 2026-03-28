import streamlit as st
from google import genai
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONNECTION ---
if "API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["API_KEY"])
else:
    st.error("❌ API Key missing!")
    st.stop()

# --- APP SETUP ---
st.set_page_config(page_title="Rupesh - Wealth Planner", layout="centered")

# Custom Styles
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main-button { background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%); color: white; padding: 20px; border-radius: 15px; text-align: center; cursor: pointer; font-size: 24px; font-weight: bold; }
    .infobox { background-color: #f0f7ff; padding: 20px; border-radius: 10px; border-left: 5px solid #1a73e8; }
    </style>
    """, unsafe_allow_html=True)

# Session State Initialization
if "page" not in st.session_state: st.session_state.page = "start"
if "goals" not in st.session_state: st.session_state.goals = []

# --- PAGE 1: START SCREEN ---
if st.session_state.page == "start":
    st.image("https://cdn-icons-png.flaticon.com/512/2654/2654504.png", width=100)
    st.title("🚀 Rupesh - Wealth Planner")
    st.subheader("Your Journey to Financial Freedom Starts Here.")
    st.write("Plan your children's education, retirement, or a secure emergency fund with AI-powered insights.")
    
    if st.button("Start My Planning Now"):
        st.session_state.page = "questions"
        st.rerun()

# --- PAGE 2: QUESTIONNAIRE ---
elif st.session_state.page == "questions":
    st.title("📋 Build Your Plan")
    lang = st.radio("Choose Language / भाषा निवडा", ["English", "Marathi"], horizontal=True)
    
    with st.container(border=True):
        st.subheader("Add a New Goal")
        g_type = st.selectbox("Type of Goal", ["Long Term (Wealth Creation)", "Short Term (Emergency Fund)"])
        g_name = st.text_input("Goal Name (e.g. Dream Home, Medical Fund)")
        g_amt = st.number_input("Amount Required (₹)", min_value=5000, value=100000, step=10000)
        
        if g_type == "Long Term (Wealth Creation)":
            g_yrs = st.slider("Time Horizon (Years)", 1, 30, 10)
        else:
            g_yrs = 0 # Emergency funds are immediate
            
        if st.button("➕ Add This Goal"):
            st.session_state.goals.append({"type": g_type, "name": g_name, "amt": g_amt, "yrs": g_yrs})
            st.toast("Goal added!")

    # Show list of added goals
    if st.session_state.goals:
        st.write("---")
        st.subheader("Your Planned Goals:")
        for i, g in enumerate(st.session_state.goals):
            st.write(f"✅ **{g['name']}**: ₹{g['amt']:,} ({g['type']})")
        
        if st.button("✨ Generate Final Plan & Visuals"):
            st.session_state.page = "results"
            st.rerun()

# --- PAGE 3: RESULTS & AI OUTPUT ---
elif st.session_state.page == "results":
    st.title("📊 Rupesh - Your Personal Wealth Plan")
    
    # 1. SPECIAL SECTION: OVERNIGHT FUND EXPLANATION
    has_emergency = any(g['type'] == "Short Term (Emergency Fund)" for g in st.session_state.goals)
    
    if has_emergency:
        st.header("🛡️ Emergency Fund Strategy")
        st.info("For your short-term needs, we recommend **Overnight Funds**.")
        
        # Easy Explanation Table
        withdrawal_data = {
            "Scenario": ["Monday to Thursday", "Friday (Before 1:30 PM)", "Friday (After 1:30 PM)", "Saturday/Sunday"],
            "Money in Bank": ["Next Working Day", "Monday", "Tuesday", "Interest Still Earned?"],
            "Interest Accrual": ["Daily", "Daily", "Daily", "YES! (Full Weekend)"]
        }
        st.table(pd.DataFrame(withdrawal_data))
        
        st.write("""
        **Why Overnight Funds?**
        - **Safe:** Invests in overnight debt markets.
        - **Liquid:** Get money in 1 working day.
        - **Weekend Interest:** Unlike savings accounts, you earn interest on Saturdays and Sundays too!
        """)

    # 2. AI DETAILED ANALYSIS
    all_goals_summary = "\n".join([f"- {g['name']}: {g['amt']} over {g['yrs']} years ({g['type']})" for g in st.session_state.goals])
    
    with st.spinner("AI is calculating your best path..."):
        prompt = f"""
        Role: Expert MFD 'Rupesh - Wealth Planner'. 
        Client Goals: {all_goals_summary}. 
        Tasks:
        1. Calculate SIP for long-term goals (12% return).
        2. Explain the safety and withdrawal benefits of Overnight funds for short-term goals.
        3. Use simple, friendly language.
        4. Provide the explanation in Marathi and English.
        """
        
        try:
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            st.markdown(response.text)
            
            # 3. VISUALIZATION
            st.header("📈 Investment Visualization")
            chart_df = pd.DataFrame(st.session_state.goals)
            fig = px.pie(chart_df, values='amt', names='name', hole=0.4, title="Distribution of Financial Goals")
            st.plotly_chart(fig)
            
        except Exception as e:
            st.error(f"Something went wrong: {e}")

    if st.button("🔄 Start New Plan"):
        st.session_state.goals = []
        st.session_state.page = "start"
        st.rerun()
