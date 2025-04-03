import os
import json
import requests
import os
import regex as re
import argparse
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from urllib.parse import quote

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

parser = argparse.ArgumentParser(description="Generate Q&A response.")
parser.add_argument('--company_name', type=str, choices=[
    "blackplanet", "bluesky", "bumble", "cato", "chess", "christian_mingle", "clubhouse",
    "coffee_meets_bagel", "eharmony", "feeld", "friendster", "gab", "gettr",
    "github", "gofundme", "goodreads", "her", "hinge", "instagram", "jodel", "kickstarter",
    "likee", "linkedin", "mastodon", "medium", "meetup", "nextdoor", "okcupid", "parler",
    "pinterest", "quora", "raya", "reddit", "sesearch_gate", "signal", "silver_singles",
    "slack", "snapchat", "strava", "supernova", "telegram", "tellonym", "threads", "tiktok",
    "tinder", "truth_social", "tumblr", "twitter_x", "vanatu", "vero", "whatsapp", "yareny", "youtube"
], required=True, help="The name of the company")
parser.add_argument('--question', type=str, help="The question to ask about the privacy policy")
args = parser.parse_args()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={GEMINI_API_KEY}"
)

BASE_URL = 'https://transparencydb.dev.berkmancenter.org/company/'


# embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def load_policy_link(policy_name):
    """
    Loads the policy link from the JSON file in the data_processing/policy_links folder.
    """
    json_file_path = os.path.join("../data_processing/policy_links", f"{policy_name}.json")
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, str):
        txt_href = data
    else:
        raise ValueError(f"Invalid format in {json_file_path}")
    print("✅ Policy file link found")
    return txt_href

def load_document(txt_href):
    """
    Downloads the document using txt_href link.
    """
    response = requests.get(txt_href)
    if response.status_code != 200:
        raise Exception(f"Could not load the document from {txt_href}")
    print("✅ Policy loaded")
    return response.text

def chunk_text(text, max_chunk_size=500):
    """
    Splits the text into chunks of approximately max_chunk_size words.
    Adjust the splitting logic as needed (e.g., by paragraph).
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_chunk_size):
        chunk = " ".join(words[i:i+max_chunk_size])
        chunks.append(chunk)
    print("✅ Chuncking complete")
    return chunks

def build_index(chunks):
    """
    Embeds the text chunks and builds a FAISS index for similarity search.
    """
    embeddings = embedder.encode(chunks, convert_to_tensor=False)
    embeddings = np.array(embeddings).astype("float32")
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    print("✅ FAISS embedding complete")
    return index, embeddings

def retrieve_relevant_chunks(question, chunks, index, chunk_embeddings, top_k=3):
    """
    Embeds the question and retrieves the top_k most similar text chunks.
    """
    question_embedding = embedder.encode([question], convert_to_tensor=False)
    question_embedding = np.array(question_embedding).astype("float32")
    faiss.normalize_L2(question_embedding)
    D, I = index.search(question_embedding, top_k)
    retrieved = [chunks[i] for i in I[0]]
    print("✅ Reterieved context")
    return retrieved

def generate_answer(question, context_chunks):
    """
    Generates an answer by calling the Gemini API using the gemini-2.0-flash-lite model.
    The API is called via a REST POST request with a payload that mirrors the provided curl example.
    """
    context = " ".join(context_chunks)
    input_text = f"question: {question} context: {context}"
    
    # Construct payload per the Gemini API documentation.
    payload = {
        "system_instruction": {
            "parts": [
                {
                "text": "You are a privacy policy expert. You will answer user's question accurately given the context provided, and you will include the reference text content you used to generate the answer by marking it as 'Reference Used:'."
                }
            ]
        },
        "contents": [
            {
                "parts": [
                    {
                        "text": input_text
                    }
                ]
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Gemini API call failed with status code {response.status_code}: {response.text}")
    
    result = response.json()
    # print("🐛 Debug Gemini API response:", result)
    
    candidate = result.get("candidates", [{}])[0]
    answer = candidate.get("content", {}).get("parts", [{}])[0].get("text")
    
    if not answer:
        raise Exception("No answer found in the Gemini API response.")
    return answer


# def extract_reference_snippet(answer_text):
#     """
#     Extracts the reference snippet from the LLM's answer based on a "Reference Used:" marker.
#     Returns the snippet text if found, otherwise returns None.
#     """
#     match = re.search(r"Reference Used:\s*(.*)", answer_text, re.DOTALL)
#     if match:
#         # Get the first line of the reference or a trimmed version
#         snippet = match.group(1).strip().splitlines()[0]
#         return snippet
#     return None

# def generate_highlight_link(base_url, chunk_text):
#     """
#     Generates a text-fragment highlight link using a snippet from the context LLM used to generate answers.
#     """
#     sentences = re.split(r'(?<=[.!?])\s+', chunk_text)
    
#     # Choose the longest sentence if available.
#     candidate_sentence = max(sentences, key=lambda s: len(s)) if sentences else chunk_text
    
#     # Optionally trim the candidate to a maximum number of characters (e.g., 200) to avoid overly long fragments.
#     max_length = 200
#     if len(candidate_sentence) > max_length:
#         candidate_sentence = candidate_sentence[:max_length]
    
#     encoded_snippet = quote(candidate_sentence)
#     highlight_link = f"{base_url}#:~:text={encoded_snippet}"
#     return highlight_link

def main(company_name, user_question):
    txt_href = load_policy_link(company_name)
    document = load_document(txt_href)
    chunks = chunk_text(document)
    index, chunk_embeddings = build_index(chunks)
    relevant_chunks = retrieve_relevant_chunks(user_question, chunks, index, chunk_embeddings)
    answer = generate_answer(user_question, relevant_chunks)
    return answer, txt_href

    # reference_snippet = extract_reference_snippet(answer)
    # if reference_snippet:
    #     highlight_link = generate_highlight_link(txt_href, reference_snippet)
    # else:
    #     highlight_link = generate_highlight_link(txt_href, relevant_chunks[0])
    # return answer, highlight_link

if __name__ == "__main__":
    if args.question:
        user_question = args.question
    else:
        user_question = input(f"Please enter your question about {args.company_name}'s privacy policy: ")
    
    answer, txt_href = main(args.company_name, user_question)
    # answer, highlight_link = main(args.company_name, user_question)
    print("Answer:", answer)
    print("Reference URL:", txt_href)
    # print("\nHighlight Link:", highlight_link)
