import graphene

# ---------------------------------------------------------
# 1. DEFINING THE SCHEMA (The "Shape" of your API)
# ---------------------------------------------------------
# In Graphene, we define the structure of our data using classes 
# that inherit from graphene.ObjectType.
#
# Here, we define a 'Query' class. This acts as the entry point 
# for fetching data. Think of it as the "GET" request in REST.

class Query(graphene.ObjectType):
    # We define two fields available to be queried: 'hello' and 'goodbye'.
    # These are both Strings.
    
    # Field 1: 'hello'
    # It accepts an optional argument 'first_name'. 
    # If no name is provided, it defaults to "stranger".
    hello = graphene.String(first_name=graphene.String(default_value="stranger"))
    
    # Field 2: 'goodbye'
    # It takes no arguments, just returns a String.
    goodbye = graphene.String()

    # -----------------------------------------------------
    # 2. WRITING RESOLVERS (The "Logic" of your API)
    # -----------------------------------------------------
# For every field you define above, you need a method to fetch its data.
    # Naming Convention: resolve_<field_name>
    
    def resolve_hello(root, info, first_name):
        # Logic to return the data for the 'hello' field.
        # 'root': The value returned by the parent field (usually None at the top level).
        # 'info': Context regarding the execution state (auth, request info, etc).
        # 'first_name': The argument defined in the field above.
        return f'Hello {first_name}!'

    def resolve_goodbye(root, info):
        # Logic to return data for 'goodbye'.
        return 'See ya!'

# ---------------------------------------------------------
# 3. INITIALIZING THE API
# ---------------------------------------------------------
# We create the actual Schema object by passing our Query class.
schema = graphene.Schema(query=Query)

# ---------------------------------------------------------
# 4. EXECUTING QUERIES (Simulating a Client Request)
# ---------------------------------------------------------

# Example A: Basic Query using the default value
print("--- Query 1: Default Argument ---")
query_string = '{ hello }'
result = schema.execute(query_string)
print(f"Query: {query_string}")
print(f"Result: {result.data['hello']}") 
# Output: Hello stranger!


# Example B: Query with an argument
print("\n--- Query 2: With Argument ---")
# Note: In GraphQL, arguments are passed inside parentheses ()
query_with_arg = '{ hello(firstName: "Student") }'
result = schema.execute(query_with_arg)
print(f"Query: {query_with_arg}")
print(f"Result: {result.data['hello']}")
# Output: Hello Student!


# Example C: Querying multiple fields
print("\n--- Query 3: Multiple Fields ---")
multi_query = '''
    {
        hello(firstName: "Teacher")
        goodbye
    }
'''
result = schema.execute(multi_query)
print(f"Result: {result.data}")
# Output: {'hello': 'Hello Teacher!', 'goodbye': 'See ya!'}