import streamlit as st
from rca_generator import generate_rca

st.set_page_config(page_title="AI Incident Triage Bot")

st.title("🚨 AI Incident Triage Bot")
st.write("🟢 App initialized successfully")

ticket = st.text_area("Paste new incident / error log:")

if st.button("Triage Incident"):
    if not ticket.strip():
        st.warning("Please enter incident details.")
    else:
        with st.spinner("Analyzing similar incidents..."):
            try:
                report, similarity_info, severity = generate_rca(ticket)

                st.success(f"RCA Generated | Predicted Severity: {severity}")
                st.markdown(report)

                with st.expander("🔍 Retrieved Similar Incidents + Similarity Scores"):
                    st.write(similarity_info)

            except Exception as e:
                st.error("Failed to generate RCA")
                st.exception(e)
