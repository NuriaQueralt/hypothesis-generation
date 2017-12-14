from neo4j.v1 import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "xena"))

def print_query(tx):
    for record in tx.run("MATCH path=(source)-[]->(target) "
                         "RETURN target.id, target.preflabel, path LIMIT 3"):
        print(record['path'].nodes[0].id, record['path'].nodes[0].labels, record['path'].nodes[0]['preflabel'])
        #print(record['path'].nodes[0].id, record['path'].nodes[0].labels, record['path'].nodes[0].properties['preflabel'])

with driver.session() as session:
    session.read_transaction(print_query)
