import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px

# --- SAFE API CONFIGURATION ---
# This looks for the key in your Streamlit Cloud 'Secrets' dashboard
if "API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["API_KEY"])
else:
    st.error("❌ API Key not found! Please add 'API_KEY' to your Streamlit Secrets.")
    st.stop()

# Using Gemini 1.5 Pro for high-quality financial logic
model = genai.GenerativeModel('gemini-1.5-pro')

# --- PAGE CONFIG ---
st.set_page_config(page_title="MFD Goal Planner", layout="centered")

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LANGUAGE & LABELS ---
lang = st.sidebar.selectbox("Choose Language / भाषा निवडा", ["English", "Marathi"])

texts = {
    "English": {
        "title": "🎯 My Financial Goal Planner",
        "intro": "Plan your dreams with expert AI guidance.",
        "goal_label": "Enter your Goal (e.g., Daughter's Marriage, New Home)",
        "amt_label": "Target Amount (₹)",
        "year_label": "Years to achieve this goal",
        "btn": "Generate My Investment Plan",
        "disclaimer": "Note: Estimates are based on a 12% p.a. return. Mutual Funds are subject to market risks."
    },
    "Marathi": {
        "title": "🎯 माझे आर्थिक ध्येय नियोजन",
        "intro": "तज्ञ AI मार्गदर्शनासह तुमच्या स्वप्नांचे नियोजन करा.",
        "goal_label": "तुमचे ध्येय लिहा (उदा. मुलीचे लग्न, नवीन घर)",
        "amt_label": "लक्ष्य रक्कम (₹)",
        "year_label": "हे ध्येय किती वर्षात पूर्ण करायचे आहे?",
        "btn": "माझे गुंतवणूक नियोजन तयार करा",
        "disclaimer": "सूचना: अंदाज वार्षिक १२% परताव्यावर आधारित आहेत. म्युच्युअल फंड गुंतवणूक बाजार जोखमीच्या अधीन असते."
    }
}

T = texts[lang]

# --- UI LAYOUT ---
st.title(T["title"])
st.write(T["intro"])
st.divider()

# Input section
with st.container():
    goal_name = st.text_input(T["goal_label"], placeholder="e.g. Retirement")
    col1, col2 = st.columns(2)
    with col1:
        target_amt = st.number_input(T["amt_label"], min_value=10000, value=1000000, step=50000)
    with col2:
        years = st.number_input(T["year_label"], min_value=1, max_value=40, value=10)

if st.button(T["btn"]):
    with st.spinner("Calculating your future..." if lang=="English" else "तुमचे नियोजन तयार होत आहे..."):
        # AI Prompt Logic
        prompt = f"""
        You are a professional Mutual Fund Distributor in India.
        Client Goal: {goal_name}
        Target Amount: ₹{target_amt}
        Time Horizon: {years} years.
        
        Task:
        1. Calculate the required Monthly SIP assuming a 12% annual return.
        2. Explain the result in very simple terms for a common person.
        3. Suggest categories like 'Large Cap' or 'Flexi Cap' for long term.
        4. Do NOT mention specific company names (like HDFC or SBI).
        5. Provide the entire response in {lang}.
        """
        
        try:
            response = model.generate_content(prompt)
            st.subheader("Your Personalized Strategy" if lang=="English" else "तुमची वैयक्तिक रणनीती")
            st.success(response.text)
            
            # --- GRAPHING ---
            i = 0.12 / 12
            n = years * 12
            sip_val = target_amt / ((( (1+i)**n ) - 1) / i * (1+i))
            
            chart_data = []
            for y in range(years + 1):
                growth = (sip_val * 12) * (( (1.12)**(y+1) - 1) / 0.12)
                chart_data.append({"Year": 2024 + y, "Estimated Wealth (₹)": round(growth)})
            
            df = pd.DataFrame(chart_data)
            fig = px.area(df, x="Year", y="Estimated Wealth (₹)", 
                          title="Wealth Growth Projection" if lang=="English" else "संपत्ती वाढीचा अंदाज")
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            # THIS PART WILL NOW SHOW THE ACTUAL ERROR
            st.error(f"Error Details: {str(e)}")
            st.info("Common fix: Try changing 'gemini-1.5-pro' to 'gemini-1.5-flash' in the code.")
