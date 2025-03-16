import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Définition des paramètres
INPUT_FILE = "data_all/nappes_transforme.csv"  # Fichier d'entrée
OUTPUT_FILE = "data_all/nappes_preprocessed.csv"  # Fichier de sortie après traitement
OUTPUT_GRAPH = "graphs/level_over_time.png"
OUTPUT_GRAPH_NO_MISSING = "graphs/level_over_time_no_missing.png"

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

# Compter les valeurs manquantes avant interpolation
missing_counts_before = df.isna().sum()

# Visualisation des tendances pour tous les piézomètres avant traitement des données manquantes
plt.figure(figsize=(25, 8))  # Augmentation de la taille du graphique
colors = plt.cm.get_cmap("tab20", len(df.columns[1:]))

for i, col in enumerate(df.columns[1:]):  # Ignorer date_mesure
    plt.plot(df["date_mesure"], df[col], linestyle="-", alpha=0.7, label=col, color=colors(i % 20))

plt.xlabel("Date")
plt.ylabel("Niveau nappe")
plt.title("Évolution du niveau de la nappe pour tous les piézomètres avant traitement des données manquantes")
plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1), fontsize="small", frameon=True, ncol=3)
plt.grid()
plt.savefig(OUTPUT_GRAPH, dpi=300, bbox_inches='tight')
plt.show()

# Gestion des valeurs manquantes (Interpolation temporelle)
df.set_index("date_mesure", inplace=True)
df = df.interpolate(method="spline", order=3)

# Compter les valeurs interpolées après le traitement
missing_counts_after = df.isna().sum()
interpolated_counts = missing_counts_before - missing_counts_after

# Affichage du nombre de valeurs interpolées par colonne
print("Nombre de valeurs interpolées par colonne :")
print(interpolated_counts)

# Ajout de variables temporelles
df["mois"] = df.index.month
df["année"] = df.index.year
df["jour_annee"] = df.index.dayofyear

# Réinitialiser l'index
df.reset_index(inplace=True)

# Sauvegarde des données prétraitées
df.to_csv(OUTPUT_FILE, sep=";", index=False, encoding="utf-8")

print(f"Données prétraitées enregistrées dans {OUTPUT_FILE}")

# Visualisation des tendances pour tous les piézomètres après traitement des données manquantes
plt.figure(figsize=(25, 8))
colors = plt.cm.get_cmap("tab20", len(df.columns[1:]))

for i, col in enumerate(df.columns[1:]):
    plt.plot(df["date_mesure"], df[col], linestyle="-", alpha=0.7, label=col, color=colors(i % 20))

plt.xlabel("Date")
plt.ylabel("Niveau nappe")
plt.title("Évolution du niveau de la nappe pour tous les piézomètres après traitement des données manquantes")
plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1), fontsize="small", frameon=True, ncol=3)
plt.grid()
plt.savefig(OUTPUT_GRAPH_NO_MISSING, dpi=300, bbox_inches='tight')
plt.show()
