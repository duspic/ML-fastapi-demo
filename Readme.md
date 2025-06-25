## Github

- moraš izbrisat ECR, jer uploudaš na docker hub
  moraš dodati dockerhub credentialse u secretse
- promijeniti deploy.yaml

1. [X] izbriši github repo
2. [X] izbriši ECR
3. [X] sve se deploya na jedan repo,
4. [X] jednom dnevno ili na klik se skrejpa i pusha
5. [X] prilikom svakog pusha se pusha na docker hub
6. [X] napravi i postavi secrete

provjeri zašto je skrejpanje užasno.

7. [ ] s docker huba treba na ecs

docker run --name sentransformer-fastapi-demo -p 8000:8000 sentransformer-fastapi-demo
