<!-- README.md -->

<h1 align="center" style="color:#4b0082;">ASML Privacy Policy Transparency Project</h1>
<p align="center"><i>In partnership with ASML Lab, Berkman Klein Center</i></p>

---

## 💜 Team Members

<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>GitHub Profile</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Yilin Qi</td>
      <td><a href="https://github.com/yilinnq">@yilinnq</a></td>
    </tr>
    <tr>
      <td>Grace Guo</td>
      <td><a href="https://github.com/gguo78">@gguo78</a></td>
    </tr>
    <tr>
      <td>Cassie Dai</td>
      <td><a href="https://github.com/cassied22">@cassied22</a></td>
    </tr>
  </tbody>
</table>

---
## 🧰 Setup

- Clone the repo
- Add an `.env` file at the root of the repository containing: `GEMINI_API_KEY=`
- Install the required dependencies:
  ```
  pip install -r requirements.txt
  ```

## 📱 Combined Application

We've created a unified Streamlit application that combines all three features into a single interface:

```bash
streamlit run app.py
```

This will launch a web application with three tabs:
1. **Policy Q&A** - Ask specific questions about a platform's privacy policy
2. **Policy Summary** - Get a structured summary of a platform's privacy policy
3. **Policy Comparison** - Compare privacy policies between two platforms

### Data Source

All features use a single data source: the `privacy_db.csv` file located in `src/summary/`. This CSV file contains links to privacy policy documents stored on Google Cloud Storage. Using a unified data source ensures consistency across all features and makes it easier to maintain the application.

<p align="center">
  <figure>
    <img src="screenshots/combined_app.png" width="800" title="Combined Privacy Policy Analysis Tool">
    <figcaption align="center"><i>Combined Privacy Policy Analysis Tool</i></figcaption>
  </figure>
</p>

---

## 🔧 Individual Functionalities

You can also use each feature separately:

### ❓ User Q&A

**Description**  
A pipeline that:

1. Loads the processed `.txt` version of the policy from the JSON file in `src/data_processing/policy_links`.
2. Loads and chunks the policy document using the HTML version of the .txt file.
3. Builds the index and retrieves relevant sections.
4. Generates the answer using the Gemini API based on a user question.
5. Outputs:
 - the answer,
 - the relevant part of the privacy policy used to generate the answer,
 - the link to the policy on Transparency Hub.

**Instructions**

```bash
cd src/qa
pipenv install
pipenv run python get_txt_policy.py --company_name="you company choice"
```

You can enter a user question directly with:
```bash
cd src/qa
pipenv install
pipenv run python get_txt_policy.py --company_name="you company choice" --question="your question here"
```
Or just run the script and it will prompt you for a question.

**Eligible Company Names**
<details> <summary>Click to view Eligible Company Names</summary>
"blackplanet", "bluesky", "bumble", "cato", "chess", "christian_mingle", "clubhouse",
"coffee_meets_bagel", "eharmony", "feeld", "friendster", "gab", "gettr",
"github", "gofundme", "goodreads", "her", "hinge", "instagram", "jodel", "kickstarter",
"likee", "linkedin", "mastodon", "medium", "meetup", "nextdoor", "okcupid", "parler",
"pinterest", "quora", "raya", "reddit", "sesearch_gate", "signal", "silver_singles",
"slack", "snapchat", "strava", "supernova", "telegram", "tellonym", "threads", "tiktok",
"tinder", "truth_social", "tumblr", "twitter_x", "vanatu", "vero", "whatsapp", "yareny", "youtube"
</details>

<p align="center">
  <figure>
    <img src="screenshots/qa_example.png" width="800" title="Example for Q&A - Tiktok">
    <figcaption align="center"><i>Example for Q&A - Tiktok</i></figcaption>
  </figure>
</p>

<p align="center">
  <figure>
    <img src="screenshots/qa_example2.png" width="800" title="Example for Q&A - Pinterest">
    <figcaption align="center"><i>Example for Q&A - Pinterest</i></figcaption>
  </figure>
</p>
