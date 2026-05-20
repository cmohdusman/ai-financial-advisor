import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd

# =========================
# CONFIG
# =========================
API_BASE_URL = "http://localhost:8000"
ANALYZE_API = f"{API_BASE_URL}/analyze/"
QA_API = f"{API_BASE_URL}/qa/"
FEEDBACK_API = f"{API_BASE_URL}/feedback/"

st.set_page_config(page_title="AI Financial Advisor", layout="wide")

# =========================
# SESSION STATE INIT
# =========================
DEFAULT_SESSION_STATE = {
    "analysis_data": {},
    "qa_response": None,
    "correct_decision": False,
    "compliant": False,
    "fraud_detected": False,
    "safe_reasoning": False,
    "analysis_done": False,
    "chat_history": []
}

for key, value in DEFAULT_SESSION_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================
# API HELPERS
# =========================
def post_request(url, retries=3, timeout=60, **kwargs):
    for attempt in range(retries):
        try:
            response = requests.post(url, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                st.warning("⏳ Retrying request...")
            else:
                st.error("❌ Request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ API Error: {str(e)}")
            break

    return None

# =========================
# SIDEBAR - USER PROFILE
# =========================
def render_sidebar():
    st.sidebar.header("👤 User Profile")

    profile = {
        "age": st.sidebar.slider("Age", 18, 100, 30),
        "salary": st.sidebar.slider("Salary", 100,100000, 10000),
        "investments": st.sidebar.slider("Investments", 100,100000,5000),
        "loans": st.sidebar.slider("Loans", 100,10000,5000),
        "goals": st.sidebar.text_area("Goals", "Save for house"),
    }
    
    return profile

# =========================
# Render BAR Chart
# =========================
def render_bar_chart(data):
    df = pd.DataFrame({
        "Category": data["categories"],
        "Amount": data["values"]
    }).sort_values(by="Amount", ascending=False)

    st.bar_chart(df.set_index("Category"))


# =========================
# RISK PROFILE
# =========================
def render_risk_profile(data):
    st.subheader("⚠ Risk Profile")

    risk = data.get("risk_profile", "Unknown").lower()

    if risk == "aggressive":
        st.error("High Risk")
    elif risk == "conservative":
        st.warning("Low Risk")
    else:
        st.success(risk)

    print("data")
    print(data)
    justification = data.get("justification")
    print("justification")
    print(justification)
    if justification:
        st.markdown("### 📖 Justification")
        st.info(justification)



# =========================
# ADVICE & INSIGHTS
# =========================
def render_advice(data):
    st.subheader("💡 Financial Advice")

    advice = data.get("advice", [])
    if isinstance(advice, list):
        for item in advice:
            st.write(f"- {item}")
    else:
        st.write(advice)

    if "insights" in data:
        st.subheader("📌 Insights")
        for insight in data["insights"]:
            st.write(f"🔹 {insight}")


# =========================
# ANALYZE FUNCTION
# =========================
def analyze_finances(file, profile):
    with st.spinner("Analyzing financial data..."):

        files = {"file": (file.name, file, "text/csv")}

        result = post_request(
            ANALYZE_API,
            files=files,
            params=profile
        )

        if result:
            st.session_state.analysis_data = result
            st.session_state.analysis_done = True
            st.session_state.chat_history = []
            st.success(" Analysis Completed!")


# =========================
# QA HANDLER
# =========================
def handle_qa(query, profile):
    analysis_data = st.session_state.get("analysis_data", {})

    payload = {
        "query": query,
        "age": int(profile["age"]),
        "salary": int(profile["salary"]),
        "investments": int(profile["investments"]),
        "loans": int(profile["loans"]),
        "analysis": {
            "categories": analysis_data.get("categories", []),
            "values": analysis_data.get("values", []),
            "insights": analysis_data.get("insights", [])
        }
    }
    
    result = post_request(QA_API, json=payload, timeout=60)

    if result:
        if isinstance(result, dict):
            return result.get("raw", str(result))
        return str(result)

    return "❌ Failed to get response"


# =========================
# MAIN UI
# =========================
def main():
    st.title("💰 AI Financial Advisor & Portfolio Assistant")

    profile = render_sidebar()

    # =========================
    # FILE UPLOAD
    # =========================
    st.header("📂 Upload Transaction CSV")
    file = st.file_uploader("Upload your transactions file", type=["csv"])

    if st.button("🚀 Analyze"):
        if file:
            analyze_finances(file, profile)
        else:
            st.warning("Please upload a file first")
    
    if st.session_state.analysis_done:
        st.header("📊 Financial Analysis Results")
        render_bar_chart(st.session_state.analysis_data)
        render_risk_profile(st.session_state.analysis_data)
        render_advice(st.session_state.analysis_data)

   
    # =========================
    # CHATGPT-STYLE QA SECTION
    # =========================
    st.header("💬 Financial Chat Assistant")

    if not st.session_state.get("analysis_done", False):
        st.warning("⚠ Please run analysis first")
    else:
        #  Show chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        #  Chat input (ChatGPT style)
        user_input = st.chat_input("Ask a financial question...")

        if user_input:
            #  Add user message
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })

            #  Show user message immediately
            with st.chat_message("user"):
                st.write(user_input)

            #  Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = handle_qa(user_input, profile)

                    # fallback if your function doesn't return
                    if not response:
                        response = st.session_state.get("qa_response", "No response")

                    st.write(response)

            #  Save AI response
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })

            #  trigger UI refresh (prevents duplication issues)
            st.rerun()
    
# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    main()
