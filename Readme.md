# TRY IT OUT

**The public URL is:
ml-fastapi-demo-ALB-672004778.eu-north-1.elb.amazonaws.com**

**try to go on /docs to use the fastapi's inbuilt interactive documentation.
or simply to /search?query= and insert your query**

# SUMMARY

This repository is made for **demonstrational purposes**! It serves little to no real-world value.

The main idea is to showcase the modern-day workflow for running ML solutions on the cloud.

The code is comprised of a **data pipeline**, a **ML model** and a **backend API** that serves the model endpoint.
The API is wrapped in a container and deployed on the cloud, and some CI/CD actions ensure an automated deployment and data renewal.

The model should be able to search for (pre-collected) LinkedIn job postings that match the query the user provides.

The tech stack is:

* **BeautifulSoup** for data scraping
* **sentence-transformers** for the pretrained ML model
* **fastapi** for the API
* **Docker** for containerization
* **DockerHub** for container registry
* **AWS** solutions (ECS + ALB) for cloud deployment
* **GitHub Actions** for CI/CD

---

## Data pipeline

### Scraping:

in the /scripts folder, there is a scrape.py file. Given the keywords (e.g. "python") and locations (e.g. "remote") , it sends GET requests to find lists of job postings on LinkedIn that match the criteria.
Once it has collected the URLs of individual postings, it sends a GET request to each of them in order to extract the information about them. These requests are sent in parallel, and have multiple retries with increasing wait times, as LinkedIn has scraping mitigation techniques which block a lot of the requests otherwise. The results are gathered in a pandas DataFrame, which can be substituted for inbuilt plain csv to avoid the weight of the library.

This script takes command line arguments, which is useful for later automatization.

### Embeddings:

embed_job_data.py - loads the model (more on the model later on), and the dataframe. Using the model, it encodes separately various columns from the scraped data. The whole rows aren't encoded together because the descriptions are long and full of redundant information, and the queries are most likely simple and short, up to 5 words. This would mean that there is never really a good match between the query and the job posting, as they'll never quite be similar. But, if the location and the job title and organization name are encoded separately - there is a better possibility for a good match. For better results, more fields could be separately encoded.

The embeddings are saved as numpy arrays, so the model can quickly load them up at startup, and use them right away in inference.

## ML Model

The model is a sentence transformer, pretrained and imported from the sentence-transformers library.
The use case is **semantic search -** the model takes the user's query, embeds it and then checks the similarity between the query embedding and the loaded embeddings from the data pipeline. It uses cosine similarity between the query embedding and each individual corpus embedding, and then combines the result, each with a hardcoded weight applied. This means that it checks the similarity to the query for each title, organization name, location and description separately, and combines the results to find the job postings which are the most similar.
In this use case, this works ok because a query such as "python developer remote" will have a high similarity to job postings that mention "python developer" in the title or "zagreb" in the location.

The model is saved and loaded locally, or pulled from the sentence-transformers repository if it's missing.

## API

The API is made with the FastAPI library. It's extremely simple, as it has only a root endpoint (used to check for "health" on the cloud), and the /search endpoint.

The model is served via the /search GET endpoint, which takes a single text argument "query".
To ensure some consistent behaviour, a simple pydantic schema is used, and it defines the structure of the output JSON.

## (Continuous) Deployment

I've included a simple dockerfile which instructs the API to run, and be available on the port 8000.
Also, there is a .github folder, in which there are two scripts.

1. build_and_deploy
   This ensures that, once the main branch is pushed, a docker image is built, pushed to dockerhub, and then pulled from dockerhub to AWS's Elastic Container Service.
2. scrape_ebmed_data
   This ensures that, once a day, new data is scraped from linkedin and then encoded into embeddings.
   Then, a pull request is made with the new data, which I need to manually inspect and merge into the main branch if I wish.

The ECS is made publicly available through an Application Load Balancer, which gives it the DNS

---


In a real-world scenario, everything should be better!

- A better use-case
- better data collection and cleanup
- model fine-tuning
- better containerization / smaller image
- data placed in a bucket instead of the docker container
- reverse proxy / better load balancer
- cleaner code altogether...

But hopefully, this is enough for a demo ;)
