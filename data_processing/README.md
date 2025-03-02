# Data Processing

### Data Source
**Primary Data Source**: We utilize the privacy policies stored in Berkman Klein Center's [Transparency Hub](https://transparencydb.dev.berkmancenter.org/) as our main data source. The Hub currently stores privacy policies data for 44 social media companies.

**Data Source for T&C summarization**: We will use the [EE21/ToS-Summaries](https://huggingface.co/datasets/EE21/ToS-Summaries?row=8) dataset on HuggingFace to help with T&C summarization.

**Data Source for Jargon Explanation**: We will use [PLACEHOLDER] as our complementary data source to help with jargon explanation.

**Data Source for User-Side Data Control**: We will use [PLACEHOLDER] as our complementary data source to help with tutorials on how users can change settings for the data types that the platforms are currenly collecting.

### Overview
We will process the privacy policies for the following features:
1. Concise summary of T&C
2. Especially sensitive parts of T&C (e.g. copyright, ownership, address, location, browsing history, data will be used to train models)
3. Q&A pairs
4. Collected data: 
    - 1) User data types collected by the platform 
    - 2) Usage Policy of collected user data types
    - 3) Whether the collected data types linked to individual vs not
5. Jargons in T&C
