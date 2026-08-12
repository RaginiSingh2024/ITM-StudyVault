import graphene
from datetime import datetime

# ==========================================
# 1. ENUMS
# ==========================================
# Students should note: Enums restrict a field to a specific set of values.
# Unlike standard Python Enums, in Graphene we inherit from graphene.Enum.

class MissionStatus(graphene.Enum):
    SCHEDULED = 1
    ACTIVE = 2
    COMPLETED = 3
    ABORTED = 4

    @property
    def description(self):
        if self == MissionStatus.ABORTED:
            return "Mission was cancelled due to unforeseen errors."
        return "Standard mission status."

# ==========================================
# 2. INTERFACES
# ==========================================
# Students should note: Interfaces are abstract types. They define a set of 
# fields that other types *must* implement. Useful for grouping related objects.

class SpaceEntity(graphene.Interface):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)
    
    # Students should note: When using Interfaces, Graphene needs to know 
    # how to map a raw Python object to a specific Graphene Type (Astronaut or Spaceship).
    # We use resolve_type for this.
    @classmethod
    def resolve_type(cls, instance, info):
        if instance['type'] == 'astronaut':
            return Astronaut
        elif instance['type'] == 'spaceship':
            return Spaceship
        return None

# ==========================================
# 3. OBJECT TYPES & SCALARS
# ==========================================
# Students should note: ObjectTypes are the meat of your schema. 
# They implement Interfaces using the Meta inner class.

class Astronaut(graphene.ObjectType):
    class Meta:
        interfaces = (SpaceEntity, )

    # Standard Scalars: String, Int, Boolean, ID, Float
    rank = graphene.String()
    # Custom Scalar: DateTime (provided by Graphene)
    joined_at = graphene.DateTime()

class Spaceship(graphene.ObjectType):
    class Meta:
        interfaces = (SpaceEntity, )

    cargo_capacity = graphene.Int()
    # List Modifier: A list of Strings
    crew_names = graphene.List(graphene.String)

# ==========================================
# 4. UNIONS
# ==========================================
# Students should note: Unions are similar to Interfaces, but the types 
# do NOT need to share common fields. It's literally "This OR That".

class SearchResult(graphene.Union):
    class Meta:
        types = (Astronaut, Spaceship)

# ==========================================
# 5. MUTATIONS & INPUT OBJECTS
# ==========================================
# Students should note: To send complex objects as arguments (like a JSON object),
# we use InputObjectType.

class AstronautInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    rank = graphene.String(default_value="Cadet")

class CreateAstronaut(graphene.Mutation):
    # Arguments the client sends TO the server
    class Arguments:
        astronaut_data = AstronautInput(required=True)

    # Fields the server sends BACK to the client
    astronaut = graphene.Field(Astronaut)
    success = graphene.Boolean()

    # The logic function
    def mutate(root, info, astronaut_data):
        # In a real app, you would save to DB here.
        # We just return the data to simulate creation.
        new_astronaut = {
            "type": "astronaut",
            "id": "999",
            "name": astronaut_data.name,
            "rank": astronaut_data.rank,
            "joined_at": datetime.now()
        }
        # Notice we return an instance of the Mutation class
        return CreateAstronaut(astronaut=new_astronaut, success=True)

# ==========================================
# 6. ROOT QUERY
# ==========================================

class Query(graphene.ObjectType):
    # Field returning a List of an Interface
    # NonNull(List) means the list itself cannot be None (but it can be empty).
    entities = graphene.List(graphene.NonNull(SpaceEntity))
    
    # Field returning a Union
    search = graphene.Field(SearchResult, query=graphene.String())

    def resolve_entities(root, info):
        # Mock database data
        return [
            {"type": "astronaut", "id": "1", "name": "Buzz", "rank": "Commander", "joined_at": datetime(2020, 1, 1)},
            {"type": "spaceship", "id": "2", "name": "Apollo", "cargo_capacity": 5000, "crew_names": ["Neil", "Buzz"]}
        ]

    def resolve_search(root, info, query):
        # Simple mock search logic
        if query == "ship":
            return {"type": "spaceship", "id": "2", "name": "Apollo", "cargo_capacity": 5000}
        return {"type": "astronaut", "id": "1", "name": "Buzz", "rank": "Commander"}

# ==========================================
# 7. ROOT MUTATION
# ==========================================

class Mutation(graphene.ObjectType):
    create_astronaut = CreateAstronaut.Field()

# ==========================================
# 8. SCHEMA ASSEMBLY
# ==========================================
# Students should note: We must register types that aren't directly referenced 
# but might be returned via Interfaces/Unions in the 'types' list if Graphene 
# misses them, though usually, it's smart enough.
schema = graphene.Schema(query=Query, mutation=Mutation, types=[Astronaut, Spaceship])

# ==========================================
# 9. EXECUTION EXAMPLES
# ==========================================

if __name__ == "__main__":
    print("--- 1. Querying an Interface (Polymorphism) ---")
    # Students should note: We use '... on TypeName' (Inline Fragments) to select 
    # fields specific to the concrete type (Astronaut or Spaceship).
    query_interface = """
    {
        entities {
            name
            ... on Astronaut {
                rank
                joinedAt
            }
            ... on Spaceship {
                cargoCapacity
            }
        }
    }
    """
    result = schema.execute(query_interface)
    print(result.data)

    print("\n--- 2. Executing a Mutation ---")
    mutation_query = """
    mutation {
        createAstronaut(astronautData: {name: "Major Tom", rank: "Captain"}) {
            success
            astronaut {
                name
                rank
            }
        }
    }
    """
    result = schema.execute(mutation_query)
    print(result.data)