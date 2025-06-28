# Prime Time Medical Research - Project Structure

A comprehensive full-stack medical research analysis platform with AI-powered opportunity scoring.

## 📁 Project Overview
```
Proiect-AI/                    # Root directory
├── 📂 frontend/               # SvelteKit web application
│   ├── 📂 src/
│   │   ├── 📂 lib/
│   │   │   ├── 📂 components/          # Reusable UI components
│   │   │   │   ├── ArticleTable.svelte    # Enhanced table with pagination, search, sort
│   │   │   │   ├── Header.svelte          # Navigation header with app icon
│   │   │   │   ├── KeywordPanel.svelte    # Generated keywords display
│   │   │   │   ├── Notification.svelte   # Toast notification system
│   │   │   │   ├── SearchForm.svelte     # Advanced search with date picker & confetti
│   │   │   │   └── SearchHistory.svelte  # Search history management
│   │   │   ├── api.ts                     # API client with error handling
│   │   │   ├── stores.ts                  # Svelte stores for state management
│   │   │   └── types.ts                   # TypeScript type definitions
│   │   ├── 📂 routes/                     # SvelteKit file-based routing
│   │   │   ├── +layout.svelte             # App layout with header & notifications
│   │   │   ├── +page.svelte               # Dashboard with search form
│   │   │   ├── 📂 articles/
│   │   │   │   ├── +page.svelte           # Articles listing with pagination
│   │   │   │   └── 📂 [pmid]/
│   │   │   │       └── +page.svelte       # Individual article details
│   │   │   └── 📂 analysis/
│   │   │       └── +page.svelte           # Analysis dashboard with opportunity scores
│   │   ├── app.css                        # Global Tailwind CSS styles
│   │   └── app.html                       # HTML template with favicon
│   ├── 📂 static/                         # Static assets
│   │   ├── favicon.ico                    # Browser favicon
│   │   └── icon.ico                       # App icon for header
│   ├── package.json                       # Node.js dependencies & scripts
│   ├── svelte.config.js                   # SvelteKit configuration
│   ├── tailwind.config.js                 # Tailwind CSS configuration
│   ├── vite.config.js                     # Vite build configuration
│   └── tsconfig.json                      # TypeScript configuration
├── 📂 src/                    # Python backend source code
│   ├── main_api.py                        # FastAPI application with comprehensive endpoints
│   ├── db_manager.py                      # Database operations & connection management
│   ├── pubmed_fetcher.py                  # PubMed API integration
│   ├── mesh_expander.py                   # MeSH term expansion for medical vocabulary
│   ├── opportunity_score.py               # ML-based opportunity scoring algorithms
│   ├── clustering.py                      # HDBSCAN clustering & UMAP visualization
│   ├── forecast.py                        # ARIMA time-series forecasting
│   ├── database_reset.py                  # Database schema initialization
│   └── init_db.sql                        # SQL schema definitions
├── 📂 nous/                   # Legacy web application
│   ├── run_backend.py
│   ├── setup_backend.py
│   └── start_backend.py
├── 📂 build/                  # Build artifacts
├── 📂 __pycache__/           # Python cache files
├── start_api.py                           # API server startup script
├── requirements_api.txt                   # Python dependencies for API
├── requirements.txt                       # General Python dependencies
├── README.md                              # Comprehensive project documentation
├── project-structure.md                   # This file - project structure overview
└── API_README.md                          # API-specific documentation
```

## 🔧 Core Components

### 🌐 Frontend (SvelteKit + TypeScript)
**Location**: `frontend/`
**Purpose**: Modern, responsive web interface for research analysis

#### Key Features:
- **Advanced Search Form** with AI keyword generation and interactive date picker
- **Confetti Celebrations** 🎉 for successful article ingestion  
- **Comprehensive Pagination** for articles and searches (5-50 items per page)
- **Real-time Search & Filter** across all data
- **Responsive Design** optimized for desktop and mobile
- **Toast Notifications** for user feedback
- **CSV Export** functionality

#### Component Architecture:
- **ArticleTable.svelte**: Enhanced table with pagination, sorting, search, and article actions
- **SearchForm.svelte**: Advanced form with date picker, quick presets, and confetti
- **Header.svelte**: Navigation with app icon and responsive menu
- **Notification.svelte**: Toast notification system with auto-dismiss
- **KeywordPanel.svelte**: AI-generated keyword display with scores

### 🔙 Backend (FastAPI + PostgreSQL)
**Location**: `src/`
**Purpose**: High-performance API with ML processing and data management

#### Core Modules:
- **main_api.py**: FastAPI application with 15+ endpoints and automatic documentation
- **db_manager.py**: Database operations with connection pooling and error handling
- **pubmed_fetcher.py**: PubMed integration with rate limiting and error recovery
- **opportunity_score.py**: Multi-factor ML scoring (novelty, citation velocity, recency)

#### ML & Analysis Pipeline:
- **clustering.py**: HDBSCAN clustering with UMAP dimensionality reduction
- **forecast.py**: ARIMA time-series forecasting for citation prediction
- **mesh_expander.py**: Medical vocabulary expansion using MeSH terms

### 🗄️ Database Schema
**Database**: PostgreSQL with vector storage
**Initialization**: `src/database_reset.py` and `src/init_db.sql`

#### Core Tables:
- **articles**: Article metadata, abstracts, DOIs, citation counts
- **authors**: Normalized author data with deduplication
- **searches**: Search history with parameters and timestamps
- **opportunity_scores**: ML-generated research opportunity metrics
- **article_vectors**: Semantic embeddings for similarity search

## 🚀 Development Workflow

### 🔄 Full Development Setup:
```bash
# 1. Backend API (Terminal 1)
python start_api.py                    # Starts on localhost:8000

# 2. Frontend Dev Server (Terminal 2)  
cd frontend && npm run dev             # Starts on localhost:5173

# 3. Database Initialization (First time)
python src/database_reset.py
```

### 📊 API Endpoints Overview:
- **Research**: `/keywords/generate`, `/search/pubmed`
- **Articles**: `/articles`, `/articles/{pmid}`, `/export/csv`
- **Analysis**: `/search/{search_id}/scores`, `/searches`
- **System**: `/health`, `/database/status`

## 🎯 User Experience Flow

1. **Dashboard** (`/`) - Enter research idea, generate keywords, select date range
2. **Search** - PubMed integration with MeSH expansion and background ML processing
3. **Confetti** 🎉 - Celebration when articles are successfully ingested
4. **Articles** (`/articles`) - Browse all articles with advanced pagination and search
5. **Analysis** (`/analysis`) - View opportunity scores and research insights
6. **Export** - Download results as CSV for further analysis

## 🤖 AI & Machine Learning Stack

### Models & Algorithms:
- **PubMedBERT**: Microsoft's biomedical language model for embeddings
- **KeyBERT**: Keyword extraction with MMR (Maximal Marginal Relevance)
- **HDBSCAN**: Density-based clustering for article grouping
- **UMAP**: Dimensionality reduction for visualization
- **ARIMA**: Time-series forecasting for citation trends

### Processing Pipeline:
1. **Keyword Generation**: Research idea → PubMedBERT → KeyBERT → Keywords
2. **Article Retrieval**: Keywords → MeSH expansion → PubMed search → Articles
3. **Background Analysis**: Articles → Clustering + Forecasting + Scoring
4. **Opportunity Scoring**: Novelty + Citation Velocity + Recency → Overall Score

## 📱 Modern Web Features

### Enhanced UI/UX:
- **Interactive Date Picker** with preset ranges (1Y, 2Y, 5Y, 10Y, All Time)
- **Confetti Animations** for successful operations
- **Real-time Pagination** with jump-to-page functionality
- **Advanced Search** across title, abstract, journal, authors, PMID
- **Responsive Design** with mobile-first approach
- **Toast Notifications** with auto-dismiss and error handling

### Technical Improvements:
- **TypeScript** for type safety and better development experience
- **Tailwind CSS** for rapid, maintainable styling
- **Vite** for fast builds and hot module replacement
- **Canvas Confetti** for celebration animations
- **Proper Error Boundaries** and loading states

## 🔧 Configuration Files

### Frontend Configuration:
- **package.json**: Dependencies, scripts, and project metadata
- **svelte.config.js**: SvelteKit framework configuration
- **vite.config.js**: Build tool configuration with proxy settings
- **tailwind.config.js**: CSS framework configuration
- **tsconfig.json**: TypeScript compiler options

### Backend Configuration:
- **requirements_api.txt**: Python dependencies for production API
- **start_api.py**: Production-ready API server startup
- **.env**: Environment variables for database and API configuration

This structure supports a scalable, maintainable application with clear separation of concerns and modern development practices.
