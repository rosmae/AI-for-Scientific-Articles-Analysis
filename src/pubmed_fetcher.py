from Bio import Entrez
from Bio import Medline
import requests
import time
import re

# Set your email (required by NCBI)
Entrez.email = "maia.marin94@e-uvt.ro"

def search_pubmed(query, max_results=10):
    """Search PubMed for the query and return a list of PMIDs"""
    try:
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        return record["IdList"]
    except Exception as e:
        print(f"Error searching PubMed: {e}")
        return []

def fetch_summaries(id_list):
    """Fetch article summaries from PubMed for a list of PMIDs"""
    if not id_list:
        return []
        
    try:
        ids = ",".join(id_list)
        handle = Entrez.efetch(db="pubmed", id=ids, rettype="medline", retmode="text")
        records = Medline.parse(handle)
        results = []
        
        for record in records:
            # Extract DOI from LID field if available
            doi = ""
            if "LID" in record:
                doi_match = re.search(r'(10\.\d+/[^\s]+)', record.get("LID", ""))
                if doi_match:
                    doi = doi_match.group(1)
            elif "AID" in record:
                for aid in record["AID"]:
                    if "[doi]" in aid:
                        doi = aid.replace(" [doi]", "")
                        break
            
            summary = {
                "PMID": record.get("PMID", ""),
                "Title": record.get("TI", ""),
                "Abstract": record.get("AB", ""),
                "DOI": doi,
                "Journal": record.get("JT", ""),
                "PubDate": record.get("DP", ""),
                "Authors": record.get("FAU", []),
                "Affiliations": record.get("AD", [])
            }
            
            # Try to get citation count
            if doi:
                summary["CitationCount"] = get_citation_count(doi)
            else:
                summary["CitationCount"] = -1 
                
            results.append(summary)
        
        handle.close()
        return results
    except Exception as e:
        print(f"Error fetching summaries from PubMed: {e}")
        return []

def get_citation_count(doi):
    """Get citation count for a DOI using CrossRef API"""
    try:
        # Respect rate limits
        time.sleep(1)
        
        url = f"https://api.crossref.org/works/{doi}"
        headers = {"User-Agent": "PrimeTimeResearchApp/0.1 (mailto:maia.marin94@e-uvt.ro)"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data["message"].get("is-referenced-by-count", 0)
        else:
            print(f"CrossRef API error: {response.status_code}")
            return 0
    except Exception as e:
        print(f"Error getting citation count: {e}")
        return 0

def fetch_by_subfield(subfield, max_results=10):
    """Search PubMed for a specific medical subfield"""
    query = f"{subfield}[MeSH Terms]"
    ids = search_pubmed(query, max_results)
    return fetch_summaries(ids)

def calculate_subfield_metrics(articles):
    """Calculate metrics for a subfield based on articles"""
    if not articles:
        return {
            "publication_count": 0,
            "total_citations": 0,
            "avg_citations": 0,
            "opportunity_score": 0
        }
    
    publication_count = len(articles)
    total_citations = sum(article.get("CitationCount", 0) for article in articles)
    avg_citations = total_citations / publication_count if publication_count > 0 else 0
    
    # Simple opportunity score: high citations but few publications = good opportunity
    # Scale from 0-100
    if publication_count == 0:
        opportunity_score = 0
    else:
        # Higher average citations = better
        # Lower publication count = better (less saturated)
        # This is a very simple heuristic for demo purposes
        opportunity_score = min(100, (avg_citations * 10) / (publication_count ** 0.5))
    
    return {
        "publication_count": publication_count,
        "total_citations": total_citations,
        "avg_citations": round(avg_citations, 2),
        "opportunity_score": round(opportunity_score, 2)
    }