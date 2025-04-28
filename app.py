import streamlit as st
import pandas as pd
import sys
import os
from dotenv import load_dotenv
import html
import re
import argparse
import subprocess
import json
import base64

sys.path.append(os.path.abspath('.'))
src_dir = os.path.join(os.path.abspath('.'), 'src')
if src_dir not in sys.path:
    sys.path.append(src_dir)
comparison_src_dir = os.path.join(os.path.abspath('.'), 'src', 'comparison', 'src')
if comparison_src_dir not in sys.path:
    sys.path.append(comparison_src_dir)

from src.comparison.src.policy_loader import load_policies
from src.comparison.src.policy_comparator import PolicyComparator
from src.qa.qa import load_policy_link, load_document, chunk_text, build_index, retrieve_relevant_chunks, generate_answer
from src.summary.summary import summarize_policy_for_platform, format_summary_for_html, format_reference_quotes

load_dotenv()

st.set_page_config(
    page_title="Privacy Policy Analysis Tool",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        @import url("https://fonts.googleapis.com/css2?family=Lexend:wght@100..900&family=Red+Hat+Display:ital,wght@0,300..900;1,300..900&display=swap");

        * {
            font-family: 'Lexend', sans-serif !important;
            font-optical-sizing: auto;
            font-weight: 200px;
            font-style: normal;
        }
        .main-header {
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 1.5rem;
            text-align: center;
            color: #1E3A8A;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            padding: 0.5rem 0;
            animation: fadeIn 1s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .feature-header {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: #2563EB;
            border-bottom: 2px solid #E5E7EB;
            padding-bottom: 0.5rem;
            animation: slideIn 0.5s ease-in-out;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .card {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid #E5E7EB;
        }
        .tool-section {
            padding: 10px;
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        .tool-section:hover {
            background-color: #F9FAFB;
        }
        .answer-container {
            background-color: #F0F9FF;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #2563EB;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stTabs {
            background-color: #F9FAFB;
            border-radius: 10px;
            padding: 0.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            background-color: #F3F4F6;
            border-radius: 8px;
            padding: 4px;
            margin-bottom: 1rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            white-space: pre-wrap;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 6px;
            transition: all 0.2s ease;
            margin: 0 3px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: none;
        }
        .stTabs [aria-selected="false"] {
            background-color: transparent;
            color: #4B5563;
        }
        .stTabs [aria-selected="true"] {
            background-color: #DBEAFE;
            color: #1E40AF;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .stButton > button {
            font-weight: 600;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            transition: all 0.2s ease;
            background-color: #2563EB;
            color: white;
        }
        .stButton > button:hover {
            background-color: #1D4ED8;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        .stSelectbox > div > div {
            background-color: #F9FAFB;
            border-radius: 8px;
            border: 1px solid #E5E7EB;
        }
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 1px solid #E5E7EB;
            padding: 0.75rem;
        }
        .streamlit-expanderHeader {
            font-weight: 600;
            color: #4B5563;
            background-color: #F3F4F6;
            border-radius: 8px;
        }
        .stAlert {
            border-radius: 8px;
        }
        footer {
            border-top: 1px solid #E5E7EB;
            padding-top: 20px;
            margin-top: 40px;
            color: #6B7280;
            font-size: 0.9rem;
            text-align: center;
        }
    </style>
    <div class="main-header">Your privacy, made simple.</div>
""", unsafe_allow_html=True)

# logo
BASE_DIR = os.path.dirname(__file__)
bkc_logo_path = os.path.join(BASE_DIR, "screenshots", "bkc_logo.png")
asml_logo_path = os.path.join(BASE_DIR, "screenshots", "asml_logo.jpeg")

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

enc1 = img_to_base64(bkc_logo_path)
enc2 = img_to_base64(asml_logo_path)

col1, col2, col3, col4 = st.columns([1,1,1,1])
with col2:
    st.markdown(
        f"<div style='display:flex; justify-content:right; padding-top:3rem; padding-bottom:5rem;'>"
        f"<img src='data:image/png;base64,{enc1}' width='200' />"
        f"</div>",
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"<div style='display:flex; justify-content:left; padding-top:3rem;padding-bottom:5rem;'>"
        f"<img src='data:image/png;base64,{enc2}' width='250' />"
        f"</div>",
        unsafe_allow_html=True,
    )

@st.cache_data
def get_policy_df():
    return load_policies()

@st.cache_data
def load_privacy_db():
    return pd.read_csv("src/summary/privacy_db.csv")

try:
    policy_df = get_policy_df()
    platforms = sorted(policy_df['Platform'].unique())
except Exception as e:
    st.error(f"Error loading policy data: {str(e)}")
    platforms = []

try:
    privacy_db = load_privacy_db()
    all_platforms = sorted(privacy_db["Platform"].unique())
except Exception as e:
    st.error(f"Error loading privacy_db.csv: {str(e)}")
    all_platforms = []

if not platforms and all_platforms:
    platforms = all_platforms
elif all_platforms:
    combined_platforms = sorted(list(set(platforms) | set(all_platforms)))
    platforms = combined_platforms

if not platforms:
    st.error("No platform data available. Please check your data files.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["❓ Policy Q&A", "📝 Policy Summary", "📊 Policy Comparison"])

with tab1:
    st.markdown('<div class="feature-header">Ask Questions About Privacy Policies</div>', unsafe_allow_html=True)
    st.write("Ask any question about a platform's privacy policy and get accurate answers powered by AI.")
    qa_platform = st.selectbox("Select a platform", all_platforms, key="qa_platform")
    user_question = st.text_input("Enter your question about the privacy policy:", placeholder="e.g., How does this platform share my data with third parties?", key="qa_question")
    col1, col2 = st.columns([1, 3])
    with col1:
        qa_button = st.button("🔍 Get Answer", key="qa_btn")
    if qa_button:
        if user_question:
            try:
                with st.spinner('🔄 Analyzing the privacy policy...'):
                    platform_id = qa_platform.lower().replace(" ", "_")
                    st.info(f"Searching for policy information for: {qa_platform}")
                    txt_href = load_policy_link(platform_id)
                    document = load_document(txt_href)
                    chunks = chunk_text(document)
                    index, chunk_embeddings = build_index(chunks)
                    relevant_chunks = retrieve_relevant_chunks(user_question, chunks, index, chunk_embeddings)
                    answer = generate_answer(user_question, relevant_chunks)
                    st.subheader("Answer:")
                    st.markdown(f"<div style=\"background-color: #F0F9FF; padding: 20px; border-radius: 10px; border-left: 5px solid #2563EB; margin-bottom: 20px;\">{answer}</div>", unsafe_allow_html=True)
                    st.markdown(f"**Source:** [Link to Privacy Policy]({txt_href})")
            except Exception as e:
                st.error(f"Error processing your question: {str(e)}")
                st.error("Make sure the selected platform has a valid privacy policy link in the database.")
        else:
            st.warning("Please enter a question.")

with tab2:
    st.markdown('<div class="feature-header">Privacy Policy Summary</div>', unsafe_allow_html=True)
    st.write("Get a comprehensive, structured summary of a platform's privacy policy organized by key topics.")
    summary_platform = st.selectbox("Select a platform", all_platforms, key="summary_platform")
    col1, col2 = st.columns([1, 3])
    with col1:
        summary_button = st.button("📋 Generate Summary", key="summary_btn")
    if summary_button:
        try:
            with st.spinner('🔄 Generating privacy policy summary...'):
                summary, refs, link = summarize_policy_for_platform(summary_platform)
                formatted_summary_html = format_summary_for_html(summary)
                formatted_refs_html = format_reference_quotes(refs)
                if summary:
                    st.subheader(f"Privacy Summary for {summary_platform}")
                    st.markdown(f"<div style=\"background-color: #F0F9FF; padding: 20px; border-radius: 10px; border-left: 5px solid #2563EB; margin-bottom: 20px;\">{formatted_summary_html}</div>", unsafe_allow_html=True)
                    st.subheader("Original Privacy Policy")
                    st.markdown(f"[View original privacy policy]({link})")
                    with st.expander("View Source References"):
                        st.markdown(f"<div style=\"background-color: #F0F9FF; padding: 20px; border-radius: 10px; border-left: 5px solid #2563EB; margin-bottom: 20px;\">{formatted_refs_html}</div>", unsafe_allow_html=True)
                else:
                    st.error("Could not generate a summary. The platform might not be available.")
        except Exception as e:
            st.error(f"Error generating summary: {str(e)}")

with tab3:
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
    if not platforms:
        st.error("⚠️ Policy data is not available. Please check that privacy_db.csv file exists in src/summary/ directory.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            platform_a = st.selectbox("Select the first platform", platforms, key="platform_a")
        with col2:
            default_b_index = 1 if len(platforms) > 1 else 0
            platform_b = st.selectbox("Select the second platform", platforms, index=default_b_index, key="platform_b")
        comparator = PolicyComparator(api_key=os.getenv('GEMINI_API_KEY'))
        if st.button("Compare Policies 🚀", key="compare_btn"):
            if platform_a != platform_b:
                try:
                    with st.spinner('Comparing privacy policies...'):
                        result = comparator.compare_policies_gemini(platform_a, platform_b, policy_df)
                        st.subheader(f"🔍 Comparing {platform_a} and {platform_b} Privacy Policies")
                        comparison_md = result['comparison']
                        for citation_id in result['citations_a']:
                            comparison_md = comparison_md.replace(f"[{citation_id}]", f"[{citation_id}](#{citation_id.lower()})")
                        for citation_id in result['citations_b']:
                            comparison_md = comparison_md.replace(f"[{citation_id}]", f"[{citation_id}](#{citation_id.lower()})")
                        st.markdown(comparison_md, unsafe_allow_html=True)
                        with st.expander(f"📝 Citations for {platform_a}"):
                            for citation_id, text in result['citations_a'].items():
                                st.markdown(f"<a id='{citation_id.lower()}'></a>**[{citation_id}]**: {text}", unsafe_allow_html=True)
                        with st.expander(f"📝 Citations for {platform_b}"):
                            for citation_id, text in result['citations_b'].items():
                                st.markdown(f"<a id='{citation_id.lower()}'></a>**[{citation_id}]**: {text}", unsafe_allow_html=True)
                        st.info("**Important Note:** This comparison is based on the latest version of the complete privacy policies for each platform. Citations are provided for verification.")
                except Exception as e:
                    st.error(f"Error during comparison: {str(e)}")
                    st.error("Please make sure you have set the GEMINI_API_KEY in your .env file and that privacy_db.csv is correctly loaded.")
            else:
                st.error("⚠️ Please select two different platforms for comparison.")

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

st.markdown("---")
st.markdown("""
<footer>
    <div>
        <p>© 2025 Privacy Policy Analysis Tool | ASML Lab, Berkman Klein Center</p>
        <p>Powered by Gemini AI Models</p>
    </div>
</footer>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
      .stTabs [data-baseweb="tab"] {
        font-size: 5rem !important;
      }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
      .stTabs [data-baseweb="tab-list"] {
        display: flex !important;
        justify-content: center !important;
      }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
  <style>
    /* spread tabs apart */
    .stTabs [data-baseweb="tab-list"] {
      display: flex !important;
      justify-content: center !important;
      gap: 2rem !important;   /* increase this for more spacing */
    }
  </style>
""", unsafe_allow_html=True)