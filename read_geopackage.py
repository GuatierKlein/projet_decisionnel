import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# Chemin des fichiers
GPKG_FILE = "data_geo/BDLISA_V3_METRO.gpkg"
LAYER_LITHO = "table_lithologie_niv3"
LAYER_POLYGONES = "entites_niveau3_extension"
INPUT_CSV = "points_eau.csv"  # Chemin du fichier CSV d'entrée
OUTPUT_CSV = "data_fixed/sol_principal_per_bss.csv"  # Chemin du fichier CSV de sortie

# Charger la couche des polygones des entités hydrogéologiques
gdf_polygones = gpd.read_file(GPKG_FILE, layer=LAYER_POLYGONES)[["codeeh", "geometry"]]

# Charger la table des lithologies depuis le GeoPackage
gdf_litho = gpd.read_file(GPKG_FILE, layer=LAYER_LITHO)[["CodeEH", "LbLitho"]]

# Associer les lithologies aux polygones
gdf_litho_polyg = gdf_polygones.merge(gdf_litho, left_on="codeeh", right_on="CodeEH", how="left")

# Charger le fichier CSV des points d'eau
df_points = pd.read_csv(INPUT_CSV, sep=";")

# Convertir tous les points en un seul `GeoDataFrame` au lieu de les traiter un par un
gdf_points = gpd.GeoDataFrame(df_points, 
                              geometry=gpd.points_from_xy(df_points["LONGITUDE"], df_points["LATITUDE"]),
                              crs="EPSG:4326")

# Convertir au même CRS que les polygones
gdf_points = gdf_points.to_crs(gdf_litho_polyg.crs)

# Effectuer la jointure spatiale **une seule fois** pour tous les points
sol_info = gpd.sjoin(gdf_points, gdf_litho_polyg, how="left", predicate="intersects")

# Récupérer le type de sol principal et tous les types de sol pour chaque point
df_sol_types = sol_info.groupby("CODE_BSS")["LbLitho"].agg(lambda x: x.value_counts().idxmax()).reset_index()
df_sol_types.rename(columns={"LbLitho": "main_soil_type"}, inplace=True)

df_all_soils = sol_info.groupby("CODE_BSS")["LbLitho"].agg(lambda x: ", ".join(x.unique())).reset_index()
df_all_soils.rename(columns={"LbLitho": "all_soil_types"}, inplace=True)

# Fusionner avec le DataFrame d'origine
df_sol_types = df_sol_types.merge(df_all_soils, on="CODE_BSS", how="left")

# Sauvegarder le fichier final
df_sol_types.to_csv(OUTPUT_CSV, sep=";", index=False, encoding="utf-8")

print(f"Données enregistrées dans {OUTPUT_CSV}")