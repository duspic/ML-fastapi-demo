
FROM python:3.10-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./model /code/model
COPY ./app/ /code/app
COPY ./data /code/data 

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]

EXPOSE 8000