from graphene import Schema, ObjectType, String
from fastapi import FastAPI
from starlette_graphene import GraphQLApp

# 1. Define the Data Structure (Query)
class Query(ObjectType):
    # Field 'hello' takes an argument 'name'
    hello = String(name=String(default_value="graphql"))

    @staticmethod
    def resolve_hello(root, info, name):
        return f"Hello {name}"

# 2. Create the Graphene Schema
schema = Schema(query=Query)

# 3. Initialize FastAPI
app = FastAPI()

# 4. Mount the GraphQL App to a route
app.mount("/graphql", GraphQLApp(schema=schema, graphiql=True))

# To run this, use the terminal command:
# uvicorn main:app --reload