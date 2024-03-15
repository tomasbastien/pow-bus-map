import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import json

# Load GTFS files into pandas DataFrames
stops_df = pd.read_csv('stops.txt')
routes_df = pd.read_csv('routes.txt')
stop_times_df = pd.read_csv('stop_times.txt')
trips_df = pd.read_csv('trips.txt')

# Merge relevant data
stops_routes_df = stop_times_df.merge(trips_df, 
on='trip_id').merge(routes_df, on='route_id').merge(stops_df, 
on='stop_id')

# Convert stops to GeoDataFrame
geometry = [Point(xy) for xy in zip(stops_routes_df.stop_lon, 
stops_routes_df.stop_lat)]
stops_gdf = gpd.GeoDataFrame(stops_routes_df, geometry=geometry, 
crs="EPSG:4326")

# Convert routes to GeoJSON LineString
routes_geojson = {}
for route_id, group in stops_routes_df.groupby('route_id'):
    line = LineString(group.geometry)
    routes_geojson[route_id] = line.__geo_interface__

# Write stops GeoJSON
stops_gdf[['stop_id', 'stop_name', 'geometry']].to_file("stops.geojson", 
driver='GeoJSON')

# Write routes GeoJSON
with open("routes.geojson", "w") as outfile:
    json.dump(routes_geojson, outfile)

