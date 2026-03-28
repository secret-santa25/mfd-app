import streamlit as st
from google import genai
import pandas as pd
import plotly.express as px

# --- 1. CONNECTION ---
if "API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["API_KEY"])
else:
    st.error("❌ API Key missing in Secrets!")
    st.stop()

# --- 2. APP SETUP ---
st.set_page_config(page_title="Rupesh - Wealth Planner", layout="centered")

# Session State Initialization
if "page" not in st.session_state: st.session_state.page = "start"
if "goals" not in st.session_state: st.session_state.goals = []

# --- PAGE 1: START SCREEN ---
if st.session_state.page == "start":
    st.markdown("<h1 style='text-align: center;'>🚀 Rupesh - Wealth Planner</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Your trusted partner in financial freedom and smart investing.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Start My Planning Now", use_container_width=True):
            st.session_state.page = "questions"
            st.rerun()

# --- PAGE 2: QUESTIONNAIRE ---
elif st.session_state.page == "questions":
    st.title("📋 Build Your Plan")
    lang = st.radio("Choose Language / भाषा निवडा", ["English", "Marathi"], horizontal=True)
    
    with st.container(border=True):
        st.subheader("Add a New Goal")
        g_type = st.selectbox("Type of Goal", ["Long Term (Wealth Creation)", "Short Term (Emergency Fund)"])
        g_name = st.text_input("Goal Name (e.g. Retirement, Child Education)")
        g_amt = st.number_input("Amount Required (₹)", min_value=5000, value=100000, step=10000)
        
        if g_type == "Long Term (Wealth Creation)":
            g_yrs = st.slider("Time Horizon (Years)", 1, 30, 10)
        else:
            g_yrs = 0 # Emergency funds are usually immediate
            
        if st.button("➕ Add This Goal"):
            # Ensure we store 'type' to avoid the KeyError again
            st.session_state.goals.append({"type": g_type, "name": g_name, "amt": g_amt, "yrs": g_yrs})
            st.toast(f"Goal '{g_name}' added!")

    # Display Added Goals with safety check
    if st.session_state.goals:
        st.write("---")
        st.subheader("Your Planned Goals:")
        for i, g in enumerate(st.session_state.goals):
            # Using .get() prevents the app from crashing if a key is missing
            name = g.get('name', 'Goal')
            amt = g.get('amt', 0)
            gtype = g.get('type', 'General')
            st.write(f"✅ **{name}**: ₹{amt:,} ({gtype})")
        
        if st.button("✨ Generate Final Plan & Visuals"):
            st.session_state.page = "results"
            st.rerun()
            
    if st.button("🗑️ Reset All"):
        st.session_state.goals = []
        st.rerun()

# --- PAGE 3: RESULTS & AI OUTPUT ---
elif st.session_state.page == "results":
    st.title("📊 Rupesh - Your Personal Wealth Plan")
    
    # Logic for Overnight Funds (Emergency Fund)
    has_emergency = any(g.get('type') == "Short Term (Emergency Fund)" for g in st.session_state.goals)
    
    if has_emergency:
        st.header("🛡️ Emergency Fund Strategy")
        st.success("**Recommendation: Overnight Funds**")
        
        st.markdown("""
        **Why Overnight Funds are best for your Emergency money:**
        - **Safe:** Extremely low risk as they invest for just 1 day.
        - **Withdrawal Rules:** - Money requested before **1:30 PM (Mon-Thu)** arrives next day.
            - Money requested on **Friday** arrives on **Monday**.
            - **Bonus:** You earn interest for **Saturday and Sunday** even if you withdraw on Friday!
        """)
        
        # Withdrawal Timeline Table
        df_time = pd.DataFrame({
            "Withdrawal Day": ["Monday", "Friday (Morning)", "Friday (Evening)", "Saturday"],
            "Money in Bank": ["Tuesday", "Monday", "Tuesday", "Tuesday"],
            "Interest Earned": ["Yes", "Full Weekend", "Full Weekend", "Daily"]
        })
        st.table(df_time)

    # Combined AI Analysis
    all_goals_summary = "\n".join([f"- {g.get('name')}: {g.get('amt')} over {g.get('yrs')} years" for g in st.session_state.goals])
    
    with st.spinner("Rupesh AI is calculating..."):
        prompt = f"""
        Role: Expert Financial Planner named 'Rupesh'. 
        Client Goals: {all_goals_summary}. 
        Language: Marathi and English.
        Tasks:
        1. Give SIP calculation for long term (12% return).
        2. Explain the benefits of Overnight Funds for short term in very easy terms.
        3. Explain the Friday withdrawal/Weekend interest scenario.
        """
        
        try:
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            st.info(response.text)
            
            # Graph
            chart_df = pd.DataFrame(st.session_state.goals)
            fig = px.pie(chart_df, values='amt', names='name', title="Wealth Allocation")
            st.plotly_chart(fig)
            
        except Exception as e:
            st.error(f"Error: {e}")

    if st.button("🔄 Start New Plan"):
        st.session_state.goals = []
        st.session_state.page = "start"
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.page_link("https://wealthrise.guru", label="🏠 Back to WealthRise Home")
