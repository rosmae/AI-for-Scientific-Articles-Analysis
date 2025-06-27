# Prime Time Medical Research - Frontend

A SvelteKit frontend for the Prime Time Medical Research Opportunities application.

## Features

- 🔍 **Research Search**: Generate keywords and search PubMed
- 📚 **Article Management**: View and browse retrieved articles  
- 🎨 **Modern UI**: Responsive design with Tailwind CSS
- 🔄 **Real-time Updates**: Live connection to FastAPI backend

## Quick Start

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

3. **Make sure the API backend is running**
   ```bash
   # In the project root
   python start_api.py
   ```

The frontend will be available at `http://localhost:5173` and will proxy API requests to `http://localhost:8000`.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## API Integration

The frontend connects to the FastAPI backend through:
- **Keyword Generation**: `POST /keywords/generate`
- **PubMed Search**: `POST /search/pubmed` 
- **Article Retrieval**: `GET /articles`
- **Health Check**: `GET /health`

## Technologies

- **SvelteKit**: Web framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Axios**: HTTP client
