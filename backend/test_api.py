#!/usr/bin/env python
"""
Test script for the backend API
"""
import requests
import json
import time
from typing import List, Dict, Any, Optional

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(response.json())
    print()

def test_keyword_extraction():
    """Test keyword extraction endpoint"""
    data = {
        "text": "machine learning applications in cancer diagnosis and treatment using image processing techniques"
    }
    response = requests.post(f"{BASE_URL}/api/v1/keywords/extract", json=data)
    print(f"Keyword extraction: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()
    return response.json().get("keywords", [])

def test_mesh_expansion():
    """Test MeSH term expansion endpoint"""
    term = "cancer"
    response = requests.post(f"{BASE_URL}/api/v1/keywords/expand?term={term}")
    print(f"MeSH expansion for '{term}': {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_pubmed_search(keywords: List[str]) -> Optional[int]:
    """Test PubMed search endpoint"""
    data = {
        "keywords": "; ".join(keywords[:3]) if keywords else "cancer",  # Use first 3 keywords or default
        "idea_text": "machine learning applications in cancer diagnosis",
        "max_results": 5,
        "start_date": "2020-01-01",
        "end_date": "2023-12-31"
    }
    response = requests.post(f"{BASE_URL}/api/v1/search/pubmed", json=data)
    print(f"PubMed search: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
        print()
        return response.json().get("search_id")
    else:
        print(f"Error: {response.text}")
        print()
        return None

def test_get_articles() -> Optional[str]:
    """Test get articles endpoint"""
    response = requests.get(f"{BASE_URL}/api/v1/articles/")
    print(f"Get articles: {response.status_code}")
    if response.status_code == 200:
        articles = response.json()
        print(f"Found {len(articles)} articles")
        if articles and len(articles) > 0:
            print(f"First article: {articles[0].get('title', 'No title')}")
            return articles[0].get('pmid')
    else:
        print(f"Error: {response.text}")
    print()
    return None

def test_get_article_detail(pmid: Optional[str]) -> None:
    """Test get article detail endpoint"""
    if not pmid:
        print("Skipping article detail test - no PMID available")
        return
    
    response = requests.get(f"{BASE_URL}/api/v1/articles/{pmid}")
    print(f"Get article detail for {pmid}: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    print()

def test_get_opportunity_score(search_id: Optional[int]) -> None:
    """Test get opportunity score endpoint"""
    if not search_id:
        print("Skipping opportunity score test - no search ID available")
        return
    
    # Wait a bit for background processing
    print("Waiting for opportunity score calculation...")
    time.sleep(5)
    
    response = requests.get(f"{BASE_URL}/api/v1/scoring/{search_id}")
    print(f"Get opportunity score for search {search_id}: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    print()

def main():
    """Run all tests"""
    print("Testing Prime Time Medical Research Opportunities API\n")
    
    test_health()
    keywords = test_keyword_extraction()
    test_mesh_expansion()
    search_id = test_pubmed_search(keywords)
    pmid = test_get_articles()
    test_get_article_detail(pmid)
    test_get_opportunity_score(search_id)
    
    print("All tests completed!")

if __name__ == "__main__":
    main()
