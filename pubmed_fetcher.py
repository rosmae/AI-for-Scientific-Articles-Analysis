from Bio import Entrez
from Bio import Medline

Entrez.email = "maia.marin94@e-uvt.ro"

def search_pubmed(query, max_result = 1):
    handle = Entrez.esearch(db ="pubmed", term = query, retmax = max_result)
    record = Entrez.read(handle)
    handle.close()
    return record["IdList"]

def fetch_summaries(id_list):
    ids =",".join(id_list)
    handle = Entrez.efetch(db="pubmed", id = ids, rettype="medline", retmode ="text")
    records = Medline.parse(handle)
    results = []

    for record in records:
        summary = {
            "PMID": record.get("PMID", ""),
            "Title": record.get("TI", ""),
            "Abstract": record.get("AB", ""),
            "DOI": record.get("LID", ""),
            "Journal": record.get("JT", ""),
            "PubDate": record.get("DP", ""),
            "Authors": record.get("FAU", []),
            "Affiliations": record.get("AD", [])
        }
        results.append(summary)

    handle.close()
    return results

    