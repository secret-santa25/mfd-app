import streamlit as st
from google import genai
import pandas as pd
import plotly.express as px

# --- 1. SECURE CONNECTION ---
if "API_KEY" in st.secrets:
    # 2026 SDK Syntax
    client = genai.Client(api_key=st.secrets["API_KEY"])
else:
    st.error("❌ API Key missing in Secrets!")
    st.stop()

# --- 2. APP UI ---
st.set_page_config(page_title="MFD Goal Planner", layout="centered")

# Language Choice
lang = st.sidebar.selectbox("Select Language / भाषा निवडा", ["English", "Marathi"])

texts = {
    "English": {"title": "🎯 Client Goal Planner", "add": "Add Goal", "calc": "Generate Full Plan", "goal_name": "Goal Name", "target": "Target (₹)", "yrs": "Years"},
    "Marathi": {"title": "🎯 ग्राहक ध्येय नियोजक", "add": "ध्येय जोडा", "calc": "नियोजन तयार करा", "goal_name": "ध्येयाचे नाव", "target": "लक्ष्य रक्कम (₹)", "yrs": "वर्षे"}
}
L = texts[lang]

st.title(L["title"])

# Session state to store multiple goals
if "goals" not in st.session_state:
    st.session_state.goals = []

# Input Form
with st.form("goal_form"):
    g_name = st.text_input(L["goal_name"], placeholder="e.g. Retirement")
    g_amt = st.number_input(L["target"], min_value=10000, value=1000000)
    g_yrs = st.number_input(L["yrs"], min_value=1, value=10)
    if st.form_submit_button(L["add"]):
        st.session_state.goals.append({"name": g_name, "amt": g_amt, "yrs": g_yrs})

# Display Added Goals
if st.session_state.goals:
    for i, g in enumerate(st.session_state.goals):
        st.write(f"✅ {g['name']}: ₹{g['amt']:,} in {g['yrs']} years")
    
    if st.button(L["calc"]):
        all_goals_text = "\n".join([f"- {g['name']}: ₹{g['amt']} in {g['yrs']} years" for g in st.session_state.goals])
        
        prompt = f"""
        Role: Professional Mutual Fund Distributor. Language: {lang}.
        Client has these goals:
        {all_goals_text}
        
        1. Calculate monthly SIP for each goal (12% return).
        2. Explain where to invest (categories like Flexi Cap, Hybrid) and why.
        3. Give a very easy and motivating explanation.
        """
        
        try:
            # Using Gemini 2.5 Flash - Stable 2026 Model
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            st.markdown("### Your Personalized Plan")
            st.info(response.text)
            
            # --- SIMPLE SUMMARY GRAPH ---
            chart_df = pd.DataFrame(st.session_state.goals)
            fig = px.pie(chart_df, values='amt', names='name', title="Goal Distribution")
            st.plotly_chart(fig)
            
        except Exception as e:
            st.error(f"Error: {e}")
