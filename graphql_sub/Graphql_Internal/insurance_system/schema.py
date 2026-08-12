import strawberry
from typing import List
from bson import ObjectId
from database import db

@strawberry.type
class Policy:
    id: str
    policy_name: str
    premium: float

@strawberry.type
class Customer:
    id: str
    name: str
    email: str
    policies: List[Policy]

@strawberry.type
class Query:
    @strawberry.field
    def customers(self) -> List[Customer]:
        customers = []
        for customer in db.customers.find():
            policies = [
                Policy(
                    id=str(policy["_id"]),
                    policy_name=policy["policy_name"],
                    premium=policy["premium"],
                )
                for policy in db.policies.find({"customer_id": str(customer["_id"])})
            ]

            customers.append(
                Customer(
                    id=str(customer["_id"]),
                    name=customer["name"],
                    email=customer["email"],
                    policies=policies,
                )
            )
        return customers

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_customer(self, name: str, email: str) -> str:
        result = db.customers.insert_one({
            "name": name,
            "email": email
        })
        return str(result.inserted_id)

    @strawberry.mutation
    def add_policy(self, customer_id: str, policy_name: str, premium: float) -> str:
        result = db.policies.insert_one({
            "customer_id": customer_id,
            "policy_name": policy_name,
            "premium": premium
        })
        return str(result.inserted_id)

schema = strawberry.Schema(query=Query, mutation=Mutation)