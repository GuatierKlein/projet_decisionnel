import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Définition des paramètres
INPUT_FILE = "data_all/nappes_transforme.csv"  # Fichier d'entrée
OUTPUT_FILE = "data_all/nappes_preprocessed_agg.csv"
OUTPUT_FILE_SMOOTHED = "data_all/nappes_preprocessed_agg_smoothed.csv"
OUTPUT_GRAPH = "graphs/average_level_over_one_year_normalized.png"
OUTPUT_GRAPH_SMOOTHED = "graphs/average_level_over_one_year_normalized_smoothed.png"

# Charger les données
df = pd.read_csv(INPUT_FILE, sep=";", dtype=str)

# Convertir la colonne timestamp_mesure en datetime
if "date_mesure" in df.columns:
    df["date_mesure"] = pd.to_datetime(df["date_mesure"], errors="coerce")
else:
    raise ValueError("La colonne 'date_mesure' est absente du fichier CSV.")

# Convertir les colonnes numériques
for col in df.columns:
    if col != "date_mesure":
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Extraire le jour de l'année
df["jour_annee"] = df["date_mesure"].dt.dayofyear

# Calculer la moyenne par jour de l'année et par piézomètre
df_annual = df.groupby(["jour_annee"]).mean()

# normalisation des données 
df_annual = (df_annual.iloc[:, 1:] - df_annual.iloc[:, 1:].mean()) / df_annual.iloc[:, 1:].std()

# Réinitialiser l'index
df_annual.reset_index(inplace=True)

# Sauvegarde des données prétraitées
df_annual.to_csv(OUTPUT_FILE, sep=";", index=False, encoding="utf-8")

print(f"Données moyennées sur un an enregistrées dans {OUTPUT_FILE}")

# Visualisation des tendances moyennes annuelles
plt.figure(figsize=(25, 8))
colors = plt.cm.get_cmap("tab20", len(df.columns[1:]))

for i, col in enumerate(df.columns[1:]):
    if col != "jour_annee":  # Ignorer la colonne du jour de l'année
        plt.plot(df_annual["jour_annee"], df_annual[col], linestyle="-", alpha=0.7, label=col, color=colors(i % 20))

plt.xlabel("Jour de l'année")
plt.ylabel("Niveau nappe (m)")
plt.title("Évolution moyenne du niveau de la nappe sur une année pour chaque piézomètre")
plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1), fontsize="small", frameon=True, ncol=3)
plt.grid()
plt.savefig(OUTPUT_GRAPH, dpi=300, bbox_inches='tight')
plt.show()


# lissage des données avec une moyenne glissante 
df_smooth = df_annual.copy()
window_size = 14  # Fenêtre de lissage 

for col in df_annual.columns[1:]:  # Exclure "jour_annee"
    df_smooth[col] = df_annual[col].rolling(window=window_size, center=True).mean()

# Sauvegarde des données prétraitées
df_smooth.to_csv(OUTPUT_FILE_SMOOTHED, sep=";", index=False, encoding="utf-8")

# Visualisation des tendances moyennes annuelles
plt.figure(figsize=(25, 8))
colors = plt.cm.get_cmap("tab20", len(df.columns[1:]))

for i, col in enumerate(df.columns[1:]):
    if col != "jour_annee":  # Ignorer la colonne du jour de l'année
        plt.plot(df_smooth["jour_annee"], df_smooth[col], linestyle="-", alpha=0.7, label=col, color=colors(i % 20))

plt.xlabel("Jour de l'année")
plt.ylabel("Niveau nappe (m)")
plt.title("Évolution moyenne lissée du niveau de la nappe sur une année pour chaque piézomètre")
plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1), fontsize="small", frameon=True, ncol=3)
plt.grid()
plt.savefig(OUTPUT_GRAPH_SMOOTHED, dpi=300, bbox_inches='tight')
plt.show()

