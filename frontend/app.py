import streamlit as st
import requests
import matplotlib.pyplot as plt

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
# EXPENSE CHART
# =========================
def render_expense_chart(data):
    st.subheader("📊 Expense Breakdown")

    if "categories" not in data or "values" not in data:
        st.warning("No category data returned")
        return

    fig, ax = plt.subplots(figsize=(2, 2))
    wedges, _, _ = ax.pie(
        data["values"],
        autopct="%1.1f%%",
        textprops={'fontsize': 8}
    )

    ax.set_title("Expense Breakdown", fontsize=10)
    ax.legend(
        wedges,
        data["categories"],
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize=8
    )

    st.pyplot(fig, use_container_width=False)


# =========================
# RISK PROFILE
# =========================
def render_risk_profile(data):
    st.subheader("⚠ Risk Profile")

    risk = data.get("risk_profile", "Unknown").lower()

    if risk == "high":
        st.error("High Risk")
    elif risk == "moderate":
        st.warning("Moderate Risk")
    else:
        st.success("Low Risk")


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
            st.success("✅ Analysis Completed!")

            render_expense_chart(result)
            render_risk_profile(result)
            render_advice(result)


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

    result = post_request(QA_API, json=payload)

    if result:
        st.session_state.qa_response = result.get("raw", "No response received.")


# =========================
# FEEDBACK HANDLER
# =========================
def submit_feedback(query):
    payload = {
        "query": query,
        "response": st.session_state.qa_response,
        "correct_decision": st.session_state.correct_decision,
        "compliant": st.session_state.compliant,
        "fraud_detected": st.session_state.fraud_detected,
        "safe_reasoning": st.session_state.safe_reasoning
    }

    result = post_request(FEEDBACK_API, json=payload)

    if result:
        reward = result.get("reward", 0)
        st.success(f"✅ Feedback submitted! Reward Score: {reward}")


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

    if file and st.button("🚀 Analyze"):
        analyze_finances(file, profile)

    # =========================
    # QA SECTION
    # =========================
    st.header("💬 Ask Financial Questions")

    with st.form("qa_form"):
        query = st.text_input("Ask something like: Can I afford a loan?")
        submit = st.form_submit_button("Ask AI")

    if submit and query:
        handle_qa(query, profile)

    # =========================
    # RESPONSE DISPLAY
    # =========================
    if st.session_state.qa_response:
        st.markdown("### 🤖 AI Response")
        st.text(st.session_state.qa_response)

        st.markdown("---")
        st.markdown("### 🙋‍♀️ Provide Feedback")

        col1, col2 = st.columns(2)

        with col1:
            st.session_state.correct_decision = st.checkbox(
                "✅ Correct Decision",
                value=st.session_state.correct_decision
            )
            st.session_state.compliant = st.checkbox(
                "📜 Policy Compliant",
                value=st.session_state.compliant
            )

        with col2:
            st.session_state.fraud_detected = st.checkbox(
                "🚨 Fraud Detected",
                value=st.session_state.fraud_detected
            )
            st.session_state.safe_reasoning = st.checkbox(
                "🧠 Safe Reasoning",
                value=st.session_state.safe_reasoning
            )

        if st.button("Submit Feedback"):
            submit_feedback(query)


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    main()
