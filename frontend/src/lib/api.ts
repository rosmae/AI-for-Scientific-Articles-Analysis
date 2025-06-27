import axios from 'axios';

// Base API URL - will proxy through Vite to localhost:8000
const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout - please try again');
    }
    if (error.response) {
      throw new Error(error.response.data?.detail || error.response.data?.message || `API Error: ${error.response.status}`);
    }
    if (error.request) {
      throw new Error('Cannot connect to API server - make sure it\'s running on localhost:8000');
    }
    throw error;
  }
);

// API Types based on your FastAPI backend
export interface KeywordGenerationRequest {
  idea: string;
}

export interface KeywordGenerationResponse {
  keywords: string[];
  expanded_keywords: string[];
}

export interface SearchRequest {
  keywords: string;
  max_results?: number;
  start_date?: string;
  end_date?: string;
}

export interface SearchResponse {
  search_id: number;
  articles_found: number;
  message: string;
}

export interface Article {
  pmid: string;
  title: string;
  abstract: string;
  journal: string;
  pub_date: string;
  authors: string[];
  doi?: string;
}

// API Functions
export const apiClient = {
  // Health check
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  },

  // Generate keywords from research idea
  async generateKeywords(idea: string): Promise<KeywordGenerationResponse> {
    const response = await api.post('/keywords/generate', { idea });
    return response.data;
  },

  // Search PubMed - Enhanced implementation
  async searchPubmed(request: SearchRequest): Promise<SearchResponse> {
    if (!request.keywords?.trim()) {
      throw new Error('Keywords cannot be empty');
    }

    console.log('Searching PubMed with request:', request);
    const response = await api.post('/search/pubmed', {
      keywords: request.keywords.trim(),
      max_results: request.max_results || 10,
      start_date: request.start_date || null,
      end_date: request.end_date || null
    });
    
    console.log('PubMed search completed:', response.data);
    return response.data;
  },

  // Get all articles - Enhanced implementation
  async getArticles(): Promise<Article[]> {
    console.log('Fetching all articles...');
    const response = await api.get('/articles');
    
    const articles = response.data || [];
    console.log(`Retrieved ${articles.length} articles`);
    
    // Ensure each article has required fields
    return articles.map((article: any) => ({
      pmid: article.pmid || '',
      title: article.title || 'No title available',
      abstract: article.abstract || '',
      journal: article.journal || 'Unknown journal',
      pub_date: article.pub_date || '',
      authors: Array.isArray(article.authors) ? article.authors : [],
      doi: article.doi || undefined
    }));
  },

  // Get article by PMID
  async getArticle(pmid: string): Promise<Article> {
    const response = await api.get(`/articles/${pmid}`);
    return response.data;
  },

  // Get search history
  async getSearchHistory(): Promise<any[]> {
    console.log('Fetching search history...');
    const response = await api.get('/searches');
    return response.data || [];
  },

  // Get opportunity scores for a search
  async getOpportunityScores(searchId: number): Promise<any> {
    console.log(`Fetching opportunity scores for search ${searchId}...`);
    const response = await api.get(`/search/${searchId}/scores`);
    return response.data;
  },

  // Export articles to CSV
  async exportToCSV(): Promise<Blob> {
    console.log('Exporting articles to CSV...');
    const response = await api.get('/export/csv', {
      responseType: 'blob'
    });
    return response.data;
  }
};
