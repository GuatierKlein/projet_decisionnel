import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# Définition des fichiers
INPUT_CROSS_CORR = "data_pluvio/cross_correlation_results.csv"
OUTPUT_CLUSTERING = "data_pluvio/clustering_dbscan_results.csv"
GRAPH_DIR = "graphs"

# Créer le dossier pour les graphiques s'il n'existe pas
os.makedirs(GRAPH_DIR, exist_ok=True)

# Charger les résultats de cross-corrélation
df_cross_corr = pd.read_csv(INPUT_CROSS_CORR, sep=";")

# Vérifier les données
if df_cross_corr.empty:
    print("Erreur : Aucune donnée de cross-corrélation trouvée.")
    exit()

# Préparer les données pour le clustering
features = ["Décalage max (jours)", "Corrélation max"]
df_features = df_cross_corr[features]

# Normaliser les données
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df_features)

# Optimisation des paramètres DBSCAN (eps et min_samples)
best_eps = 0.5
best_min_samples = 5
best_score = -1

for eps in np.arange(0.1, 2.0, 0.1):
    for min_samples in range(2, 10):
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(df_scaled)
        
        if len(set(labels)) > 1 and -1 not in labels:
            score = silhouette_score(df_scaled, labels)
            if score > best_score:
                best_score = score
                best_eps = eps
                best_min_samples = min_samples

print(f"Meilleurs paramètres DBSCAN : eps={best_eps}, min_samples={best_min_samples}")

# Appliquer DBSCAN avec les paramètres optimaux
dbscan = DBSCAN(eps=best_eps, min_samples=best_min_samples)
df_cross_corr["Cluster"] = dbscan.fit_predict(df_scaled)

# Vérifier si DBSCAN a trouvé plusieurs clusters
unique_clusters = np.unique(df_cross_corr["Cluster"])
if len(unique_clusters) > 1:
    silhouette_avg = silhouette_score(df_scaled, df_cross_corr["Cluster"])
    print(f"Score silhouette : {silhouette_avg:.2f}")
else:
    print("DBSCAN n'a détecté qu'un seul cluster ou des points bruités.")

# Sauvegarder les résultats
df_cross_corr.to_csv(OUTPUT_CLUSTERING, sep=";", index=False, encoding="utf-8")
print(f"Résultats de clustering enregistrés dans {OUTPUT_CLUSTERING}")

# Visualisation des clusters
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_cross_corr, x="Décalage max (jours)", y="Corrélation max", hue="Cluster", palette="tab10")
plt.xlabel("Décalage max (jours)")
plt.ylabel("Corrélation max")
plt.title("Clustering DBSCAN des nappes en fonction du retard et de la corrélation aux précipitations")
plt.savefig(os.path.join(GRAPH_DIR, "clustering_dbscan_results.png"))
plt.close()
print("Graphique du clustering DBSCAN sauvegardé dans graphs/clustering_dbscan_results.png")