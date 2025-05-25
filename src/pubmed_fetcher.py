from Bio import Entrez
from Bio import Medline
import requests
import time
import re

# Set your email (required by NCBI)
Entrez.email = "maia.marin94@e-uvt.ro"

def search_pubmed(query, max_results=10, start_date=None, end_date=None):
    """Search PubMed for the query and return a list of PMIDs"""
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