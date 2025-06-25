from pydantic import BaseModel, RootModel, HttpUrl

class JobSchema(BaseModel):
    title: str
    location: str
    org_name: str
    org_link: HttpUrl
    description: str
    job_posting_link: HttpUrl
    score: float
    
class JobSchemaList(RootModel):
    root: list[JobSchema]