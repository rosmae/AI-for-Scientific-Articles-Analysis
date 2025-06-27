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

The system consists of multiple components:

1. **Desktop Application**: Tkinter GUI application in `src/main.py`
2. **API Service**: FastAPI implementation in `src/main_api.py` 
3. **Web Frontend**: SvelteKit application for the user interface (planned)
4. **Core Modules**: Shared functionality in `src/` folder
5. **Database**: PostgreSQL for storing articles, keywords, and analysis results

The applications share core functionality while offering different interfaces.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+

### Web Application Setup

### API Service Setup

#### Using the API startup script (Recommended)
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

# Install dependencies
pip install -r requirements_api.txt

# Start the API service
python start_api.py
```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`

#### Alternative API startup
```bash
# From the src directory
cd src
uvicorn main_api:app --reload
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

### Desktop Application
```bash
# Make sure you're in the project root and venv is activated
pip install -r requirements.txt
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

The FastAPI service (`src/main_api.py`) exposes the following key endpoints:

- `GET /health` - API health check
- `POST /keywords/generate` - Extract keywords from research ideas using BERT
- `POST /search/pubmed` - Search PubMed and store articles
- `GET /articles` - Retrieve all articles
- `GET /articles/{pmid}` - Get specific article details
- `GET /search/{search_id}/scores` - Get opportunity scores for a search
- `GET /export/csv` - Export articles to CSV
- `GET /searches` - Get search history

API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Machine Learning Components

The application includes machine learning capabilities for research analysis:

### Core ML Modules
- **Clustering Analysis** (`src/clustering.py`): HDBSCAN clustering with UMAP visualization
- **Citation Forecasting** (`src/forecast.py`): ARIMA time-series modeling for citation trends  
- **Opportunity Scoring** (`src/opportunity_score.py`): Multi-factor scoring algorithm

### Text Processing
- **PubMedBERT**: Domain-specific text embeddings for medical literature
- **KeyBERT**: Automatic keyword extraction from research ideas
- **MeSH Expansion** (`src/mesh_expander.py`): Medical vocabulary enhancement

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

- **Core Application:**
  - FastAPI: Modern web framework for API services
  - Tkinter: Desktop GUI application framework
  - PostgreSQL: Database for articles and analysis storage
  - SQLAlchemy: Database ORM and operations

- **Machine Learning & NLP:**
  - PubMedBERT: Biomedical text embeddings
  - KeyBERT: Keyword extraction
  - scikit-learn: Machine learning algorithms (HDBSCAN, UMAP)
  - ARIMA: Time-series forecasting for citations
  - transformers: Hugging Face transformers library

- **External APIs:**
  - NCBI E-utilities: PubMed article retrieval
  - CrossRef API: Citation data
  - OpenAlex API: Additional citation metrics
  - MeSH API: Medical vocabulary expansion

- **Frontend (Planned):**
  - SvelteKit: Reactive UI framework
  - Chart.js: Data visualizations
  - Tailwind CSS: Utility-first styling

## Deployment

### API Service Deployment
The FastAPI service can be deployed on any Python-compatible server:

```bash
# Production startup using start_api.py
python start_api.py

# Or directly with uvicorn
cd src
uvicorn main_api:app --host 0.0.0.0 --port 8000 --workers 4
```

For production with Gunicorn:
```bash
# From project root
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main_api:app
```

### Desktop Application
The desktop application can be packaged into an executable:
```bash
# Build standalone executable (requires PyInstaller)
cd src
python -m PyInstaller --onefile main.py
```

### Database Setup
1. Install PostgreSQL
2. Create database and user
3. Configure `.env` file with credentials
4. Run `python src/database_reset.py` to initialize schema

## Troubleshooting

- **Database Connection Issues:** Verify PostgreSQL is running and credentials in `.env` are correct
- **Missing Dependencies:** Run `pip install -r requirements.txt` or `pip install -r requirements_api.txt`
- **PubMed API Issues:** Check internet connection or API rate limits
- **Import Errors:** Ensure you're in the correct directory and virtual environment is activated
- **BERT Model Download:** First run may take time to download PubMedBERT model

## 🙏 Acknowledgments

- Built using [PubMedBERT](https://huggingface.co/microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract) for biomedical text analysis
- Uses [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) for PubMed integration
- Frontend powered by [SvelteKit](https://kit.svelte.dev/)
- Data visualization with [Chart.js](https://www.chartjs.org/)
- Styling with [Tailwind CSS](https://tailwindcss.com/)
