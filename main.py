# OLD
# from pubmed_fetcher import search_pubmed, fetch_summaries

# if __name__ == "__main__":
#     query = "cancer"
#     ids = search_pubmed(query)
#     print("PubMed IDs:", ids)
#     summaries = fetch_summaries(ids)
#     for article in summaries:
#         print("\n--- Article ---")
#         print("PMID:", article["PMID"])
#         print("Title:", article["Title"])
#         print("Abstract:", article["Abstract"])
#         print("DOI:", article["DOI"])
#         print("Authors:", ", ".join(article["Authors"]))