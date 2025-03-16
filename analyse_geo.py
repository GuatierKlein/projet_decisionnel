import pandas as pd
import matplotlib.pyplot as plt
import os

# Chemins des fichiers CSV
CSV_SOIL = "data_fixed/sol_principal_per_bss.csv"
CSV_POINTS_EAU = "points_eau.csv"
CSV_NAPPES = "data_all/nappes_concatenees.csv"
GRAPH_DIR = "graphs"
GRAPH_FILE = os.path.join(GRAPH_DIR, "niveau_nappe_par_sol.png")

# Créer le dossier pour les graphiques s'il n'existe pas
os.makedirs(GRAPH_DIR, exist_ok=True)

# Charger les données
print("📥 Chargement des fichiers...")
df_soil = pd.read_csv(CSV_SOIL, sep=";")
df_points_eau = pd.read_csv(CSV_POINTS_EAU, sep=";")
df_nappes = pd.read_csv(CSV_NAPPES, sep=";")

# Fusionner les fichiers sur CODE_BSS
df_merged = df_nappes.merge(df_points_eau, left_on="code_bss", right_on="CODE_BSS", how="left")
df_merged = df_merged.merge(df_soil, on="CODE_BSS", how="left")

# Étude du niveau moyen par type de sol principal
df_analysis = df_merged.groupby("main_soil_type")["niveau_nappe_eau"].mean().reset_index()
df_analysis = df_analysis.dropna()

# Affichage des résultats
print("📊 Niveau moyen par type de sol principal :")
print(df_analysis)

# Visualisation et sauvegarde du graphique
plt.figure(figsize=(12, 6))
plt.barh(df_analysis["main_soil_type"], df_analysis["niveau_nappe_eau"], color="skyblue")
plt.xlabel("Niveau moyen de la nappe (m)")
plt.ylabel("Type de sol principal")
plt.title("Niveau moyen de la nappe par type de sol principal")
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.savefig(GRAPH_FILE)
plt.close()

print(f"✅ Graphique sauvegardé sous {GRAPH_FILE}")