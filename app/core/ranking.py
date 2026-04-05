def rank_documents(documents, searchable_texts: dict, query: str) -> list:
    # for each document, count how many times query appears in its searchable_text
    # sort by that count highest first
    # return sorted list
    
    scored = []
    for doc in documents:
        text = searchable_texts.get(doc.id, "")
        score = text.count(query)
        scored.append((score, doc))
    
    # sort by score highest first
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # return just the documents without scores
    return [doc for score, doc in scored]


# 1. Loop over documents
# 2. For each document get its searchable_text from the dict
# 3. Count how many times the query appears
# 4. Store (score, document) as a pair
# 5. Sort all pairs by score, highest first
# 6. Strip the scores out and return just the documents