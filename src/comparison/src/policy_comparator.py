import google.generativeai as genai
from .text_processor import TextProcessor
from typing import Dict, List

class PolicyComparator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-8b')
        self.text_processor = TextProcessor()

        self.aspects = [
            "Data Collection",
            "Data Sharing",
            "User Rights",
            "Cookies",
            "Third-party Data",
            "Data Retention",
            "Security Measures"
        ]

    def prepare_policy_chunks(self, policy_text: str) -> Dict:
        chunks = self.text_processor.create_chunks(policy_text)
        embeddings = self.text_processor.create_embeddings(chunks)
        return {'chunks': chunks, 'embeddings': embeddings}

    def get_relevant_sections(self, aspect: str, policy_data: Dict) -> List[Dict]:
        query = f"Find information about {aspect} in privacy policy"
        return self.text_processor.find_relevant_chunks(
            query,
            policy_data['chunks'],
            policy_data['embeddings']
        )

    def compare_policies_gemini(self, platform_a: str, platform_b: str, df):
        policy_a_text = df[df['Platform'] == platform_a]['Policy'].iloc[0]
        policy_b_text = df[df['Platform'] == platform_b]['Policy'].iloc[0]

        policy_a_data = self.prepare_policy_chunks(policy_a_text)
        policy_b_data = self.prepare_policy_chunks(policy_b_text)

        comparison_data = []
        citations_a, citations_b = {}, {}
        citation_counter_a, citation_counter_b = 1, 1

        for aspect in self.aspects:
            relevant_a = self.get_relevant_sections(aspect, policy_a_data)
            relevant_b = self.get_relevant_sections(aspect, policy_b_data)

            citations_a[f"A{citation_counter_a}"] = " ".join(chunk['chunk'] for chunk in relevant_a)
            citations_b[f"B{citation_counter_b}"] = " ".join(chunk['chunk'] for chunk in relevant_b)

            comparison_data.append({
                'aspect': aspect,
                'platform_a_text': citations_a[f"A{citation_counter_a}"],
                'platform_b_text': citations_b[f"B{citation_counter_b}"],
                'citation_a': f"[A{citation_counter_a}]",
                'citation_b': f"[B{citation_counter_b}]"
            })

            citation_counter_a += 1
            citation_counter_b += 1

        prompt = self._build_comparison_prompt(
            platform_a, platform_b, comparison_data
        )

        response = self.model.generate_content(prompt)
        return {
            'comparison': response.text,
            'citations_a': citations_a,
            'citations_b': citations_b
        }

    def _build_comparison_prompt(self, platform_a, platform_b, comparison_data):
        prompt = f"""
Compare the privacy policies of {platform_a} and {platform_b} based on the following extracted sections.
Create a detailed comparison table with citations to support each point.

Format your response exactly as follows:
| Privacy Aspect | {platform_a} | {platform_b} |
|---------------|--------------|--------------|
[Table content with citations in format [A1], [B1], etc. Citations must appear exactly once per aspect at the end of each description.]

Do NOT generate a summary line of citations at the start or end of your response.

Use these sections to create your comparison:
"""

        for data in comparison_data:
            prompt += f"\n\n{data['aspect']}:\n"
            prompt += f"{platform_a}: {data['platform_a_text']} {data['citation_a']}\n"
            prompt += f"{platform_b}: {data['platform_b_text']} {data['citation_b']}\n"

        return prompt
