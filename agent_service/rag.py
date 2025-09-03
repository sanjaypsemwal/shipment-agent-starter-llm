import json, argparse
from pathlib import Path
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from scipy.sparse import spdiags
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
INDEX_DIR = Path(__file__).resolve().parents[0] / "_index"; INDEX_DIR.mkdir(exist_ok=True)
DOCS_PATHS=[DATA_DIR / "docs" / "policies.md", DATA_DIR / "docs" / "carriers.md", DATA_DIR / "docs" / "faq.md"]
class SimpleRAG:
    def __init__(self): self.docs=[]; self.vectorizer=TfidfVectorizer(stop_words="english"); self.matrix=None
    def load_docs(self):
        self.docs=[]; 
        for i,p in enumerate(DOCS_PATHS):
            text=p.read_text(encoding="utf-8"); title=p.stem.title(); self.docs.append({"doc_id":i,"title":title,"text":text})
    def build(self):
        self.load_docs(); corpus=[d["text"] for d in self.docs]; self.matrix=self.vectorizer.fit_transform(corpus)
        (INDEX_DIR / "tfidf.json").write_text(json.dumps({"vocab":self.vectorizer.vocabulary_,"idf_diag":self.vectorizer.idf_.tolist(),"docs":self.docs}), encoding="utf-8")
    def load(self):
        idx=INDEX_DIR / "tfidf.json"
        if not idx.exists(): self.build()
        data=json.loads(idx.read_text(encoding="utf-8")); self.docs=data["docs"]; self.vectorizer.vocabulary_=data["vocab"]
        self.vectorizer.idf_=np.array(data["idf_diag"]); self.vectorizer._tfidf._idf_diag=spdiags(self.vectorizer.idf_,0,len(self.vectorizer.idf_),len(self.vectorizer.idf_))
        self.matrix=self.vectorizer.transform([d["text"] for d in self.docs])
    def search(self, query:str, k:int=3)->List[Dict]:
        if self.matrix is None: self.load()
        q=self.vectorizer.transform([query]); sims=cosine_similarity(q,self.matrix)[0]
        top=sorted(enumerate(sims), key=lambda x:x[1], reverse=True)[:k]; out=[]
        for idx,score in top:
            d=self.docs[idx]; line=d["text"].split("\n")[0][:200]
            out.append({"title":d["title"],"score":float(score),"quote":line})
        return out
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--rebuild-index", action="store_true"); args=ap.parse_args()
    rag=SimpleRAG(); 
    (rag.build() if args.rebuild_index else rag.load())
    print("Index rebuilt." if args.rebuild_index else "Index loaded.")
