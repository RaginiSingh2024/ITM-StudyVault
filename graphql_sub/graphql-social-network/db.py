from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "ragini123"

driver = GraphDatabase.driver(uri, auth=(username, password))

def run_query(query):
    with driver.session() as session:
        result = session.run(query)
        return [record.data() for record in result]