import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# Définition des fichiers
INPUT_CROSS_CORR = "data_pluvio/cross_correlation_results.csv"
OUTPUT_CLUSTERING = "data_pluvio/clustering_kmeans_results.csv"
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

# Déterminer le nombre optimal de clusters avec la méthode du coude
inertia = []
K_range = range(2, 10)
for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(df_scaled)
    inertia.append(kmeans.inertia_)

# Tracer la méthode du coude
plt.figure(figsize=(8, 5))
plt.plot(K_range, inertia, marker='o', linestyle='-')
plt.xlabel("Nombre de clusters")
plt.ylabel("Inertie")
plt.title("Méthode du coude pour déterminer K optimal")
plt.savefig(os.path.join(GRAPH_DIR, "elbow_method_kmeans.png"))
plt.close()
print("Graphique de la méthode du coude sauvegardé dans graphs/elbow_method.png")

# Appliquer le clustering avec le nombre optimal de clusters (ex: 3)
# Déterminer le nombre optimal de clusters avec la méthode du score silhouette
silhouette_scores = []
best_k = 2
best_score = -1

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(df_scaled)
    score = silhouette_score(df_scaled, cluster_labels)
    silhouette_scores.append(score)
    if score > best_score:
        best_k = k
        best_score = score

k_optimal = best_k
print(f"Nombre optimal de clusters déterminé par silhouette : {k_optimal}, Score silhouette : {best_score:.2f}")

# Tracer le score silhouette pour visualisation
plt.figure(figsize=(8, 5))
plt.plot(K_range, silhouette_scores, marker='o', linestyle='-')
plt.xlabel("Nombre de clusters")
plt.ylabel("Score silhouette")
plt.title("Score silhouette pour déterminer K optimal")
plt.savefig(os.path.join(GRAPH_DIR, "silhouette_method_kmeans.png"))
plt.close()
print("Graphique de la méthode silhouette sauvegardé dans graphs/silhouette_method.png")
kmeans = KMeans(n_clusters=k_optimal, random_state=42, n_init=10)
df_cross_corr["Cluster"] = kmeans.fit_predict(df_scaled)

# Calculer le score silhouette
silhouette_avg = silhouette_score(df_scaled, df_cross_corr["Cluster"])
print(f"Score silhouette : {silhouette_avg:.2f}")

# Sauvegarder les résultats
df_cross_corr.to_csv(OUTPUT_CLUSTERING, sep=";", index=False, encoding="utf-8")
print(f"Résultats de clustering enregistrés dans {OUTPUT_CLUSTERING}")

# Visualisation des clusters
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_cross_corr, x="Décalage max (jours)", y="Corrélation max", hue="Cluster", palette="tab10")
plt.xlabel("Décalage max (jours)")
plt.ylabel("Corrélation max")
plt.title("Clustering des nappes en fonction du retard et de la corrélation aux précipitations")
plt.savefig(os.path.join(GRAPH_DIR, "clustering_kmeans_results.png"))
plt.close()
print("Graphique du clustering sauvegardé dans graphs/clustering_results.png")
