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
├── backend/                   # Future FastAPI web backend (placeholder)
│
├── src/                       # Core application modules
│   ├── clustering.py          # Research clustering algorithms using HDBSCAN/UMAP
│   ├── database_reset.py      # Database reset utility
│   ├── db_manager.py          # Database operations and connection management
│   ├── forecast.py            # Citation trend forecasting with ARIMA
│   ├── init_db.sql            # PostgreSQL database schema
│   ├── main.py                # Desktop Tkinter GUI application
│   ├── main_api.py            # FastAPI web service implementation
│   ├── mesh_expander.py       # MeSH vocabulary expansion
│   ├── opportunity_score.py   # Research opportunity scoring algorithms
│   ├── pubmed_fetcher.py      # PubMed API integration
│   ├── build/                 # PyInstaller build outputs
│   ├── resources/             # Application resources (icons, etc.)
│   └── __pycache__/          # Python bytecode cache
│
├── nous/                      # Backend utilities and scripts
│   ├── run_backend.py         # Backend runner script
│   ├── setup_backend.py       # Backend setup script
│   └── start_backend.py       # Backend startup script
│
├── build/                     # Application build artifacts
├── dist/                      # Distribution files
├── __pycache__/              # Python bytecode cache
│
├── start_api.py               # FastAPI startup script
├── debug_db.py                # Database debugging utility
├── API_README.md              # API documentation
├── requirements.txt           # Core Python dependencies
├── requirements_api.txt       # API-specific Python dependencies
├── .env                       # Environment variables (local)
├── .env.example               # Example environment variables
├── .gitattributes             # Git attributes configuration
├── .gitignore                 # Git ignore rules
├── project-structure.md       # This file
└── README.md                  # Project documentation


