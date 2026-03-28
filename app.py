import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px

# --- SAFE API CONFIGURATION ---
if "API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["API_KEY"])
else:
    st.error("❌ API Key not found in Secrets!")
    st.stop()

# CHANGED: Using 'gemini-1.5-flash' for better reliability and speed
model = genai.GenerativeModel('gemini-1.5-flash')

# --- PAGE CONFIG ---
st.set_page_config(page_title="MFD Goal Planner", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #1a73e8; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #1557b0; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- LANGUAGE & LABELS ---
lang = st.sidebar.selectbox("Choose Language / भाषा निवडा", ["English", "Marathi"])

texts = {
    "English": {
        "title": "🎯 Financial Goal Planner",
        "intro": "Plan your future investments with AI-powered insights.",
        "goal_label": "What is your goal? (e.g. Retirement, Child's Education)",
        "amt_label": "How much money do you need? (Target ₹)",
        "year_label": "In how many years?",
        "btn": "Calculate My Plan",
        "result_head": "Your Personalized Strategy",
        "disclaimer": "Disclaimer: Returns are illustrative (12% p.a.). Mutual Funds are subject to market risks."
    },
    "Marathi": {
        "title": "🎯 आर्थिक ध्येय नियोजक",
        "intro": "AI-आधारित माहितीसह तुमच्या भविष्यातील गुंतवणुकीचे नियोजन करा.",
        "goal_label": "तुमचे ध्येय काय आहे? (उदा. निवृत्ती, मुलांचे शिक्षण)",
        "amt_label": "तुम्हाला किती पैशांची गरज आहे? (लक्ष्य रक्कम ₹)",
        "year_label": "किती वर्षात?",
        "btn": "नियोजन तयार करा",
        "result_head": "तुमची वैयक्तिक रणनीती",
        "disclaimer": "सूचना: अंदाज १२% वार्षिक परताव्यावर आधारित आहेत. म्युच्युअल फंड गुंतवणूक बाजार जोखमीच्या अधीन असते."
    }
}

T = texts[lang]

st.title(T["title"])
st.info(T["intro"])

# --- INPUTS ---
goal_name = st.text_input(T["goal_label"], value="Retirement")
col1, col2 = st.columns(2)
with col1:
    target_amt = st.number_input(T["amt_label"], min_value=10000, value=1000000, step=50000)
with col2:
    years = st.number_input(T["year_label"], min_value=1, max_value=40, value=10)

if st.button(T["btn"]):
    with st.spinner("Generating your plan..." if lang=="English" else "नियोजन तयार होत आहे..."):
        # AI Logic
        prompt = f"""
        Role: Expert Mutual Fund Distributor.
        Goal: {goal_name}, Target: ₹{target_amt}, Time: {years} years.
        Language: {lang}.
        1. Calculate monthly SIP needed for 12% return.
        2. Explain why Equity Mutual Funds are good for this goal.
        3. Keep it very simple and friendly.
        """
        
        try:
            response = model.generate_content(prompt)
            st.subheader(T["result_head"])
            st.markdown(response.text)
            
            # --- MATH & GRAPH ---
            # Formula: P = FV / [((1+r)^n - 1)/r * (1+r)]
            r = 0.12 / 12
            n = years * 12
            sip_calc = target_amt / ((( (1+r)**n ) - 1) / r * (1+r))
            
            data = []
            for y in range(years + 1):
                # Monthly compound growth visualization
                val = (sip_calc * 12) * (( (1.12)**(y+1) - 1) / 0.12)
                data.append({"Year": 2024 + y, "Wealth (₹)": round(val)})
            
            df = pd.DataFrame(data)
            fig = px.bar(df, x="Year", y="Wealth (₹)", color="Wealth (₹)", 
                         title="Estimated Wealth Growth" if lang=="English" else "संपत्ती वाढीचा अंदाज")
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption(T["disclaimer"])
            
        except Exception as e:
            st.error(f"Something went wrong. Technical Error: {str(e)}")
