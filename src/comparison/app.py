import streamlit as st
import pandas as pd
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath('.'))

from src.policy_loader import load_policies
from src.policy_comparator import PolicyComparator

load_dotenv()

data_path = "./data"
policy_df = load_policies(data_path)

st.markdown("""
    <style>
        .single-line-title {
            white-space: nowrap;
            font-size: 2rem;
            font-weight: bold;
            padding-bottom: 1rem;
        }
    </style>
    <div class='single-line-title'>📑 Cross-App Privacy Policy Comparison</div>
""", unsafe_allow_html=True)

platforms = sorted(policy_df['Platform'].unique())

col1, col2 = st.columns(2)

with col1:
    platform_a = st.selectbox("Select the first platform", platforms)

with col2:
    platform_b = st.selectbox("Select the second platform", platforms, index=1)

comparator = PolicyComparator(api_key=os.getenv('GEMINI_API_KEY'))

if st.button("Compare Policies 🚀"):
    if platform_a != platform_b:
        with st.spinner('Comparing privacy policies...'):
            result = comparator.compare_policies_gemini(platform_a, platform_b, policy_df)

            st.subheader(f"🔍 Comparing {platform_a} and {platform_b} Privacy Policies")

            # Render clickable citations
            comparison_md = result['comparison']
            for citation_id in result['citations_a']:
                comparison_md = comparison_md.replace(
                    f"[{citation_id}]",
                    f"[{citation_id}](#{citation_id.lower()})"
                )

            for citation_id in result['citations_b']:
                comparison_md = comparison_md.replace(
                    f"[{citation_id}]",
                    f"[{citation_id}](#{citation_id.lower()})"
                )

            st.markdown(comparison_md, unsafe_allow_html=True)

            with st.expander(f"📝 Citations for {platform_a}"):
                for citation_id, text in result['citations_a'].items():
                    st.markdown(f"<a id='{citation_id.lower()}'></a>**[{citation_id}]**: {text}", unsafe_allow_html=True)

            with st.expander(f"📝 Citations for {platform_b}"):
                for citation_id, text in result['citations_b'].items():
                    st.markdown(f"<a id='{citation_id.lower()}'></a>**[{citation_id}]**: {text}", unsafe_allow_html=True)

            st.info("**Important Note:** This comparison is based on the latest version of the complete privacy policies for each platform. Citations are provided for verification.")
    else:
        st.error("⚠️ Please select two different platforms for comparison.")

# Citation CSS
st.markdown("""
    <style>
        .citation {
            color: #0645AD;
            text-decoration: underline;
            cursor: help;
        }
        .citation:hover {
            background-color: #f0f0f0;
        }
    </style>
""", unsafe_allow_html=True)
