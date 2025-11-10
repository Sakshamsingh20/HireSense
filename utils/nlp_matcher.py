from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def match_candidates_for_job(job_description: str, candidates: list):
    """
    Returns list of matches: [{id, name, score, snippet}...]
    Uses TF-IDF + cosine similarity between job description and candidate text.
    """
    docs = [job_description] + [c.get("text","") for c in candidates]
    if len(docs) <= 1:
        return []
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    try:
        X = vectorizer.fit_transform(docs)
        job_vec = X[0:1]
        cand_vecs = X[1:]
        sims = cosine_similarity(job_vec, cand_vecs)[0]
    except Exception as e:
        # if vectorization fails, return zero scores
        sims = [0.0]*len(candidates)
    results = []
    for c, s in zip(candidates, sims):
        snippet = (c.get("text","")[:250] + "...") if c.get("text") else ""
        results.append({"id": c.get("id"), "name": c.get("name"), "score": float(s), "snippet": snippet})
    # sort by score desc
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return results
