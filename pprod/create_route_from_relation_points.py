import requests
import geojson

def query_overpass(relation_id):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = (
        "[out:json];"
        f"relation({relation_id});"
        "out geom;"
    )
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    return data

def extract_points_from_overpass_data(data):
    points = []
    for element in data['elements']:
        if element['type'] == 'relation':
            for member in element['members']:
                if member['type'] == 'node':
                    lon = member['lon']
                    lat = member['lat']
                    points.append([lon, lat])
    return points

def query_openrouteservice(coordinates):
    endpoint = 'https://api.openrouteservice.org/v2/directions/driving-car/geojson'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png',
        'Authorization': '5b3ce3597851110001cf62483a8b9711fdbd49c0b11b4087ad9a32ff'
    }
    data = {
        'coordinates': coordinates
    }
    response = requests.post(endpoint, headers=headers, json=data)
    return response.json()

def create_geojson_route(coordinates, filename):
    route_data = query_openrouteservice(coordinates)
    with open(filename, 'w') as f:
        geojson.dump(route_data, f)

def main():
    relation_id = 17013466
    overpass_data = query_overpass(relation_id)
    points = extract_points_from_overpass_data(overpass_data)
    create_geojson_route(points, 'route.geojson')

if __name__ == "__main__":
    main()

