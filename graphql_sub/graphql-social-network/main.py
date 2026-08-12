import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from schema import Query, Mutation

schema = strawberry.Schema(query=Query, mutation=Mutation)

app = FastAPI()

graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")