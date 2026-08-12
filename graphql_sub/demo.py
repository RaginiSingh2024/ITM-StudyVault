from graphene import objectType , string, Schema
class Query(objectType):
    hello = string(name=string(default_value="stranger"))

    def resolve_hello(self, info, name):
        return f"Hello, {name}!"            
    
scheme = Schema(query=Query)
gql=""
{
    hello   (name: "GraphQL")   
}    

"""
result = scheme.execute(gql)    
print(result.data['hello'])  # Output: Hello, GraphQL!
    """
