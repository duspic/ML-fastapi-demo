from sentence_transformers import SentenceTransformer

def load_model() -> SentenceTransformer:
    try:
        print("Loading local model")
        return SentenceTransformer("./model/paraphrase-MiniLM-L6-v2.h5")
    except Exception as e:
        print("No local model found. Downloading a new one")
        model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
        model.save("model/paraphrase-MiniLM-L6-v2.h5")
        return model
    
