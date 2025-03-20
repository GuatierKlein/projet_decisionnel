import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point
import os
import pandas as pd

# Définition des paramètres
INPUT_CSV = "points_eau.csv"  # Remplacez par le chemin de votre fichier CSV
OUTPUT_DIR = "maps/"  # Dossier de sortie des fichiers à la racine du projet

# Vérifier et créer le dossier de sortie si nécessaire
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Charger le fichier CSV d'entrée
df = pd.read_csv(INPUT_CSV, sep=';', dtype=str)  # Charger toutes les colonnes en tant que chaînes

# Convertir les coordonnées en float (gérer les éventuelles erreurs de parsing)
df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors='coerce')
df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors='coerce')

# Extraire les coordonnées et les noms des stations
stations_coords = df[["CODE_BSS", "LATITUDE", "LONGITUDE"]].dropna()

# Inverser l'ordre des coordonnées si nécessaire (correction courante)
gdf = gpd.GeoDataFrame(
    stations_coords,
    geometry=[Point(lon, lat) for lat, lon in zip(stations_coords["LATITUDE"], stations_coords["LONGITUDE"])],
    crs="EPSG:4326"  # Vérifier que les coordonnées sont bien en WGS84
)

# Vérifier les premières lignes pour détecter une éventuelle inversion des colonnes
print(gdf.head())

# Convertir en projection Web Mercator pour OpenStreetMap
gdf = gdf.to_crs(epsg=3857)

# Tracer la carte avec OpenStreetMap
fig, ax = plt.subplots(figsize=(8, 8))
gdf.plot(ax=ax, color="red", markersize=100, label="Stations")
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

# Ajouter les noms des stations
for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf["CODE_BSS"]):
    ax.text(x, y, label, fontsize=10, ha="right", color="blue")

ax.set_title("Localisation des Stations Hydrologiques en France")
plt.legend()
plt.savefig(os.path.join(OUTPUT_DIR, "map_raw.png"))
