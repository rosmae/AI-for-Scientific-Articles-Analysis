from keybert import KeyBERT

kw_model = KeyBERT()
doc = "Acute appendicitis is a common surgical emergency requiring immediate intervention."
keywords = kw_model.extract_keywords(doc)

print("Extracted keywords:", keywords)
