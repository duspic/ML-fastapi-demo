from fastapi import FastAPI, Query
import pandas as pd
import numpy as np
from sentence_transformers import util

from app import utils, pydantic_models


MODEL = utils.load_model()

JOBS_DF = pd.read_csv("data/scraped_linkedin_jobs.csv")
DESCRIPTION_EMBEDDINGS = np.load("data/description_embeddings.npy")
LOCATION_EMBEDDINGS = np.load("data/location_embeddings.npy")
ORG_EMBEDDINGS = np.load("data/org_embeddings.npy")
TITLE_EMBEDDINGS = np.load("data/title_embeddings.npy")


TITLE_WEIGHT = 0.5
LOCATION_WEIGHT = 0.5
ORG_WEIGHT = 0.2
DESCRIPTION_WEIGHT = 0.3

app = FastAPI()

@app.get("/")
def root():
    return {"The service is working! Use the /search GET endpoint for model inference"}

@app.get("/search")
def search(query: str = Query(min_length=3), no_of_results: int = 5) -> pydantic_models.JobSchemaList:
    query_embeddings = MODEL.encode(query, convert_to_tensor=True)

    # Compute similarities per embedding
    sim_title = util.cos_sim(query_embeddings.cpu(), TITLE_EMBEDDINGS,)[0]
    sim_location = util.cos_sim(query_embeddings.cpu(), LOCATION_EMBEDDINGS)[0]
    sim_description = util.cos_sim(query_embeddings.cpu(), DESCRIPTION_EMBEDDINGS)[0]
    sim_org = util.cos_sim(query_embeddings.cpu(), ORG_EMBEDDINGS)[0]

    # Remove "noisy" low results
    #sim_title = 0 if sim_title < 0.6 else sim_title
    #sim_location = 0 if sim_location < 0.6 else sim_location
    #sim_description = 0 if sim_description < 0.3 else sim_description
    #sim_org = 0 if sim_org < 0.2 else sim_org

    # Weigh the results and add together
    combined_score = (
        TITLE_WEIGHT * sim_title +
        LOCATION_WEIGHT * sim_location +
        DESCRIPTION_WEIGHT * sim_description +
        ORG_WEIGHT * sim_org
    )

    
    top_indices = np.argsort(-combined_score)[:no_of_results]

    results = []
    for idx in top_indices:
        JOBS_DF.reset_index(inplace=True, drop=True)
        idx = int(idx)
        job = JOBS_DF.iloc[idx].to_dict()
        job["score"] = round(float(combined_score[idx]), 3)
        results.append(job)

    return results

