import streamlit as st
from rca_generator import generate_rca

st.set_page_config(page_title="AI Incident Triage Bot")

st.title("🚨 AI Incident Triage Bot")

ticket = st.text_area("Paste new incident / error log:")

if st.button("Triage Incident"):
    if ticket:
        with st.spinner("Analyzing similar incidents..."):
            report, similarity_info, severity = generate_rca(ticket)
            st.success(f"RCA Generated | Predicted Severity: {severity}")
            st.markdown(report)
    with st.expander("🔍 Retrieved Similar Incidents + Similarity Scores"):
           st.write(similarity_info)
else:
        st.warning("Please enter incident details.")