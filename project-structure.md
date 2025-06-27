# Project Structure
├── frontend/          # SvelteKit web application
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/    # UI components
│   │   │   │   ├── ArticleTable.svelte
│   │   │   │   ├── ClusterViz.svelte
│   │   │   │   ├── Footer.svelte
│   │   │   │   ├── Header.svelte
│   │   │   │   ├── KeywordPanel.svelte
│   │   │   │   ├── OpportunityScore.svelte
│   │   │   │   ├── SearchForm.svelte
│   │   │   │   └── TrendChart.svelte
│   │   │   ├── api.ts         # API client
│   │   │   ├── stores.ts      # Svelte stores
│   │   │   └── types.ts       # TypeScript definitions
│   │   ├── routes/            # SvelteKit routes
│   │   │   ├── +page.svelte   # Home/dashboard
│   │   │   ├── articles/+page.svelte
│   │   │   ├── analysis/+page.svelte
│   │   │   └── settings/+page.svelte
│   │   ├── app.css            # Global styles (Tailwind)
│   │   ├── app.html           # HTML template
│   │   └── main.js            # Entry point
│   ├── static/                # Static assets
│   ├── package.json           # Node.js dependencies
│   ├── svelte.config.js       # Svelte configuration
│   ├── tailwind.config.js     # Tailwind CSS configuration
│   └── vite.config.js         # Vite configuration
│
├── backend/                   # FastAPI web backend
│   ├── app/                   # Application code 
│   │   ├── api/               # API endpoints
│   │   │   ├── routers/       # Route handlers
│   │   │   │   ├── articles.py
│   │   │   │   ├── keywords.py
│   │   │   │   ├── scoring.py
│   │   │   │   └── search.py
│   │   ├── core/              # Core functionality 
│   │   │   ├── config.py      # Application configuration
│   │   │   ├── ml.py          # ML model initialization
│   │   │   └── utils.py       # Helper functions
│   │   ├── db/                # Database models and operations 
│   │   │   ├── database.py    # Database connection
│   │   │   ├── models.py      # SQLAlchemy models
│   │   │   └── operations.py  # Database operations
│   │   ├── ml/                # Machine learning models 
│   │   │   ├── train_model.py # Model training script
│   │   │   ├── clustering.py  # Research clustering logic
│   │   │   └── forecast.py    # Citation trend forecasting
│   │   └── services/          # Business logic services
│   │       ├── keyword_service.py  # Keyword extraction
│   │       ├── mesh_service.py     # MeSH term expansion
│   │       ├── pubmed_service.py   # PubMed API integration
│   │       └── scoring_service.py  # Opportunity scoring
│   ├── main.py                # FastAPI entry point
│   └── requirements.txt       # Python dependencies
│
├── src/                       # Original desktop application (preserved)
│   ├── model/                 # Machine learning models
│   │   ├── train_model.py     # Model training script
│   │   ├── generate_training_data.py  # Training data preparation
│   │   └── trained_model.joblib  # Saved model file
│   ├── clustering.py          # Research clustering algorithms
│   ├── db_manager.py          # Database operations
│   ├── forecast.py            # Citation forecasting
│   ├── init_db.sql            # Database schema
│   ├── main.py                # Desktop app entry point
│   ├── mesh_expander.py       # MeSH vocabulary expansion
│   ├── opportunity_score.py   # Score calculation algorithms
│   ├── pubmed_fetcher.py      # PubMed API integration
│   └── database_reset.py      # Database reset utility
│
├── .env.example               # Example environment variables
├── .gitattributes             # Git attributes configuration
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation


