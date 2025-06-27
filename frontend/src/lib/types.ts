// Application Types
export interface Article {
  pmid: string;
  title: string;
  abstract: string;
  journal: string;
  pub_date: string;
  authors: string[];
  doi?: string;
  citation_count?: number;
}

export interface SearchResult {
  search_id: number;
  idea_text: string;
  keyword_text: string;
  max_results: number;
  timestamp: string;
  articles_found: number;
}

export interface OpportunityScore {
  search_id: number;
  novelty_score: number;
  citation_velocity_score: number;
  recency_score: number;
  overall_score: number;
  computed_at: string;
}

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

export interface DatabaseStatus {
  connected: boolean;
  message: string;
}

// UI State Types
export interface AppState {
  isLoading: boolean;
  error: string | null;
  currentSearch: SearchResult | null;
  articles: Article[];
  searches: SearchResult[];
}
