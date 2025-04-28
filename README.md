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
- Run `./run.sh` to automatically setup virtual environment & run our app for the following three features: 
  - User Q&A
  - Privacy Policy Summary
  - Policy Comparison Across Platform

---

## 🔧 Individual Functionalities

You can also use each feature separately:

### ❓ User Q&A

**Description**
The Policy Q&A feature allows users to ask a question about a platform and get accurate answers referencing the platform's original privacy policy document.

 <p align="center">
  <figure>
    <img src="screenshots/qa_ui.png" width="800" title="Feature Interface">
    <figcaption align="center"><i>Feature Interface</i></figcaption>
  </figure>
</p>


**Key Features**  
- Loads the processed `.txt` version of the privacy policy
- Loads and chunks the policy document using the HTML version of the .txt file.
- Builds the index and retrieves relevant sections.
- Generates the answer using the Gemini API based on a user question.
- Outputs:
 - the answer,
 - the relevant part of the privacy policy used to generate the answer,
 - the link to the policy on Transparency Hub.

<p align="center">
  <figure>
    <img src="screenshots/qa_results1.png" width="800" title="Example for Q&A - Tiktok">
    <figcaption align="center"><i>Example for Q&A - Tiktok</i></figcaption>
  </figure>
</p>

<p align="center">
  <figure>
    <img src="screenshots/qa_results2.png" width="800" title="Example for Q&A - Pinterest">
    <figcaption align="center"><i>Example for Q&A - Pinterest</i></figcaption>
  </figure>
</p>

###  📊 Policy Comparison
**Description**   
The Policy Comparison feature allows users to analyze and compare privacy policies between two different platforms side by side.

<p align="center">
  <figure>
    <img src="screenshots/comp_ui.png" width="800" title="Feature Interface">
    <figcaption align="center"><i>Feature Interface</i></figcaption>
  </figure>
</p>

**Key Features**
- Side-by-side comparison of privacy policies from different platforms
- Comprehensive analysis across critical privacy aspects:
  - Data collection
  - Data sharing
  - User rights
  - Cookies
  - Third-party data
  - Data retention
  - Security measures
- Hyperlinked citations to source material for verification
- Expandable sections showing original privacy policy excerpts

<p align="center">
  <figure>
    <img src="screenshots/comp_results.png" width="800" title="Example for Privacy comparison">
    <figcaption align="center"><i>Example for Privacy comparison - X vs. Whatsapp</i></figcaption>
  </figure>
</p>

<p align="center">
  <figure>
    <img src="screenshots/comp_ref.png" width="800" title="Reference Example">
    <figcaption align="center"><i>Reference Example</i></figcaption>
  </figure>
</p>


###  📝 Policy Summary
**Description**   
The Policy Summary feature provides users with a clear, structured overview of a selected platform’s privacy policy. By choosing a platform from the list, users receive a concise summary that highlights the most critical aspects of how their data is handled. 

<p align="center">
  <figure>
    <img src="screenshots/sum_ref.png" width="800" title="Feature Interface">
    <figcaption align="center"><i>Feature Interface</i></figcaption>
  </figure>
</p>

**Key Features**
- Generates a readable, well-structured summary of the selected platform’s privacy policy
- Summary covers essential aspects of data practices, including:
  - Types of data collected
  - Purpose of data collection
  - Data sharing and disclosure:
  - User rights and choices:
  - Data storage and security:
  - Use of cookies and tracking technologies:
  - Other important information (such as children’s privacy, changes to the policy etc.):

- Expandable sections showing original privacy policy excerpts as well as the link to the full privacy policy page from the original platform for further reading

<p align="center">
  <figure>
    <img src="screenshots/sum_ex1.png" width="800" title="Example for Privacy summary">
    <figcaption align="center"><i>Example for Privacy Summary - chess.com</i></figcaption>
  </figure>
</p>

<p align="center">
  <figure>
    <img src="screenshots/sum_ex2.png" width="800" title="Reference Example">
    <figcaption align="center"><i>Reference of Summary Example</i></figcaption>
  </figure>
</p>
