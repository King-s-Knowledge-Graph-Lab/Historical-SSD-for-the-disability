import time, requests, json
from qwikidata.entity import WikidataItem
from qwikidata.json_dump import WikidataJsonDump
from qwikidata.utils import dump_entities_to_json
import sqlite3
from tqdm import tqdm
from SPARQLWrapper import SPARQLWrapper, JSON

conn = sqlite3.connect('resources/filtered_database.db')
cursor = conn.cursor()

cursor.execute("SELECT mesh FROM articles")
mesh_list = [row[0] for row in cursor.fetchall()]

conn.close()

print(f"Number of mesh entries: {len(mesh_list)}")

split_mesh_list = []
for mesh_entry in tqdm(mesh_list):
    split_mesh_list.extend(mesh_entry.split('|'))

print(f"Number of split mesh entries: {len(split_mesh_list)}")
split_mesh_list = list(set(split_mesh_list))[1:]


def get_entity_by_label(label):
    # Search for entities by label using the Wikidata API
    url = "https://www.wikidata.org/w/api.php"
    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'language': 'en',
        'type': 'item',
        'search': label
    }
    response = requests.get(url, params=params)
    results = response.json()['search']
    if results:
        return results[0]['id']  # Return the ID of the first matching entity
    else:
        return None

def get_rdf_triples(entity_id):
    # Fetch the RDF triples for a given entity ID
    if entity_id:
        rdf_url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.ttl"
        response = requests.get(rdf_url)
        return response.text
    else:
        return "No data found."

def fetch_specific_triples(entity_id):
    # Set up the SPARQL endpoint and query
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = """
    SELECT ?property ?value ?entityLabel
    WHERE {
      wd:%s ?p ?statement .
      ?statement ?ps ?value .
      ?property wikibase:claim ?p.
      ?property wikibase:statementProperty ?ps.
      OPTIONAL { wd:%s rdfs:label ?entityLabel FILTER (LANG(?entityLabel) = "en") }
    }
    """ % (entity_id, entity_id)
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    # Store results in a dictionary
    data = {'properties': {}}
    entity_label = None
    for result in results["results"]["bindings"]:
        property_id = result['property']['value'].split('/')[-1]  # Extracting property ID
        value = result['value']['value']
        if 'entityLabel' in result:
            entity_label = result['entityLabel']['value']  # Extract entity label
        if property_id not in data['properties']:
            data['properties'][property_id] = []
        data['properties'][property_id].append(value)
    
    # Store entity label and Q-ID if available
    if entity_label:
        data['entityLabel'] = entity_label
        data['entityID'] = entity_id
    
    return data


result = {}
batch_size = 1000 
current_batch = 0

for keyword in tqdm(split_mesh_list):
    entity_id = get_entity_by_label(keyword)
    if entity_id:  # Ensure there is an entity ID returned
        entity_data = fetch_specific_triples(entity_id)
        result[keyword] = entity_data

    current_batch += 1
    # Check if it's time to save the batch
    if current_batch % batch_size == 0:
        with open('wikidata_results.json', 'w') as f:
            json.dump(result, f, indent=4)
        print(f"Saved {current_batch} entries to JSON.")
    time.sleep(1)

# Save any remaining data after the loop finishes
with open('wikidata_results.json', 'w') as f:
    json.dump(result, f, indent=4)
print(f"Final save completed. Total entries saved: {len(result)}")