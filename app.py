import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px

# --- SAFE API CONFIGURATION ---
if "API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["API_KEY"])
else:
    st.error("❌ API Key not found in Streamlit Secrets!")
    st.stop()

# UPDATED FOR 2026: Using Gemini 2.0 Flash (replaces retired 1.5 models)
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    # Fallback to 2.5 if 2.0 is in high demand
    model = genai.GenerativeModel('gemini-2.5-flash')

# --- PAGE CONFIG ---
st.set_page_config(page_title="MFD Goal Planner", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #1a73e8; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LANGUAGE & LABELS ---
lang = st.sidebar.selectbox("Choose Language / भाषा निवडा", ["English", "Marathi"])

texts = {
    "English": {
        "title": "🎯 Financial Goal Planner",
        "intro": "Plan your future with AI-powered insights.",
        "goal_label": "Enter your Goal (e.g. Child Education, Retirement)",
        "amt_label": "Target Amount (₹)",
        "year_label": "Time Horizon (Years)",
        "btn": "Calculate My Plan",
        "disclaimer": "Mutual Fund investments are subject to market risks."
    },
    "Marathi": {
        "title": "🎯 आर्थिक ध्येय नियोजक",
        "intro": "तुमच्या स्वप्नांचे AI सह नियोजन करा.",
        "goal_label": "तुमचे ध्येय लिहा (उदा. मुलांचे शिक्षण, निवृत्ती)",
        "amt_label": "लक्ष्य रक्कम (₹)",
        "year_label": "किती वर्षात पूर्ण करायचे आहे?",
        "btn": "नियोजन तयार करा",
        "disclaimer": "म्युच्युअल फंड गुंतवणूक बाजार जोखमीच्या अधीन असते."
    }
}

T = texts[lang]
st.title(T["title"])
st.write(T["intro"])

# --- INPUTS ---
goal_name = st.text_input(T["goal_label"], value="Child Education")
col1, col2 = st.columns(2)
with col1:
    target_amt = st.number_input(T["amt_label"], min_value=10000, value=1000000, step=50000)
with col2:
    years = st.number_input(T["year_label"], min_value=1, max_value=40, value=10)

if st.button(T["btn"]):
    with st.spinner("Generating Plan..." if lang=="English" else "नियोजन तयार होत आहे..."):
        prompt = f"Role: Expert Financial Advisor. Language: {lang}. Goal: {goal_name}. Target: ₹{target_amt} in {years} years. Calculate monthly SIP at 12% return and explain simply."
        
        try:
            response = model.generate_content(prompt)
            st.success("✅ Plan Generated Successfully!")
            st.markdown(response.text)
            
            # --- GRAPH ---
            r = 0.12 / 12
            n = years * 12
            sip = target_amt / ((( (1+r)**n ) - 1) / r * (1+r))
            
            data = []
            for y in range(years + 1):
                val = (sip * 12) * (( (1.12)**(y+1) - 1) / 0.12)
                data.append({"Year": 2026 + y, "Wealth (₹)": round(val)})
            
            df = pd.DataFrame(data)
            fig = px.bar(df, x="Year", y="Wealth (₹)", title="Wealth Projection")
            st.plotly_chart(fig, use_container_width=True)
            st.caption(T["disclaimer"])
            
        except Exception as e:
            st.error(f"Technical Error: {str(e)}")
            st.info("Check if your API Key has 'Gemini 2.0' enabled in AI Studio.")
