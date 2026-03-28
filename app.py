import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px

# --- SETUP ---
# Replace with your actual key or use Streamlit Secrets (recommended)
API_KEY = "YOUR_GEMINI_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

st.set_page_config(page_title="MFD Goal Planner", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #004a99; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- LANGUAGE SELECTION ---
lang = st.sidebar.radio("Select Language / भाषा निवडा", ("English", "Marathi"))

labels = {
    "English": {"title": "🎯 Financial Goal Planner", "goal": "What is your goal?", "amount": "Target Amount (₹)", "years": "In how many years?", "btn": "Calculate Plan"},
    "Marathi": {"title": "🎯 आर्थिक ध्येय नियोजक", "goal": "तुमचे ध्येय काय आहे?", "amount": "लक्ष्य रक्कम (₹)", "years": "किती वर्षात?", "btn": "नियोजन तयार करा"}
}

L = labels[lang]

st.title(L["title"])
st.write("Welcome! Let's plan your future together." if lang=="English" else "नमस्कार! चला तुमच्या भविष्याचे नियोजन करूया.")

# --- INPUT SECTION ---
with st.expander("Add Your Goals" if lang=="English" else "तुमची ध्येये जोडा", expanded=True):
    goal_name = st.text_input(L["goal"], placeholder="Child Education / Retirement")
    target_amt = st.number_input(L["amount"], min_value=1000, step=50000)
    years = st.slider(L["years"], 1, 30, 10)

if st.button(L["btn"]):
    # Use Gemini to explain the strategy
    prompt = f"""
    Context: You are a helpful Mutual Fund Distributor. 
    User Goal: {goal_name}, Target: {target_amt}, Time: {years} years.
    Language: {lang}.
    Task: Explain how much they should invest monthly (SIP) assuming a 12% annual return. 
    Suggest categories like Flexi Cap or Mid Cap. Keep it simple and encouraging. 
    Output the explanation in {lang}.
    """
    
    response = model.generate_content(prompt)
    
    st.subheader("Your Personalized Plan" if lang=="English" else "तुमचे वैयक्तिक नियोजन")
    st.info(response.text)

    # --- GRAPH LOGIC ---
    # Simple compound interest visualization for the webpage
    months = years * 12
    monthly_rate = 0.12 / 12
    # Approx SIP needed formula: Target / [((1+r)^n - 1)/r * (1+r)]
    sip_needed = target_amt / ((( (1+monthly_rate)**months ) - 1) / monthly_rate * (1+monthly_rate))
    
    data = []
    current_wealth = 0
    for y in range(years + 1):
        # Rough estimation for graph
        current_wealth = (sip_needed * 12) * (( (1.12)**(y+1) - 1) / 0.12)
        data.append({"Year": 2024+y, "Wealth (₹)": round(current_wealth)})
    
    df = pd.DataFrame(data)
    fig = px.area(df, x="Year", y="Wealth (₹)", title="Wealth Growth Over Time")
    st.plotly_chart(fig, use_container_width=True)
    
    st.success("Disclaimer: Mutual Fund investments are subject to market risks." if lang=="English" else "सूचना: म्युच्युअल फंड गुंतवणूक ही बाजार जोखमीच्या अधीन असते.")