import json

def create_umap_file(layer_names_file):
    with open(layer_names_file, 'r') as file:
        layer_names = file.readlines()

    umap_data = {
        "type": "umap",
        "geometry": {},
        "properties": {
            "name": "UMAP File with Named Layers"
        },
        "uri": "https://umap.openstreetmap.fr",
        "layers": []
    }

    for name in layer_names:
        layer_name = name.strip()
        layer = {
            "type": "FeatureCollection",
            "features": [],
            "_umap_options": {
                "name": layer_name,
                "editMode": "advanced",
                "browsable": True,
                "inCaption": True,
                "displayOnLoad": True
            }
        }
        umap_data["layers"].append(layer)

    filename = "umap_file.umap"
    with open(filename, 'w') as f:
        f.write(json.dumps(umap_data, indent=2))

    print("UMAP format file saved as: {}".format(filename))

def main():
    layer_names_file = "layers.txt"
    create_umap_file(layer_names_file)

if __name__ == "__main__":
    main()
