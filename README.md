# pow-bus-map
Created for Protect Our Winters France, based on an shared inventory and OpenStreetMap id, render a map that presents bus lines that allow to reach outdoors destinations

Lines details are gathered across the POW community, in order to update OpenSteetMap data. Then this python script uses Overpass to query OpenStreeMap about IDs specified in the "lines" file, to get geometry datas and generate associated layer on a Leaflet map (with Folium library).

Helped with ChatGPT prompts.

Published on https://protectourwinters.fr/se-deplacer/

