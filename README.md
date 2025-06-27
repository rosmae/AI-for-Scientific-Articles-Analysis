# AI for Scientific Articles Analysis

A comprehensive platform for analyzing scientific research opportunities in medical literature using artificial intelligence with an interactive web interface.

![Model Predictions](src/model/predictions_vs_actual.png)

## 🌟 Features

### Intelligent Analysis
- **PubMed Integration** for searching relevant scientific articles
- **AI-powered Keyword Generation** from research ideas
- **MeSH Term Expansion** using medical vocabulary
- **Citation Analysis** with historical data visualization
- **Machine Learning Predictions** for research opportunity scores
- **Research Clustering** using HDBSCAN and UMAP dimensionality reduction
- **Trend Forecasting** with ARIMA time-series modeling

### Interactive Web Interface
- **Real-time Data Visualization** of research clusters and opportunities
- **Responsive Dashboard** for research analytics
- **Interactive Query Builder** for PubMed searches
- **Article Management** interface
- **CSV Export** for further analysis in external tools
- **Score Visualization** with interactive charts

### Research Opportunity Analysis
- **Novelty Scoring** using semantic similarity
- **Citation Velocity Analysis** for impact assessment
- **Recency Evaluation** for timeliness of research areas
- **Overall Opportunity Scoring** for guiding research decisions
- **Visualization** of research opportunity landscape

## 🏗️ Architecture

The system consists of two main components:

1. **Desktop Application**: Original implementation in `src/` folder using Tkinter GUI
2. **Web Application**: Modern implementation with:
   - **Frontend:** SvelteKit application for the user interface
   - **Backend:** FastAPI service for handling API requests and business logic
   - **Database:** PostgreSQL for storing articles, keywords, and analysis results

Both applications share core functionality while offering different interfaces.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+

### Web Application Setup

#### Backend Setup
```bash
# Clone the repository
git clone https://github.com/rosmae/AI-for-Scientific-Articles-Analysis.git
cd AI-for-Scientific-Articles-Analysis

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Create and activate virtual environment
python -m venv venv
# For Linux/Mac:
source venv/bin/activate
# For Windows:
venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Run the FastAPI backend
cd backend
uvicorn main:app --reload
```

#### Frontend Setup
1. Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2. Install the Node.js dependencies:
    ```bash
    npm install
    ```
3. Start the development server:
    ```bash
    npm run dev
    ```

Access the web application at `http://localhost:5173`

### Desktop Application (Legacy)
```bash
# Make sure you're in the project root and venv is activated
cd src
python main.py
```

## Database Configuration

1. Create a PostgreSQL database
2. Copy `.env.example` to `.env` in the root directory
3. Fill in your database credentials in `.env`
4. The application will initialize the database schema on first run

## Usage

### Basic Workflow:
1. **Enter Research Idea:** Type your research idea in the text area
2. **Generate Keywords:** The system extracts relevant keywords automatically
3. **Search PubMed:** Adjust search parameters and execute the search
4. **View Results:** Review the articles found in the results table
5. **Analyze Opportunities:** View the opportunity score and its components
6. **Export Data:** Save your results for further analysis

### Advanced Features:
- **Cluster Visualization:** View research clusters in 2D space
- **Citation Forecasting:** Project future citation trends
- **Custom Searches:** Refine searches with specific parameters
- **Data Export:** Export findings to CSV for external analysis
- **Article Details:** Access full article metadata and metrics

## API Endpoints

The FastAPI backend exposes the following key endpoints:

- `/api/keywords/extract` - Extract keywords from research ideas
- `/api/keywords/expand` - Expand keywords with MeSH terms
- `/api/search/create` - Create a new search entry
- `/api/search/execute` - Execute search on PubMed
- `/api/articles` - Retrieve articles
- `/api/scoring/{id}` - Get opportunity scores for a search

API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Machine Learning Model

The application includes a trained machine learning model for predicting opportunity scores:

- **Model Training:** Run `python src/model/train_model.py` to train/retrain the model
- **Training Data Generation:** `python src/model/generate_training_data.py` creates training data from your database
- **Model Evaluation:** View model performance in the web interface

### Opportunity Score Prediction
- Uses RandomForestRegressor for opportunity prediction
- Features include semantic embeddings, citation metrics, and publication trends
- Trained on historical search and citation data
- Visualize model performance in prediction vs. actual charts

### Text Embedding
- PubMedBERT for domain-specific text embeddings
- KeyBERT for automatic keyword extraction
- Semantic clustering using HDBSCAN
- Dimensionality reduction with UMAP for visualization

### Citation Analysis
- ARIMA forecasting for citation trends
- Citation velocity calculation for impact assessment
- Historical citation data retrieval from CrossRef and OpenAlex

## 🛡️ Database Features
- PostgreSQL Backend: Robust storage for articles and analysis
- Full-text Search: Advanced search capabilities
- Vector Storage: Efficient storage for semantic embeddings
- Citation History: Temporal tracking of citation metrics
- Search History: Tracking of past research queries

## Requirements

- Backend:
  - Python 3.7+
  - PostgreSQL database
  - 4GB+ RAM recommended (for model inference)
  - Internet connection (for PubMed and CrossRef API)

- Frontend:
  - Node.js 14+
  - NPM or Yarn

## Technologies Used

- **Backend:**
  - FastAPI: Modern, high-performance web framework for building APIs
  - SQLAlchemy: SQL toolkit and ORM
  - PubMedBERT, KeyBERT: NLP models for medical text analysis
  - scikit-learn, PyTorch: Machine learning frameworks
  - NCBI E-utilities (PubMed), CrossRef: External APIs

- **Frontend:**
  - Svelte: Reactive UI framework
  - Chart.js: Interactive data visualizations
  - Axios: HTTP client for API requests
  - Svelte-routing: Client-side routing
  - Tailwind CSS: Utility-first CSS framework

## Deployment

### Backend Deployment
The backend can be deployed on any server that supports Python:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

For production, consider using Gunicorn as a process manager:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
```

### Frontend Deployment
Build the frontend for production:
```bash
cd frontend
npm run build
```

The contents of the `frontend/public` directory can then be served by any static file server like Nginx, Apache, or Netlify.

## Troubleshooting

- **Database Connection Issues:** Verify PostgreSQL is running and credentials are correct
- **Missing Libraries:** Ensure all dependencies are installed
- **PubMed API Issues:** Check internet connection or try again later (API rate limits)
- **CORS Issues:** Make sure the backend allows requests from your frontend origin

## 🙏 Acknowledgments

- Built using [PubMedBERT](https://huggingface.co/microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract) for biomedical text analysis
- Uses [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) for PubMed integration
- Frontend powered by [SvelteKit](https://kit.svelte.dev/)
- Data visualization with [Chart.js](https://www.chartjs.org/)
- Styling with [Tailwind CSS](https://tailwindcss.com/)
