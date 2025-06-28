# Prime Time Medical Research - AI-Powered Research Opportunity Analysis

A comprehensive platform for analyzing scientific research opportunities in medical literature using artificial intelligence with a modern, interactive web interface.

![Prime Time Medical Research](frontend/static/icon.ico)

## 🌟 Features

### 🔬 Intelligent Research Analysis
- **PubMed Integration** for searching relevant scientific articles with MeSH expansion
- **AI-Powered Keyword Generation** using PubMedBERT and KeyBERT models
- **Semantic Analysis** with transformer-based embeddings
- **Citation Analysis** with velocity and impact scoring
- **Research Clustering** using HDBSCAN and UMAP dimensionality reduction
- **Trend Forecasting** with ARIMA time-series modeling
- **Opportunity Scoring** combining novelty, citation velocity, and recency metrics

### 🎨 Modern Web Interface
- **SvelteKit Frontend** with TypeScript and Tailwind CSS
- **Real-time Search** with instant feedback and notifications
- **Interactive Date Pickers** with quick preset ranges
- **Confetti Celebrations** 🎉 for successful article ingestion
- **Comprehensive Pagination** for browsing all articles and searches
- **Responsive Design** optimized for desktop and mobile
- **Dark/Light Theme Support** with modern UI components

### 📊 Advanced Analytics Dashboard
- **Research Opportunity Analysis** with detailed scoring metrics
- **Search History Management** with filtering and pagination
- **Article Database** with full-text search and sorting
- **Export Functionality** for CSV data analysis
- **Individual Article Views** with detailed metadata
- **Background Processing** for clustering and forecasting

### 🎯 User Experience Enhancements
- **Toast Notifications** for all user actions
- **Loading States** with progress indicators
- **Error Handling** with user-friendly messages
- **Keyboard Shortcuts** for efficient navigation
- **Auto-save** search history and preferences

## 🏗️ Architecture

### Modern Full-Stack Application
1. **FastAPI Backend** (`src/main_api.py`) - High-performance Python API with automatic documentation
2. **SvelteKit Frontend** (`frontend/`) - Modern web application with TypeScript
3. **PostgreSQL Database** - Robust data storage with semantic vectors
4. **ML Pipeline** - Background processing for analysis and scoring
5. **API Documentation** - Interactive Swagger/OpenAPI documentation

### Key Technologies
- **Backend**: FastAPI, PostgreSQL, Transformers, KeyBERT, HDBSCAN, UMAP
- **Frontend**: SvelteKit, TypeScript, Tailwind CSS, Canvas Confetti
- **ML/AI**: PubMedBERT, scikit-learn, numpy, pandas
- **Database**: PostgreSQL with vector storage for embeddings

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 13+

### 🌐 Full-Stack Application Setup

#### 1. Backend API Setup
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

# Install Python dependencies
pip install -r requirements_api.txt

# Initialize database (first time only)
python src/database_reset.py

# Start the API service
python start_api.py
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`

#### 2. Frontend Web Application Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The web application will be available at `http://localhost:5173`

#### 3. Alternative API Startup
```bash
# From the src directory
cd src
uvicorn main_api:app --reload --host 0.0.0.0 --port 8000
```

### 🎯 Application Usage

#### Research Workflow
1. **Open** the web application at `http://localhost:5173`
2. **Enter** your research idea in the search form
3. **Generate** AI-powered keywords using PubMedBERT
4. **Select** date range using the interactive calendar
5. **Search** PubMed and enjoy the confetti celebration! 🎉
6. **Browse** all articles with pagination and search
7. **Analyze** opportunities on the Analysis page
8. **Export** results to CSV for further analysis

## 📱 Web Application Features

### 🏠 Dashboard
- **Research Search Form** with AI keyword generation
- **Interactive Date Picker** with preset ranges (1 year, 2 years, 5 years, 10 years, all time)
- **Real-time Notifications** with toast messages
- **Search History** with quick access to previous searches

### 📚 Articles Page
- **Comprehensive Article Table** with pagination (5, 10, 20, 50 items per page)
- **Advanced Search & Filter** across title, abstract, journal, authors, PMID
- **Sortable Columns** (title, journal, publication date)
- **Article Actions**: View details, open DOI, view on PubMed
- **Jump to Page** functionality for quick navigation
- **CSV Export** for all articles

### 📊 Analysis Page
- **Search Selection** with enhanced pagination (6, 12, 24, 48 searches per page)
- **Search Filtering** by research idea, keywords, or search ID
- **Opportunity Scoring** with detailed metrics:
  - Novelty Score (semantic uniqueness)
  - Citation Velocity Score (impact growth)
  - Recency Score (timeliness)
  - Overall Opportunity Score (combined metric)
- **Background Analysis** including clustering and forecasting

### 🎨 UI/UX Enhancements
- **Confetti Celebrations** 🎉 when articles are successfully ingested
- **Loading States** with spinners and progress indicators
- **Error Handling** with user-friendly messages
- **Responsive Design** for mobile and desktop
- **Modern Icons** and visual feedback
- **Smooth Animations** and transitions

## 🗄️ Database Configuration

1. **Install PostgreSQL** 13+ on your system
2. **Create a database** for the application
3. **Copy** `.env.example` to `.env` in the root directory
4. **Configure** your database credentials in `.env`:
   ```env
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   DATABASE_NAME=prime_time_db
   DATABASE_USERNAME=your_username
   DATABASE_PASSWORD=your_password
   ```
5. **Initialize** the database schema:
   ```bash
   python src/database_reset.py
   ```

The application will automatically create all required tables and indexes.

## 🔧 API Documentation

The FastAPI backend (`src/main_api.py`) provides a comprehensive REST API with automatic documentation:

### 🔗 Key Endpoints

#### Research & Search
- `POST /keywords/generate` - Generate keywords from research ideas using PubMedBERT
- `POST /search/pubmed` - Search PubMed with date filters and store articles
- `GET /searches` - Get paginated search history

#### Articles & Data  
- `GET /articles` - Retrieve all articles with pagination support
- `GET /articles/{pmid}` - Get detailed article information
- `GET /export/csv` - Export articles to CSV format

#### Analysis & Scoring
- `GET /search/{search_id}/scores` - Get opportunity scores for a specific search
- Background processing for clustering, forecasting, and opportunity scoring

#### System
- `GET /health` - API health check and status
- `GET /database/status` - Database connection status
- `POST /database/initialize` - Initialize database schema

### 📚 Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

All endpoints include comprehensive request/response schemas, examples, and validation.

## 🤖 Machine Learning & AI Components

### 🧠 Core ML Pipeline
- **PubMedBERT Embeddings**: Domain-specific transformer model for medical literature analysis
- **KeyBERT Extraction**: Automatic keyword generation from research ideas with MMR algorithm
- **Semantic Similarity**: Cosine similarity for research novelty assessment
- **HDBSCAN Clustering**: Density-based clustering for article grouping
- **UMAP Dimensionality Reduction**: 2D visualization of research landscapes

### 📈 Analysis Modules
- **Clustering Pipeline** (`src/clustering.py`): Advanced clustering with parameter optimization
- **Forecasting Pipeline** (`src/forecast.py`): ARIMA time-series modeling for citation prediction
- **Opportunity Scoring** (`src/opportunity_score.py`): Multi-factor scoring combining:
  - **Novelty Score**: Semantic uniqueness vs existing research
  - **Citation Velocity**: Impact growth rate analysis
  - **Recency Score**: Timeliness evaluation
  - **Overall Score**: Weighted combination for research opportunity ranking

### 🔍 Text Processing
- **MeSH Term Expansion** (`src/mesh_expander.py`): Medical vocabulary enhancement
- **Semantic Vector Storage**: Efficient embedding storage and retrieval
- **Background Processing**: Asynchronous analysis pipeline

## �️ Database Architecture

### PostgreSQL Features
- **Article Storage**: Complete metadata with abstracts and citations
- **Vector Storage**: Semantic embeddings for similarity search
- **Search History**: Temporal tracking of research queries
- **Author Management**: Normalized author data with relationships
- **Citation Tracking**: Historical citation metrics and trends

### Database Schema
- `articles`: Core article metadata and content
- `authors`: Author information with deduplication
- `searches`: Search history and parameters
- `opportunity_scores`: ML-generated research opportunity metrics
- `article_vectors`: Semantic embeddings for articles

## 💻 System Requirements

### Backend Requirements
- **Python**: 3.9+ (recommended 3.11+)
- **Memory**: 8GB+ RAM (4GB minimum for model inference)
- **Storage**: 2GB+ for models and data
- **Database**: PostgreSQL 13+
- **Network**: Internet connection for PubMed and model downloads

### Frontend Requirements
- **Node.js**: 18+ (recommended LTS)
- **Memory**: 2GB+ RAM for development
- **Browser**: Modern browser with ES2020 support

## 🛠️ Technology Stack
  - FastAPI: Modern web framework for API services
  - Tkinter: Desktop GUI application framework
### Backend Stack
- **FastAPI**: High-performance Python web framework with automatic API documentation
- **PostgreSQL**: Robust relational database with vector storage capabilities
- **Pydantic**: Data validation and settings management using Python type annotations
- **Uvicorn**: Lightning-fast ASGI server for production deployment

### Frontend Stack
- **SvelteKit**: Modern full-stack web framework with TypeScript support
- **TypeScript**: Type-safe JavaScript for better development experience
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Canvas Confetti**: Celebration animations for user engagement
- **Vite**: Next-generation frontend build tool with HMR

### Machine Learning & AI
- **PubMedBERT**: Microsoft's biomedical language model for domain-specific embeddings
- **KeyBERT**: BERT-based keyword extraction with MMR (Maximal Marginal Relevance)
- **Transformers**: Hugging Face library for transformer models
- **scikit-learn**: Machine learning algorithms (HDBSCAN, UMAP, clustering)
- **ARIMA**: Time-series forecasting for citation trend prediction

### External APIs & Data Sources
- **NCBI E-utilities**: PubMed article retrieval and search
- **MeSH API**: Medical Subject Headings vocabulary expansion
- **CrossRef API**: Citation data and DOI resolution
- **OpenAlex**: Academic research metrics and citations

## 🚀 Deployment

### 🌐 Production API Deployment
```bash
# Production startup with optimized settings
python start_api.py

# Or with uvicorn directly
cd src
uvicorn main_api:app --host 0.0.0.0 --port 8000 --workers 4

# With Gunicorn for high-performance production
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main_api:app --bind 0.0.0.0:8000
```

### 🎨 Frontend Production Build
```bash
cd frontend
npm run build
npm run preview  # Preview production build
# Or deploy the 'build' directory to your web server
```

### 🗄️ Database Production Setup
```bash
# Initialize production database
python src/database_reset.py

# Optional: Import sample data
python src/db_manager.py --import-sample-data
```

## 📊 Performance & Scalability

- **Concurrent Processing**: Background task processing for ML analysis
- **Database Indexing**: Optimized queries with proper indexing
- **API Rate Limiting**: Configurable rate limits for external API calls
- **Caching**: Intelligent caching for frequently accessed data
- **Vector Storage**: Efficient semantic similarity search

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Microsoft** for PubMedBERT model
- **NCBI** for PubMed API access
- **Hugging Face** for transformer infrastructure
- **SvelteKit** community for excellent documentation
- **FastAPI** team for the amazing framework

### 🎓 Academic Supervision & Guidance

Special thanks to our distinguished academic mentors:

- **Octavian Andronic** - Project Coordinator
  - **Medical Resident in General Surgery, University Assistant**
  - **Coordinator, Big Data Analysis Hub** – Center for Innovation and e-Health, UMFCD
  - For his expertise in medical data analysis and scientific publishing standards

- **Lector Dr. Sebastian Stefaniga** - Course Coordinator
  - For providing invaluable guidance and coordination throughout this project development

Their academic leadership and deep understanding of medical research methodologies have been instrumental in shaping this AI-powered research analysis platform to meet the real-world needs of medical researchers and practitioners.

---

**Prime Time Medical Research** - Discover research opportunities with AI-powered analysis! 🔬✨

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


