import math
import json

docs = [
    "I am a dog",
    "This is my cat's",
    "who are you mr cat",
    "I am running",
    "i love cats"
]


maps = {
    "NN": "n",
    "NNS": "n",
    "NNP": "n",
    "NNPS": "n",
    "VB": "v",
    "VBD": "v",
    "VBG": "v",
    "VBN": "v",
    "VBP": "v",
    "VBZ": "v",
    "JJ": "a",
    "JJR": "a",
    "JJS": "a",
    "RB": "r",
    "RBR": "r",
    "RBS": "r",
    "DT": "n",
    "PRP$": "n",
    "PRP": "n"
}

## nltk.download('wordnet')
## nltk.download('punkt_tab')
## nltk.download('averaged_perceptron_tagger_eng')

from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, word_tokenize

def clean(sentence):
    return [lemmatizer.lemmatize(word.lower(), maps.get(pos, "n")) for word, pos in pos_tag(word_tokenize(sentence))]


lemmatizer = WordNetLemmatizer()
class BM25Retriever:

    def __init__(self, b=0.75, k1=1.5):
        self.b = b
        self.k1 = k1
        self.N = 0
        self.avg_dl = 0
        self.df = dict()
        self.docs = dict()
        
    
    def fit(self, docs):
        # receives a list of docs,
        # first clean them of syntactical sugar
        cleaned = [clean(d) for d in docs]
        # id = doc position
        for i, doc_words in enumerate(cleaned):
            d = len(doc_words)
            self.avg_dl += d
            self.docs[str(i)] = {"length": d, "fdt": dict()}
            for word in doc_words:
                self.docs[str(i)]["fdt"][word] = self.docs[str(i)]["fdt"].get(word, 0) + 1
                self.df[word] = self.df.get(word, 0) + 1

            self.N += 1
        
        self.avg_dl /= self.N 

        return self

    def score_term(self, doc: str, term: str):
        fdt = self.docs[doc]["fdt"].get(term,0)
        dft = self.df.get(term,0)
        # term is supposed to be a word
        idf = math.log10(1 + ((self.N - dft)/(dft+0.5)))
        tf = (fdt*(self.k1 +1))/(fdt + self.k1*(1 - self.b + self.b*(self.N/self.avg_dl)))

        return tf*idf
    
    def score_query(self, query: str):

        clean_q = clean(query)
        # for all docs get the sum over terms
        scores = []
        for i in range(self.N):
            scores.append(sum(self.score_term(str(i), term) for term in clean_q))
        
        return scores

    def save_json(self, file_path="bm25_model.json"):
        """Save the BM25 model to a JSON file."""
        data = {
            "b": self.b,
            "k1": self.k1,
            "N": self.N,
            "avg_dl": self.avg_dl,
            "df": self.df,
            "docs": self.docs,
        }
        with open(file_path, "w") as f:
            json.dump(data, f)
    
    @staticmethod
    def load_json(file_path="bm25_model.json"):
        """Load a BM25 model from a JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)
        
        obj = BM25Retriever(b=data["b"], k1=data["k1"])
        obj.N = data["N"]
        obj.avg_dl = data["avg_dl"]
        obj.df = data["df"]
        obj.docs = data["docs"]
        return obj


# bm25 = BM25Retriever()
# bm25.fit(docs)

# print(bm25.score_query("i love cats"))

# bm25.save_json()
# del bm25

loaded_bm25 = BM25Retriever.load_json()

print(loaded_bm25.score_query("i love cats"))

