import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Définition des fichiers
INPUT_CLUSTERING = "data_pluvio/clustering_kmeans_results.csv"
INPUT_SOIL = "data_fixed/sol_principal_per_bss.csv"
GRAPH_DIR = "graphs"

# Créer le dossier pour les graphiques s'il n'existe pas
os.makedirs(GRAPH_DIR, exist_ok=True)

# Charger les résultats de clustering
df_cluster = pd.read_csv(INPUT_CLUSTERING, sep=";")

# Charger les données des types de sol
df_soil = pd.read_csv(INPUT_SOIL, sep=";")

# Fusionner les deux datasets sur CODE_BSS
df_merged = df_cluster.merge(df_soil, left_on="station_id", right_on="CODE_BSS", how="left")

# Étude du lien entre cluster et type de sol principal
soil_cluster_analysis = df_merged.groupby("Cluster")["main_soil_type"].value_counts().unstack().fillna(0)

# Visualisation avec annotations
plt.figure(figsize=(12, 6))
sns.heatmap(soil_cluster_analysis, annot=True, cmap="coolwarm", fmt="g")
plt.xlabel("Type de sol principal")
plt.ylabel("Cluster")
plt.title("Cluster dans lequel chaque type de sol est le plus fréquent")
plt.tight_layout()
plt.savefig(os.path.join(GRAPH_DIR, "soil_cluster_most_frequent.png"))
plt.close()

print("Graphique de l'analyse des clusters dominants par type de sol sauvegardé dans graphs/soil_cluster_most_frequent.png")

# Étude du lien entre cluster et la liste complète des types de sol
df_merged["all_soil_types"] = df_merged["all_soil_types"].fillna("Unknown")

# Séparer chaque type de sol dans la liste et les associer aux clusters
df_exploded = df_merged.assign(all_soil_types=df_merged["all_soil_types"].str.split(", ")).explode("all_soil_types")

# Analyser la fréquence des clusters pour chaque type de sol
soil_cluster_freq = df_exploded.groupby("Cluster")["all_soil_types"].value_counts().unstack().fillna(0)

# Affichage en console des types de sol les plus fréquents par cluster (limité à 3)
print("\n📊 Types de sol les plus fréquents par cluster (triés par fréquence, max 3):")
for cluster, row in soil_cluster_freq.iterrows():
    sorted_soils = row.sort_values(ascending=False)
    top_soils = sorted_soils.head(3)
    print(f"Cluster {cluster}: {', '.join([f'{soil} ({count})' for soil, count in top_soils.items()])}")
