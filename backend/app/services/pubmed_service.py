from Bio import Entrez
from Bio import Medline
import requests
import time
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.config import settings

# Configure Entrez email
Entrez.email = settings.PUBMED_EMAIL

def search_pubmed(query: str, max_results: int = 10, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[str]:
    """
    Search PubMed for the query and return a list of PMIDs.
    
    This function is adapted from src/pubmed_fetcher.py
    """
    try:
        if start_date and end_date:
            query += f' AND ("{start_date}"[PDAT] : "{end_date}"[PDAT])'
        
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results, sort="relevance")
        record = Entrez.read(handle)
        handle.close()
        return record["IdList"]
    except Exception as e:
        print(f"Error searching PubMed: {e}")
        return []

def fetch_summaries(id_list: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch article summaries from PubMed for a list of PMIDs.
    
    This function is adapted from src/pubmed_fetcher.py
    """
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
            
            # Parse the publication date - handle various formats
            pub_date = record.get("DP", "")
            formatted_date = parse_pubmed_date(pub_date)
            
            pmid_value = record.get("PMID", "")
            summary = {
                "PMID": pmid_value,
                "Title": record.get("TI", ""),
                "Abstract": record.get("AB", ""),
                "DOI": doi,
                "Journal": record.get("JT", ""),
                "PubDate": formatted_date,
                "Authors": record.get("FAU", []),
                "Affiliations": record.get("AD", [])
            }

            # Try to get citation count
            if doi:
                summary["CitationCount"] = get_citation_count(doi)
            else:
                summary["CitationCount"] = 0  # Changed from -1 to 0 to avoid potential errors

            # Get citation history from OpenAlex
            citation_history = get_citation_history_openalex(pmid=pmid_value, doi=doi)
            summary["CitationHistory"] = citation_history
                
            results.append(summary)
        
        handle.close()
        return results
    except Exception as e:
        print(f"Error fetching summaries from PubMed: {e}")
        return []

def parse_pubmed_date(date_str: str) -> str:
    """Parse PubMed date string into a standard format"""
    if not date_str:
        return None
        
    try:
        # Handle various date formats
        formats = [
            "%Y %b %d",  # 2023 Jan 15
            "%Y %b",     # 2023 Jan
            "%Y"         # 2023
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
                
        # If no format matches, return just the year if possible
        if date_str.strip().isdigit() and len(date_str.strip()) == 4:
            return f"{date_str.strip()}-01-01"
            
        return None
    except Exception:
        return None

def get_citation_count(doi: str) -> int:
    """
    Get citation count for a DOI using CrossRef API.
    
    This function is copied from src/pubmed_fetcher.py
    """
    try:
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
    
def get_citation_history_openalex(pmid: Optional[str] = None, doi: Optional[str] = None) -> Dict[int, int]:
    """
    Fetch yearly citation history from OpenAlex using DOI or PMID.
    
    This function is copied from src/pubmed_fetcher.py
    """
    try:
        if doi:
            openalex_id = f"doi:{doi.lower()}"
        elif pmid:
            openalex_id = f"pmid:{pmid}"
        else:
            print("No DOI or PMID available for OpenAlex lookup.")
            return {}

        time.sleep(1)
        url = f"https://api.openalex.org/works/{openalex_id}"
        headers = {"User-Agent": "PrimeTimeResearchApp/0.1 (mailto:maia.marin94@e-uvt.ro)"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            counts_by_year = data.get("counts_by_year", [])
            history = {entry["year"]: entry["cited_by_count"] for entry in counts_by_year}
            return history
        elif response.status_code == 404:
            print(f"OpenAlex: No record found for {openalex_id}")
            return {}
        else:
            print(f"OpenAlex API error: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error fetching citation history from OpenAlex: {e}")
        return {}
