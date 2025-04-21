"""
Privacy Policy Analysis Tool

This application combines three features:
1. Policy Q&A - Ask specific questions about a platform's privacy policy
2. Policy Summary - Get a structured summary of a platform's privacy policy
3. Policy Comparison - Compare privacy policies between two platforms

The application uses Gemini models to perform natural language processing tasks
on privacy policy documents.

To run:
streamlit run app.py

Requirements:
- Python 3.8+
- Required packages in requirements.txt
- Gemini API key in .env file
"""

import streamlit as st
import pandas as pd
import sys
import os
from dotenv import load_dotenv
import argparse
import subprocess
import json

sys.path.append(os.path.abspath('.'))

# Fix module import paths if needed
src_dir = os.path.join(os.path.abspath('.'), 'src')
if src_dir not in sys.path:
    sys.path.append(src_dir)

comparison_src_dir = os.path.join(os.path.abspath('.'), 'src', 'comparison', 'src')
if comparison_src_dir not in sys.path:
    sys.path.append(comparison_src_dir)

# Import components from each feature
from src.comparison.src.policy_loader import load_policies
from src.comparison.src.policy_comparator import PolicyComparator
from src.qa.qa import load_policy_link, load_document, chunk_text, build_index, retrieve_relevant_chunks, generate_answer
from src.summary.summary import summarize_policy_for_platform

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Privacy Policy Analysis Tool",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        /* Main header styling */
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
        
        /* Feature header styling */
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
        
        /* Card styling for content sections */
        .card {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid #E5E7EB;
        }
        
        /* Tool section styling */
        .tool-section {
            padding: 10px;
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        
        .tool-section:hover {
            background-color: #F9FAFB;
        }
        
        /* Answer container styling */
        .answer-container {
            background-color: #F0F9FF;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #2563EB;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Tab styling */
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
        
        /* Button styling */
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
        
        /* Select box styling */
        .stSelectbox > div > div {
            background-color: #F9FAFB;
            border-radius: 8px;
            border: 1px solid #E5E7EB;
        }
        
        /* Input styling */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 1px solid #E5E7EB;
            padding: 0.75rem;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            font-weight: 600;
            color: #4B5563;
            background-color: #F3F4F6;
            border-radius: 8px;
        }
        
        /* Info/error box styling */
        .stAlert {
            border-radius: 8px;
        }
        
        /* Footer styling */
        footer {
            border-top: 1px solid #E5E7EB;
            padding-top: 20px;
            margin-top: 40px;
            color: #6B7280;
            font-size: 0.9rem;
            text-align: center;
        }
    </style>
    <div class="main-header">🔒 Privacy Policy Analysis Tool</div>
""", unsafe_allow_html=True)

# Load platform data
try:
    # Load policies from privacy_db.csv
    policy_df = load_policies()
    platforms = sorted(policy_df['Platform'].unique())
    print(f"✅ Loaded {len(platforms)} platforms from privacy_db.csv for comparison")
except Exception as e:
    st.error(f"Error loading policy data: {str(e)}")
    platforms = []
    
# Try to load from the CSV for QA and Summary features (direct access)
try:
    privacy_db = pd.read_csv("src/summary/privacy_db.csv")
    all_platforms = sorted(privacy_db["Platform"].unique())
    print(f"✅ Loaded {len(all_platforms)} platforms from privacy_db.csv for QA and Summary")
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

# Create tabs for the three features
tab1, tab2, tab3 = st.tabs(["❓ Policy Q&A", "📝 Policy Summary", "📊 Policy Comparison"])

# Tab 1: Q&A Feature
with tab1:
    st.markdown('<div class="feature-header">Ask Questions About Privacy Policies</div>', unsafe_allow_html=True)
    st.write("Ask any question about a platform's privacy policy and get accurate answers powered by AI.")
    
    # Platform selection
    qa_platform = st.selectbox("Select a platform", all_platforms, key="qa_platform")
    
    # Question input
    user_question = st.text_input("Enter your question about the privacy policy:", 
                                 placeholder="e.g., How does this platform share my data with third parties?", 
                                 key="qa_question")
    
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
                    st.markdown(f"""
                    <div style="background-color: #F0F9FF; padding: 20px; border-radius: 10px; border-left: 5px solid #2563EB; margin-bottom: 20px;">
                    {answer}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"**Source:** [Link to Privacy Policy]({txt_href})")
            except Exception as e:
                st.error(f"Error processing your question: {str(e)}")
                st.error("Make sure the selected platform has a valid privacy policy link in the database.")
        else:
            st.warning("Please enter a question.")

# Tab 2: Summary Feature
with tab2:
    st.markdown('<div class="feature-header">Privacy Policy Summary</div>', unsafe_allow_html=True)
    st.write("Get a comprehensive, structured summary of a platform's privacy policy organized by key topics.")
    
    # Platform selection
    summary_platform = st.selectbox("Select a platform", all_platforms, key="summary_platform")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        summary_button = st.button("📋 Generate Summary", key="summary_btn")
    
    if summary_button:
        try:
            with st.spinner('🔄 Generating privacy policy summary...'):
                # Call the summary function
                summary, refs, link = summarize_policy_for_platform(summary_platform)
                
                if summary:
                    st.subheader(f"Privacy Summary for {summary_platform}")
                    st.markdown(f"""
                    <div style="background-color: #F0F9FF; padding: 20px; border-radius: 10px; border-left: 5px solid #2563EB; margin-bottom: 20px;">
                    {summary}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.subheader("Original Privacy Policy")
                    st.markdown(f"[View original privacy policy]({link})")
                    
                    with st.expander("View Source References"):
                        st.markdown(refs)
                else:
                    st.error("Could not generate a summary. The platform might not be available.")
        except Exception as e:
            st.error(f"Error generating summary: {str(e)}")

# Tab 3: Policy Comparison Feature
with tab3:
    st.markdown('<div class="feature-header">Compare Privacy Policies</div>', unsafe_allow_html=True)
    st.write("Analyze and compare the privacy policies of two different platforms side by side.")
    
    # Check if data is available for comparison
    if not platforms:
        st.error("⚠️ Policy data is not available. Please check that privacy_db.csv file exists in src/summary/ directory.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            platform_a = st.selectbox("First Platform", platforms, key="platform_a")
        
        with col2:
            # Select a different default for platform B
            default_b_index = 1 if len(platforms) > 1 else 0
            platform_b = st.selectbox("Second Platform", platforms, index=default_b_index, key="platform_b")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            compare_button = st.button("🔄 Compare Policies", key="compare_btn")
        
        if compare_button:
            if platform_a != platform_b:
                try:
                    with st.spinner('🔄 Comparing privacy policies...'):
                        comparator = PolicyComparator(api_key=os.getenv('GEMINI_API_KEY'))
                        
                        result = comparator.compare_policies_gemini(platform_a, platform_b, policy_df)
                        
                        st.subheader(f"🔍 Comparing {platform_a} and {platform_b} Privacy Policies")
                        
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
                        
                        st.markdown(f"""
                        <div style="background-color: #F0F9FF; padding: 20px; border-radius: 10px; border-left: 5px solid #2563EB; margin-bottom: 20px;">
                        {comparison_md}
                        </div>
                        """, unsafe_allow_html=True)
                        
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

# Footer
st.markdown("---")
st.markdown("""
<footer>
    <div>
        <p>© 2024 Privacy Policy Analysis Tool | ASML Lab, Berkman Klein Center</p>
        <p>Powered by Gemini AI Models</p>
    </div>
</footer>
""", unsafe_allow_html=True) 
