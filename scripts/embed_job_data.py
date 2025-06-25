import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Stupid fix for import issues
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import utils




model = utils.load_model()
jobs_df = pd.read_csv("data/scraped_linkedin_jobs.csv").fillna("") 
# replace NaNs because they're float type and cause errors - only strings are expected


# The descriptions are very long and contain a lot of redundant information. 
# The queries, however, are short and based on the most relevant information.
# A good approach seems to be encoding separate embeddings, and combining them with some weights later on.
titles = jobs_df["title"].tolist()
locations = jobs_df["location"].tolist()
descriptions = jobs_df["description"].tolist()
org_names = jobs_df["org_name"].tolist()

print("Starting the embedding process")
title_embeddings = model.encode(titles, convert_to_numpy=True, show_progress_bar=True)
location_embeddings = model.encode(locations, convert_to_numpy=True, show_progress_bar=True)
description_embeddings = model.encode(descriptions, convert_to_numpy=True, show_progress_bar=True)
org_embeddings = model.encode(org_names, convert_to_numpy=True, show_progress_bar=True)

print("Saving embeddings to /data")
np.save("data/title_embeddings.npy", title_embeddings)
np.save("data/location_embeddings.npy", location_embeddings)
np.save("data/description_embeddings.npy", description_embeddings)
np.save("data/org_embeddings.npy", org_embeddings)

print("Succesfully saved embeddings")