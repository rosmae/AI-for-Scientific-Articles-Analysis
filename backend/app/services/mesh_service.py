import requests
from typing import List

def expand_with_mesh(term: str) -> List[str]:
    """
    Expand a medical term using NCBI MeSH entry terms (synonyms).
    
    This function is adapted from src/mesh_expander.py
    """
    try:
        # Step 1: Search MeSH database for the term
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "mesh",
            "term": term,
            "retmode": "json"
        }
        search_resp = requests.get(search_url, params=search_params)
        search_data = search_resp.json()

        id_list = search_data.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return [term]  # No matches found

        mesh_uid = id_list[0]

        # Step 2: Get full descriptor info from MeSH
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        summary_params = {
            "db": "mesh",
            "id": mesh_uid,
            "retmode": "json"
        }
        summary_resp = requests.get(summary_url, params=summary_params)
        summary_data = summary_resp.json()
        doc = summary_data.get("result", {}).get(mesh_uid, {})

        # Entry terms often contain synonyms
        synonyms = doc.get("ds_meshterms", []) or []
        synonyms.append(term)  # Ensure original is included
        return list(set(synonyms))  # Remove duplicates if any

    except Exception as e:
        print(f"[MeSH Expander Error] {e}")
        return [term]
