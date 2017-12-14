####
# @author: Núria Queralt Rosinach
# @version: 01-12-2017
# trying official python client

from neo4j.v1 import GraphDatabase, basic_auth


# initialize neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "xena"))

# ask the driver object for a new session
with driver.session() as session:
    # find high degree nodes (hubs)
    query = "MATCH (n) WITH n [] AS "
    result = session.run(query)
