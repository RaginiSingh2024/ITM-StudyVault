import strawberry

@strawberry.type
class FriendRequest:
    id: int
    status: str


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello GraphQL"


@strawberry.type
class Mutation:

    @strawberry.mutation
    def sendFriendRequest(self, senderId:int, receiverId:int) -> FriendRequest:
        return FriendRequest(id=1, status="pending")