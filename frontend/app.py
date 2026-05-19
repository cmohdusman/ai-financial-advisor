import streamlit as st
import requests
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Financial Advisor", layout="wide")

st.title("💰 AI Financial Advisor & Portfolio Assistant")

# =========================
# Sidebar: User Profile
# =========================
st.sidebar.header("👤 User Profile")

age = st.sidebar.number_input("Age", 18, 100, 30)
salary = st.sidebar.number_input("Salary", value=50000.0)
investments = st.sidebar.number_input("Investments", value=100000.0)
loans = st.sidebar.number_input("Loans", value=20000.0)
goals = st.sidebar.text_area("Goals", "Save for house")

# =========================
# File Upload
# =========================
st.header("📂 Upload Transaction CSV")
file = st.file_uploader("Upload your transactions file", type=["csv"])

# =========================
# Analyze Finance
# =========================
if file and st.button("🚀 Analyze"):

    with st.spinner("Analyzing financial data..."):

        # ✅ IMPORTANT: correct file format
        files = {
            "file": (file.name, file, "text/csv")
        }

        params = {
            "age": age,
            "salary": salary,
            "investments": investments,
            "loans": loans,
            "goals": goals
        }

        try:
            response = requests.post(
                "http://localhost:8000/analyze/",
                files=files,
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                st.session_state.analysis_data = data

                st.success("✅ Analysis Completed!")

                # =========================
                # Expense Chart
                # =========================
                st.subheader("📊 Expense Breakdown")

                if "categories" in data and "values" in data:
                    # ✅ Create centered section with limited width
                    
                    col1, col2 = st.columns([1, 3])  # 👈 small left, big empty right
                    with col1:
                        fig, ax = plt.subplots(figsize=(3, 3))

                        wedges, texts, autotexts = ax.pie(
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
                        st.pyplot(fig)
                else:
                    st.warning("No category data returned")

                # =========================
                # Risk Profile
                # =========================
                st.subheader("⚠ Risk Profile")
                risk = data.get("risk_profile", "Unknown")

                if risk.lower() == "high":
                    st.error("High Risk")
                elif risk.lower() == "moderate":
                    st.warning("Moderate Risk")
                else:
                    st.success("Low Risk")

                # =========================
                # Advice
                # =========================
                st.subheader("💡 Financial Advice")

                advice = data.get("advice", [])

                if isinstance(advice, list):
                    for a in advice:
                        st.write(f"✅ {a}")
                else:
                    st.write(advice)

                # =========================
                # Insights (optional)
                # =========================
                if "insights" in data:
                    st.subheader("📌 Insights")
                    for i in data["insights"]:
                        st.write(f"🔹 {i}")

            else:
                st.error(f"❌ Backend error: {response.text}")

        except Exception as e:
            st.error(f"❌ Connection failed: {e}")

# =========================
# QA Section
# =========================
# ✅ Step 3: ALWAYS SHOW RESPONSE if exists
# =========================
# QA Section
# =========================
st.header("💬 Ask Financial Questions")

# ✅ Form for Enter-key submission
with st.form("qa_form"):
    query = st.text_input("Ask something like: Can I afford a loan?")
    submit = st.form_submit_button("Ask AI")

# ✅ Initialize session state safely
if "qa_response" not in st.session_state:
    st.session_state.qa_response = None

if "correct_decision" not in st.session_state:
    st.session_state.correct_decision = False
if "compliant" not in st.session_state:
    st.session_state.compliant = False
if "fraud_detected" not in st.session_state:
    st.session_state.fraud_detected = False
if "safe_reasoning" not in st.session_state:
    st.session_state.safe_reasoning = False

# ✅ Handle Ask AI
if submit and query:

    # ✅ Get analysis data safely
    analysis_data = st.session_state.get("analysis_data", {})

    payload = {
        "query": query,
        "age": int(age),
        "salary": float(salary),
        "investments": float(investments),
        "loans": float(loans),
        "analysis": {
            "categories": analysis_data.get("categories", []),
            "values": analysis_data.get("values", []),
            "insights": analysis_data.get("insights", [])
        }
    }

    try:
        response = requests.post(
            "http://localhost:8000/qa/",
            json=payload
        )

        if response.status_code == 200:
            result = response.json()

            # ✅ Store response
            st.session_state.qa_response = result["response"]

            # ✅ Reset feedback on new question
            st.session_state.correct_decision = False
            st.session_state.compliant = False
            st.session_state.fraud_detected = False
            st.session_state.safe_reasoning = False

        else:
            st.error(f"❌ Error {response.status_code}")

    except Exception as e:
        st.error(f"❌ Connection failed: {e}")


# ✅ =========================
# ✅ SHOW RESPONSE + FEEDBACK
# ✅ =========================
if st.session_state.get("qa_response"):

    st.markdown("### 🤖 AI Response")
    st.text(st.session_state.qa_response)   # ✅ clean rendering (no color issues)

    # ✅ Feedback Section
    st.markdown("---")
    st.markdown("### 🙋‍♀️ Provide Feedback")

    col1, col2 = st.columns(2)

    with col1:
        st.session_state.correct_decision = st.checkbox(
            "✅ Correct Decision",
            value=st.session_state.correct_decision
        )
        st.session_state.compliant = st.checkbox(
            "✅ Policy Compliant",
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

    # ✅ Submit feedback
    if st.button("Submit Feedback"):

        feedback_payload = {
            "query": query,
            "response": st.session_state.qa_response,
            "correct_decision": st.session_state.correct_decision,
            "compliant": st.session_state.compliant,
            "fraud_detected": st.session_state.fraud_detected,
            "safe_reasoning": st.session_state.safe_reasoning
        }

        try:
            fb_response = requests.post(
                "http://localhost:8000/feedback/",
                json=feedback_payload
            )

            if fb_response.status_code == 200:
                reward = fb_response.json()["reward"]
                st.success(f"✅ Feedback submitted! Reward Score: {reward}")
            else:
                st.error("❌ Feedback failed")

        except Exception as e:
            st.error(f"❌ Feedback error: {e}")