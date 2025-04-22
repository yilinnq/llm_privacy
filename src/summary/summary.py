import os
import argparse
import pandas as pd
import requests
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
import re 
import html

# ==== Step 1: Configure Gemini ====
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("GEMINI_API_KEY environment variable not set.")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ==== Step 2: Constants ====
TOKEN_LIMIT = 220000  # conservative threshold for Gemini input

QUESTIONS = {
    "a. Type of data collected": "What types of data are collected?",
    "b. Purpose of data collection": "What is the purpose of collecting data?",
    "c. Data sharing and disclosure": "How is data shared or disclosed?",
    "d. User rights and choices": "What rights or choices do users have?",
    "e. Data storage and security": "How is data stored and protected?",
    "f. Use of cookies and tracking technologies": "How are cookies or tracking technologies used?",
    "g. Other important information": (
        "Are there any other important privacy-related topics mentioned "
        "that have NOT been covered by the previous questions? "
        "Exclude details related to: types of data collected, purpose of collection, "
        "data sharing or disclosure, data storage or security, user rights or choices, "
        "and use of cookies or tracking technologies. "
        "Instead, focus on topics such as children’s privacy, international data transfer, "
        "policy updates, third-party links, or any special terms."
    )
}

# ==== Step 3: Utilities ====
def fetch_text_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def estimate_token_count(text):
    return len(text) // 4  # approx. 1 token = 4 characters

def chunk_text_by_paragraph(text, max_chars=1000, min_words=4):
    raw_paragraphs = [p.strip() for p in text.split("\n\n")]
    paragraphs = [p for p in raw_paragraphs if len(p.split()) >= min_words]
    chunks, current_chunk = [], ""
    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 < max_chars:
            current_chunk += para.strip() + "\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def embed_chunks(chunks, model):
    return model.encode(chunks, convert_to_tensor=True)

def retrieve_relevant_chunks(chunks, chunk_embeddings, question, model, top_k=8, similarity_threshold=0.01):
    question_embedding = model.encode(question, convert_to_tensor=True)
    similarities = cosine_similarity(
        question_embedding.cpu().numpy().reshape(1, -1),
        chunk_embeddings.cpu().numpy()
    ).flatten()
    top_indices = similarities.argsort()[::-1][:top_k]
    return [chunks[i] for i in top_indices if similarities[i] > similarity_threshold]

# ==== Step 4: Direct full-document summarization ====

def generate_summary_only(policy_text, company=None):
    company_note = f"The privacy policy belongs to {company}." if company else ""
    prompt = f"""
You are a legal assistant AI. {company_note} Please do not state other words except for the summary. 
Read the following privacy policy and produce a structured summary using the labels below and Please do not fabricate information:

1. Summary of the privacy policy:
   a. Type of data collected:
        1: 
        2: 
        3:
        ...
   b. Purpose of data collection:
        1: 
        2: 
        3:
        ...  
   c. Data sharing and disclosure:
        1: 
        2: 
        ...  
   d. User rights and choices:
        1: 
        2: 
        ...
   e. Data storage and security:
        1: 
        2: 
        ...
   f. Use of cookies and tracking technologies:
        1: 
        2: 
        ...
   g. Other important information (such as children’s privacy, changes to the policy etc.):
        1: 
        2: 
        ...

Here is the policy text:
\"\"\"
{policy_text}
\"\"\"

Please return only the summary and no other words, using exactly the labels and format provided above. Please provide grounded answer ONLY based on the provided policy text above and do not fabricate information. 
If the information for any section is missing or not mentioned, say "Missing" for that section and don't need to say anything else.

"""
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_references_only(policy_text, summary_text):
    prompt = f"""
You are a legal assistant AI. Given the summary below, return all the direct quotes from the privacy policy that support each part.

Instructions:
- For EACH bullet point in the summary, find **direct quotes** from the original policy that supports the point.
- If no relavent quote can be found or the original summary section is missing, say "Missing." DO NOT fabricate quotes. 

Summary:
\"\"\"
{summary_text}
\"\"\"

Original policy:
\"\"\"
{policy_text}
\"\"\"

Please make sure to cover all the points in the summary and output the references in this format:

Reference quote from the original privacy policy text:
    a. Type of data collected: 
        Reference 1: "..."
        Reference 2: "..."
        ...
    b. Purpose of data collection: 
        Reference 1: "..."
        Reference 2: "..."
    c. Data sharing and disclosure: 
        Reference 1: "..."
        Reference 2: "..."
        ...
    d. User rights and choices: 
        Reference 1: "..."
        Reference 2: "..."
        ...
    e. Data storage and security:
        Reference 1: "..."
        Reference 2: "..."
        ...
    f. Use of cookies and tracking technologies:  
        Reference 1: "..."
        Reference 2: "..."
        ...
    g. Other important information: 
        Reference 1: "..."
        Reference 2: "..."
        ...
"""
    response = model.generate_content(prompt)
    return response.text.strip()

def summarize_entire_document(policy_text, company=None, original_url=None):
    summary = generate_summary_only(policy_text, company=company)
    references = generate_references_only(policy_text, summary_text=summary)
    return summary, references, original_url



# ==== Step 5: RAG-based fallback ====
def rag_summarize_with_similarity(policy_chunks, company, original_url):
    final_summary, references = [], []
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    chunk_embeddings = embed_chunks(policy_chunks, embedder)

    for label, question in QUESTIONS.items():
        relevant_chunks = retrieve_relevant_chunks(policy_chunks, chunk_embeddings, question, embedder)
        if not relevant_chunks:
            final_summary.append(f"{label}\nNot mentioned.")
            references.append(f"References for {label}:\nNone found.")
            continue

        combined_context = "\n\n".join(relevant_chunks)
        prompt = f"""
You are a legal assistant AI summarizing a privacy policy for {company}.
Answer the following summarization question **only based on the provided text below**. 
If the answer is not directly mentioned, say "Not mentioned."

Question: {question}

Text:
\"\"\"
{combined_context}
\"\"\"

Provide a concise answer grounded in the original text.
"""
        response = model.generate_content(prompt)
        final_summary.append(f"{label}\n{response.text.strip()}")
        references.append(f"References for {label}:\n" + "\n---\n".join(relevant_chunks))

    return "\n\n".join(final_summary), "\n\n".join(references), original_url

# ==== Step 6: Main control logic ====
def summarize_policy_for_platform(platform_name, csv_path=None):
    if csv_path is None:
        # Try to determine the correct path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_csv = os.path.join(script_dir, "privacy_db.csv")
        
        if os.path.exists(default_csv):
            csv_path = default_csv
        else:
            # Try a relative path
            csv_path = os.path.join("src", "summary", "privacy_db.csv")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Could not find privacy_db.csv at {csv_path}")
    df = pd.read_csv(csv_path)
    match = df[df["Platform"].str.lower() == platform_name.lower()]
    if match.empty:
        print(f"Platform '{platform_name}' not found in {csv_path}.")
        return None, None, None

    txt_url = match.iloc[0]["Privacy Policy Txt"]
    original_url = match.iloc[0]["Privacy Policy URL"]
    company = match.iloc[0]["Platform"]
    policy_text = fetch_text_from_url(txt_url)

    if estimate_token_count(policy_text) < TOKEN_LIMIT:
        summary, reference, original_url = summarize_entire_document(policy_text, company, original_url)
        return summary, reference, original_url
    else:
        chunks = chunk_text_by_paragraph(policy_text)
        return rag_summarize_with_similarity(chunks, company, original_url)


def format_summary_for_html(summary_text):
    html_lines = []
    for line in summary_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("1. summary of the privacy policy"):
            continue  # Skip this line entirely
        if line.startswith("a.") or line.startswith("b.") or line.startswith("c.") or \
           line.startswith("d.") or line.startswith("e.") or line.startswith("f.") or line.startswith("g."):
            html_lines.append(f"<p><strong>{line}</strong></p>")
        elif line.startswith("1:") or line.startswith("2:") or line.startswith("3:") or line[0].isdigit():
            html_lines.append(f"<p style='margin-left: 1.5em;'>{line}</p>")
        else:
            html_lines.append(f"<p>{line}</p>")
    return "\n".join(html_lines)


def format_reference_quotes(ref_text):
    lines = ref_text.strip().splitlines()
    html_output = []
    section_label = None

    for line in lines:
        line = html.unescape(line.strip())

        # Match section headers like: a. Type of data collected:
        section_match = re.match(r"^([a-g])\.\s+(.*?):", line, re.IGNORECASE)
        if section_match:
            section_label = f"{section_match.group(1).lower()}. {section_match.group(2)}"
            html_output.append(f"<p><strong>{section_label}:</strong></p>")
            continue

        # Match references like: Reference 1: "..." (or unquoted text)
        ref_match = re.match(r"Reference\s+(\d+):\s+(.*)", line, re.IGNORECASE)
        if ref_match:
            number = ref_match.group(1)
            quote = ref_match.group(2).strip()
            quote = quote.strip('"')  # Remove existing quotes to avoid double quoting
            html_output.append(
                f"<p style='margin-left: 1.5em;'><strong>Reference {number}:</strong> \"{html.escape(quote)}\"</p>"
            )
            continue

        # Handle 'Missing'
        if "missing" in line.lower():
            html_output.append(f"<p style='margin-left: 1.5em;'><em style='color:#B91C1C;'>Missing</em></p>")

    return "\n".join(html_output)

        


# ==== Entry Point ====
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize a platform's privacy policy using hybrid Gemini + RAG.")
    parser.add_argument("--platform", required=True, help="Platform name as listed in the CSV")
    args = parser.parse_args()

    summary, refs, link = summarize_policy_for_platform(args.platform)
    if summary:
        print("=== Structured Privacy Summary ===\n")
        print(summary)
        print("\n=== Original URL ===")
        print(link)
        print("\n=== Source References ===")
        print(refs)
    else:
        print("No summary could be generated.")

