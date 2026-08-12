from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import Request
from graphene import ObjectType, String, Schema, Field, Int, List, Mutation, InputObjectType
from sqlalchemy import create_engine, Column, Integer, String as saString, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import json

# ---------------- DATABASE CONFIG ---------------- #

DB_URL = "postgresql+psycopg2://postgres:lYSVkdiMCaFyZiKqxaBjfYCzWgLMRpLE@maglev.proxy.rlwy.net:48424/railway"

engine = create_engine(DB_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# ---------------- MODELS ---------------- #

class Employer(Base):
    __tablename__ = "employers"
    id = Column(Integer, primary_key=True)
    name = Column(saString)
    contact_email = Column(saString)
    industry = Column(saString)
    jobs = relationship("Job", back_populates="employer")


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(saString)
    description = Column(saString)
    employer_id = Column(Integer, ForeignKey("employers.id"))
    employer = relationship("Employer", back_populates="jobs")


Base.metadata.create_all(engine)

# ---------------- GRAPHQL TYPES ---------------- #

class EmployerObject(ObjectType):
    id = Int()
    name = String()
    contact_email = String()
    industry = String()


class JobObject(ObjectType):
    id = Int()
    title = String()
    description = String()
    employer_id = Int()


# ---------------- MUTATION ---------------- #

class CreateJobInput(InputObjectType):
    title = String(required=True)
    description = String(required=True)
    employer_id = Int(required=True)


class CreateJob(Mutation):
    class Arguments:
        input = CreateJobInput(required=True)

    job = Field(JobObject)

    def mutate(root, info, input):
        session = SessionLocal()
        new_job = Job(
            title=input.title,
            description=input.description,
            employer_id=input.employer_id,
        )
        session.add(new_job)
        session.commit()
        session.refresh(new_job)
        session.close()
        return CreateJob(job=new_job)


# ---------------- QUERY ---------------- #

class Query(ObjectType):
    jobs = List(JobObject)

    def resolve_jobs(root, info):
        session = SessionLocal()
        jobs = session.query(Job).all()
        session.close()
        return jobs


class Mutation(ObjectType):
    create_job = CreateJob.Field()


schema = Schema(query=Query, mutation=Mutation)

# ---------------- FASTAPI APP ---------------- #

app = FastAPI()

@app.post("/graphql")
async def graphql_server(request: Request):
    body = await request.json()
    result = schema.execute(body.get("query"))
    return JSONResponse(result.data)