import requests
import folium
from folium.plugins import FloatImage
import json
import math
import os
import geojson

# Function to fetch GeoJSON data from Overpass API
def fetch_overpass_data(relation_id):
    overpass_query = (
        "[out:json];"
        f"relation({relation_id});"
        "out geom;"
    )
    overpass_url = "http://overpass-api.de/api/interpreter"
    response = requests.get(overpass_url, params={"data": overpass_query})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch Overpass data for relation {relation_id}: {response.text}")
        return None

# Function to convert OSM GeoJSON to GeoJSON compatible with Folium
def osm_to_folium_geojson(osm_geojson, layer_name):
    features = []
    for feature in osm_geojson['elements']:
        if feature['type'] == 'relation':
            # Extract relation name from tags
            relation_tags = feature.get('tags', {})
            relation_name = relation_tags.get('name')
            
            for member in feature.get('members', []):
                if member['type'] == 'way':
                    way_coordinates = []
                    for node in member.get('geometry', []):
                        lon = float(node['lon'])
                        lat = float(node['lat'])
                        if -90 <= lat <= 90:
                            way_coordinates.append([lon, lat])
                        else:
                            print(f"Ignoring invalid node with coordinates: [{lon}, {lat}]")
                    if len(way_coordinates) > 1:  # Ensure at least two valid coordinates for a line
                        features.append({
                            'type': 'Feature',
                            'geometry': {
                                'type': 'LineString',
                                'coordinates': way_coordinates
                            },
                            'properties': {
                                'name': relation_name
                            }
                        })
                elif member['type'] == 'node':
                    lon = float(member['lon'])
                    lat = float(member['lat'])
                    if -90 <= lat <= 90:
                        features.append({
                            'type': 'Feature',
                            'geometry': {
                                'type': 'Point',
                                'coordinates': [lon, lat]
                            },
                            'properties': {
                                'name': relation_name
                            }
                        })
                    else:
                        print(f"Ignoring invalid node with coordinates: [{lon}, {lat}]")
        elif feature['type'] == 'node':
            lon = float(feature['lon'])
            lat = float(feature['lat'])
            if -90 <= lat <= 90:
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [lon, lat]
                    },
                    'properties': {
                        'name': layer_name
                    }
                })
            else:
                print(f"Ignoring invalid node with coordinates: [{lon}, {lat}]")
    
    return {'type': 'FeatureCollection', 'features': features}

# Function to save GeoJSON data to a file
def save_geojson(data, filename):
    with open(filename, "w") as output_file:
        json.dump(data, output_file, indent=4)
    print("GeoJSON data written to", filename)

# Function to calculate the bounding box of GeoJSON features
def calculate_bounding_box(geojson):
    min_lon, min_lat, max_lon, max_lat = float('inf'), float('inf'), float('-inf'), float('-inf')
    for feature in geojson['features']:
        geometry = feature['geometry']
        if geometry['type'] == 'Point':
            if len(geometry['coordinates']) == 3:
                lon, lat, altitude = geometry['coordinates']
            else:
                lon, lat = geometry['coordinates']
                altitude = None  # Altitude is absent
            min_lon = min(min_lon, lon)
            min_lat = min(min_lat, lat)
            max_lon = max(max_lon, lon)
            max_lat = max(max_lat, lat)
        elif geometry['type'] == 'LineString' or geometry['type'] == 'MultiPoint':
            for coord in geometry['coordinates']:
                if len(coord) == 3:
                    lon, lat, altitude = coord
                else:
                    lon, lat = coord
                    altitude = None  # Default to None if altitude is missing
                min_lon = min(min_lon, lon)
                min_lat = min(min_lat, lat)
                max_lon = max(max_lon, lon)
                max_lat = max(max_lat, lat)
        elif geometry['type'] == 'Polygon' or geometry['type'] == 'MultiLineString':
            for segment in geometry['coordinates']:
                for coord in segment:
                    if len(coord) == 3:
                        lon, lat, altitude = coord
                    else:
                        lon, lat = coord
                        altitude = None  # Default to None if altitude is missing
                    min_lon = min(min_lon, lon)
                    min_lat = min(min_lat, lat)
                    max_lon = max(max_lon, lon)
                    max_lat = max(max_lat, lat)
        elif geometry['type'] == 'MultiPolygon':
            for polygon in geometry['coordinates']:
                for segment in polygon:
                    for coord in segment:
                        if len(coord) == 3:
                            lon, lat, altitude = coord
                        else:
                            lon, lat = coord
                            altitude = None  # Default to None if altitude is missing
                        min_lon = min(min_lon, lon)
                        min_lat = min(min_lat, lat)
                        max_lon = max(max_lon, lon)
                        max_lat = max(max_lat, lat)
    return min_lon, min_lat, max_lon, max_lat

def on_click_zoom_on_layer(e):
    # Get the coordinates of the clicked point
    lat, lon = e.latlng
    # Re-center the map
    m.panTo([lat, lon])


#### READ OSM IDs ####

# Read relation IDs from file
with open("./ressources/lines", "r") as file:
    relation_ids = [int(line.strip()) for line in file.readlines()]

# Initialize variables for bounding box calculation
all_geojson_features = []

# Fetch and process GeoJSON data for each relation ID
for relation_id in relation_ids:
    osm_geojson = fetch_overpass_data(relation_id)
    if osm_geojson:
        # Extract the name of the relation from its tags
        relation_tags = osm_geojson['elements'][0].get('tags', {})
        layer_name = relation_tags.get('name', f"Unnamed Layer {relation_id}")

        # Convert OSM GeoJSON to GeoJSON compatible with Folium
        folium_geojson = osm_to_folium_geojson(osm_geojson, layer_name)
        all_geojson_features.extend(folium_geojson['features'])


#### READ GEOJSON FILES #####

directory_path = './ressources/geojson/'
for filename in os.listdir(directory_path):
    if filename.endswith(".geojson"):
        file_path = os.path.join(directory_path, filename)
        print("processing "+file_path)
        # Open and load the GeoJSON file
        with open(file_path, 'r') as geojson_file:
            data = geojson.load(geojson_file)
            
            # Check if the GeoJSON contains 'features'
            if 'features' in data:
                all_geojson_features.extend(data['features'])

# print(all_geojson_features)

# Calculate the bounding box of all GeoJSON features
min_lon, min_lat, max_lon, max_lat = calculate_bounding_box({'type': 'FeatureCollection', 'features': all_geojson_features})

# Calculate the center of the bounding box
center_lon = (min_lon + max_lon) / 2
center_lat = (min_lat + max_lat) / 2

# Calculate the zoom level based on the bounding box dimensions
delta_lon = max_lon - min_lon
delta_lat = max_lat - min_lat
max_delta = max(delta_lon, delta_lat)
zoom_level = math.floor(8 - math.log(max_delta, 2))

# Create a folium map centered on the calculated center
mymap = folium.Map(location=[center_lat, center_lon], zoom_start=8)

# Add all GeoJSON features to the map with tooltips
for feature in all_geojson_features:
    if feature['geometry']['type'] == 'Point':
        lon, lat = feature['geometry']['coordinates']
        fill_color = '#003b5c'  # Custom fill color using hexadecimal color code (e.g., orange)
        border_color = '#003b5c'  # Custom fill color using hexadecimal color code (e.g., orange)
        folium.CircleMarker(location=[lat, lon], radius=2, color=border_color, fill=False, fill_color=fill_color, tooltip=feature['properties']['name']).add_to(mymap)


# for feature in all_geojson_features:
    if feature['geometry']['type'] == 'LineString':
            style_lines = lambda x: {'color': '#003b5c'}
            folium.GeoJson(feature, tooltip=feature['properties']['name'], style_function=style_lines).add_to(mymap)

    if feature['geometry']['type'] == 'MultiLineString':
            style_lines = lambda x: {'color': '#003b5c'}
            # print(feature['properties'])
            if 'name' in feature['properties']:
                folium.GeoJson(feature, tooltip=feature['properties']['name'], style_function=style_lines).add_to(mymap)
            elif (('route_short_name' in feature['properties']) and ('route_long_name' in feature['properties'])):
                folium.GeoJson(feature, tooltip=feature['properties']['route_short_name']+" - "+feature['properties']['route_long_name'], style_function=style_lines).add_to(mymap)



#### DESTINATIONS ####

# Read points from destinations-hiver.json and add them to the map
with open("./ressources/destinations-hiver.json", "r") as dest_file:
    points_data = json.load(dest_file, strict=False)
    for point_feature in points_data['features']:
        point_properties = point_feature.get('properties', {})
        point_geometry = point_feature.get('geometry', {})
        if point_geometry['type'] == 'Point':
            lon, lat = point_geometry['coordinates']
            name = point_properties.get('name', 'Unnamed Point')
            # Define the head color as a hexadecimal color code
            #head_color = '#faea5d'  # POW Yellow
            head_color = '#fea8db'  # POW Pink
            # Generate the SVG code with the dynamic head color
            pin_icon_html = f"""
            <div style="position: relative; width: 24px; height: 24px;">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <!-- Pin head (circle) -->
                <circle cx="12" cy="6" r="5" fill="{head_color}" />
                <!-- Pin body (line) -->
                <path d="M12 11v10" />
              </svg>
            </div>
            """
            custom_icon = folium.features.DivIcon(
                html=pin_icon_html,
                icon_size=(24, 24),
                icon_anchor=(12, 24)
            )
            # color = point_properties.get('marker-color', 'blue')
            # icon = folium.Icon(color=color, icon='snowflake', prefix='fa', icon_color='white')
            # folium.Marker(location=[lat, lon], tooltip=name, icon=icon).add_to(mymap)
            folium.Marker(
                location=[lat, lon],
                tooltip=name,
                icon=custom_icon
            ).add_to(mymap)

# Add watermark
url = ("./ressources/logo-POW-Fr-bleu-2.png")
FloatImage(url, bottom=5, left=2, width='100px').add_to(mymap)


# Save the map to an HTML file
output_map_file = "leaflet_map.html"
mymap.save(output_map_file)
print(f"Map saved as '{output_map_file}'")
