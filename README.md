# AI for Scientific Articles Analysis

A comprehensive tool for analyzing scientific research opportunities in medical literature using artificial intelligence.

![Model Predictions](src/model/predictions_vs_actual.png)

## Overview

This application helps researchers identify promising research opportunities by:
1. Finding relevant scientific articles from PubMed
2. Analyzing citation patterns, novelty, and research trends
3. Computing opportunity scores to guide research decisions
4. Storing and managing a database of research interests and findings

## Features

- **PubMed Integration:** Search PubMed with advanced query options
- **Keyword Generation:** AI-powered extraction of relevant keywords from research ideas
- **MeSH Term Expansion:** Automatically expands search terms using MeSH vocabulary
- **Opportunity Scoring:** Calculates research opportunity scores based on:
  - **Novelty:** How unique the research area is
  - **Citation Rate:** Impact and attention in the scientific community
  - **Recency:** Timeliness and current relevance of the topic
- **Data Storage:** PostgreSQL database for storing articles and analysis results
- **Data Export:** Export results to CSV for further analysis
- **Machine Learning Model:** Trained model to predict opportunity scores

## Setup Instructions

```
git clone https://github.com/rosmae/AI-for-Scientific-Articles-Analysis.git
cd AI-for-Scientific-Articles-Analysis
python3 -m venv venv
# For Linux/Mac:
source venv/bin/activate  
# For Windows: 
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
## Database Configuration

1. Create a PostgreSQL database
2. Copy `.env.example` to `.env`
3. Fill in your database credentials in `.env`
4. Run the application, which will initialize the database schema

## Usage

### Basic Workflow:
1. **Connect to Database:** Enter your PostgreSQL credentials and click "Connect"
2. **Enter Research Idea:** Type your research idea in the text area
3. **Generate Keywords:** Click "Generate" to extract relevant keywords
4. **Search PubMed:** Adjust search parameters and click "Search PubMed"
5. **View Results:** Review the articles found in the results table
6. **Analyze Opportunities:** The opportunity score and its components are displayed at the bottom

### Advanced Features:
- **Export CSV:** Save all articles and analysis data to a CSV file
- **Article Details:** Double-click on any article to view full details
- **Custom Searches:** Edit generated keywords or add date filters

## Machine Learning Model

The application includes a trained machine learning model for predicting opportunity scores:

- **Model Training:** Run `python src/model/train_model.py` to train/retrain the model
- **Training Data Generation:** `python src/model/generate_training_data.py` creates training data from your database
- **Model Evaluation:** View model performance in `src/model/predictions_vs_actual.png`

## Requirements

- Python 3.7+
- PostgreSQL database
- 4GB+ RAM recommended (for model inference)
- Internet connection (for PubMed and CrossRef API)

## Technologies Used

- **Natural Language Processing:** PubMedBERT, KeyBERT
- **Machine Learning:** scikit-learn, PyTorch
- **APIs:** NCBI E-utilities (PubMed), CrossRef
- **Database:** PostgreSQL
- **UI:** Tkinter
- **Other Libraries:** Biopython, transformers, psycopg2

## Project Structure

- **src/**: Main source code
  - **main.py**: Main application entry point
  - **db_manager.py**: Database operations
  - **pubmed_fetcher.py**: PubMed API integration
  - **mesh_expander.py**: MeSH vocabulary expansion
  - **opportunity_score.py**: Score calculation algorithms
  - **model/**: ML model components
    - **train_model.py**: Model training script
    - **generate_training_data.py**: Training data preparation
    
## Troubleshooting

- **Database Connection Issues:** Verify PostgreSQL is running and credentials are correct
- **Missing Libraries:** Ensure all dependencies are installed via `pip install -r requirements.txt`
- **PubMed API Issues:** Check internet connection or try again later (API rate limits)
