from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import argparse
import pandas as pd
import requests
import google.generativeai as genai

# ==== Step 1: Configure Gemini ====
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("GEMINI_API_KEY environment variable not set.")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ==== Step 2: Fetch and chunk policy text ====
def fetch_text_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def chunk_text_by_paragraph(text, max_chars=2000, min_words=4):
    raw_paragraphs = [p.strip() for p in text.split("\n\n")]
    # Filter out short paragraphs to reduce noise
    paragraphs = [p for p in raw_paragraphs if len(p.split()) >= min_words]

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 < max_chars:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


# ==== Step 3: Define each summarization question ====
QUESTIONS = {
    "a. Type of data collected": "What types of data are collected?",
    "b. Purpose of data collection": "What is the purpose of collecting data?",
    "c. Data sharing and disclosure": "How is data shared or disclosed?",
    "d. User rights and choices": "What rights or choices do users have?",
    "e. Data storage and security": "How is data stored and protected?",
    "f. Use of cookies and tracking technologies": "How are cookies or tracking technologies used?",
    "g. Other important information": "Is there any other important info, such as children’s privacy or policy changes?"
}

# ==== Step 4: Vectorize and select relevant chunks ====
def retrieve_relevant_chunks(chunks, question, top_k=8):
    corpus = chunks + [question]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)
    similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
    top_indices = similarities.argsort()[::-1][:top_k]
    return [chunks[i] for i in top_indices if similarities[i] > 0.02]

# ==== Step 5: RAG + Similarity-based summarization ====
def rag_summarize_with_similarity(policy_chunks, company, original_url):
    final_summary = []
    references = []

    for label, question in QUESTIONS.items():
        relevant_chunks = retrieve_relevant_chunks(policy_chunks, question)
        
        if not relevant_chunks:
            final_summary.append(f"{label}\nNot mentioned.")
            references.append(f"References for {label}:\nNone found.")
            continue

        combined_context = "\n\n".join(relevant_chunks)
        prompt = f"""
You are a legal assistant AI summarizing a privacy policy for {company}.
Answer the following question **only based on the provided text below**.
If the answer is not directly mentioned, say "Not mentioned."

Question: {question}

Text:
\"\"\"
{combined_context}
\"\"\"
Please Provide an answer grounded in the original text and not fabricate information.
"""

        response = model.generate_content(prompt)
        final_summary.append(f"{label}\n{response.text.strip()}")
        references.append(f"References for {label}:\n" + "\n---\n".join(relevant_chunks))

    return "\n\n".join(final_summary), "\n\n".join(references), original_url

# ==== Step 6: Load from CSV and run ====
def summarize_policy_for_platform(platform_name, csv_path="privacy_db.csv"):
    df = pd.read_csv(csv_path)
    match = df[df["Platform"].str.lower() == platform_name.lower()]

    if match.empty:
        print(f"Platform '{platform_name}' not found in {csv_path}.")
        return None, None, None

    txt_url = match.iloc[0]["Privacy Policy Txt"]
    original_url = match.iloc[0]["Privacy Policy URL"]
    company = match.iloc[0]["Platform"]

    policy_text = fetch_text_from_url(txt_url)
    chunks = chunk_text_by_paragraph(policy_text)

    return rag_summarize_with_similarity(chunks, company, original_url)

# ==== Command-line interface ====
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize a platform's privacy policy using similarity-aware RAG + Gemini.")
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

