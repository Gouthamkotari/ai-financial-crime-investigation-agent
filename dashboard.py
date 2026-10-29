
import os

import requests
import streamlit as st

st.set_page_config(
    page_title="AI Financial Crime Investigation Agent",
    page_icon="🔎",
    layout="wide",
)

# Connect to the deployed FastAPI backend.
DEFAULT_API_URL = "https://financial-crime-api.onrender.com"

try:
    API_BASE_URL = st.secrets.get(
        "API_BASE_URL", DEFAULT_API_URL
    )
except Exception:
    API_BASE_URL = os.getenv("API_BASE_URL", DEFAULT_API_URL)

API_BASE_URL = API_BASE_URL.rstrip("/")

st.title("🔎 AI Financial Crime Investigation Agent")
st.caption(
    "Transaction risk scoring and evidence-based investigation"
)

st.info(
    "Enter transaction details below to generate a model-based "
    "risk assessment. Results are estimates and require human review."
)

with st.form("transaction_form"):
    st.subheader("Transaction details")

    col1, col2 = st.columns(2)

    with col1:
        step = st.number_input(
            "Transaction step",
            min_value=1,
            value=1,
            step=1,
            help="The transaction time step in the dataset.",
        )

        transaction_type = st.selectbox(
            "Transaction type",
            ["TRANSFER", "CASH_OUT", "PAYMENT", "CASH_IN", "DEBIT"],
        )

        amount = st.number_input(
            "Transaction amount",
            min_value=0.01,
            value=1000.00,
            step=100.00,
        )

        origin_account = st.text_input(
            "Origin account ID (optional)"
        )

    with col2:
        destination_account = st.text_input(
            "Destination account ID (optional)"
        )

        oldbalanceOrg = st.number_input(
            "Origin balance before transaction",
            min_value=0.0,
            value=5000.0,
            step=100.0,
        )

        newbalanceOrig = st.number_input(
            "Origin balance after transaction",
            min_value=0.0,
            value=4000.0,
            step=100.0,
        )

        oldbalanceDest = st.number_input(
            "Destination balance before transaction",
            min_value=0.0,
            value=100.0,
            step=100.0,
        )

        newbalanceDest = st.number_input(
            "Destination balance after transaction",
            min_value=0.0,
            value=1100.0,
            step=100.0,
        )

    submitted = st.form_submit_button(
        "Investigate Transaction",
        type="primary",
        use_container_width=True,
    )

if submitted:
    payload = {
        "step": int(step),
        "type": transaction_type,
        "amount": float(amount),
        "origin_account": origin_account.strip() or None,
        "destination_account": destination_account.strip() or None,
        "oldbalanceOrg": float(oldbalanceOrg),
        "newbalanceOrig": float(newbalanceOrig),
        "oldbalanceDest": float(oldbalanceDest),
        "newbalanceDest": float(newbalanceDest),
    }

    with st.spinner("Analyzing transaction..."):
        try:
            response = requests.post(
                f"{API_BASE_URL}/investigate",
                json=payload,
                timeout=120,
            )

            if response.ok:
                result = response.json()
                summary = result.get("case_summary", {})

                st.subheader("Investigation result")

                risk_level = summary.get("risk_level", "Unknown")
                risk_score = summary.get("risk_score", 0)

                col1, col2, col3 = st.columns(3)

                col1.metric("Risk level", risk_level)
                col2.metric(
                    "Risk score",
                    f"{float(risk_score):.1%}",
                )
                col3.metric(
                    "Transaction amount",
                    f"{float(summary.get('amount', amount)):,.2f}",
                )

                st.progress(
                    max(0.0, min(1.0, float(risk_score)))
                )

                st.subheader("Evidence and findings")
                evidence = result.get("evidence", [])

                if evidence:
                    for item in evidence:
                        with st.expander(
                            item.get("finding", "Finding")
                        ):
                            st.write(item.get("details", "No details"))
                else:
                    st.write("No evidence items were returned.")

                st.subheader("Balance analysis")
                st.write(
                    result.get(
                        "balance_note",
                        "No balance analysis was returned.",
                    )
                )

                st.subheader("Recommended actions")
                for action in result.get("recommended_actions", []):
                    st.markdown(f"- {action}")

                limitations = result.get("limitations", [])
                if limitations:
                    st.subheader("Limitations")
                    for limitation in limitations:
                        st.markdown(f"- {limitation}")

                st.warning(
                    "This model-generated score is not proof of fraud. "
                    "A qualified human reviewer should assess the evidence."
                )

            else:
                st.error(f"API returned {response.status_code}")
                try:
                    st.code(response.text)
                except Exception:
                    st.write("The API returned an error.")

        except requests.exceptions.Timeout:
            st.error(
                "The API took too long to respond. "
                "Please try again in a moment."
            )
        except requests.exceptions.RequestException as error:
            st.error(f"Could not connect to the API: {error}")

st.divider()
st.caption(
    "Backend: FastAPI on Render | "
    "Model: Random Forest V2 | "
    "For demonstration and investigation support"
)
