import requests
import json

def query_overpass(relation_id):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = (
        "[out:json];"
        f"relation({relation_id});"
        "out geom;"
    )
    response = requests.get(overpass_url, params={'data': overpass_query})
    if response.status_code == 200:
        return response.json()
    else:
        print("Error querying Overpass API:", response.text)
        return None

def main():
    # Read relation IDs from file
    with open("lines", "r") as file:
        relation_ids = file.readlines()

    for relation_id in relation_ids:
        relation_id = relation_id.strip()
        # Query Overpass API
        geojson_data = query_overpass(relation_id)

        if geojson_data:
            # Write GeoJSON data to file named after the relation name
            relation_name = geojson_data['elements'][0]['tags'].get('name', "relation_" + 
relation_id)
            filename = relation_name.replace("'", "") + ".osm"
            with open(filename, "w") as output_file:
                json.dump(geojson_data, output_file, indent=4)
            print("GeoJSON data written to", filename)
        else:
            print("Failed to fetch GeoJSON data for relation ID:", relation_id)

if __name__ == "__main__":
    main()
