import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Définition des paramètres
INPUT_FILE = "data_all/nappes_preprocessed_agg_smoothed.csv"  # Fichier des données agrégées
OUTPUT_FILE = "graphs/correlation_matrix.png"  # Fichier de sortie pour la matrice de corrélation

# Charger les données
if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"Le fichier {INPUT_FILE} est introuvable.")

df = pd.read_csv(INPUT_FILE, sep=";", dtype=float)

# Vérifier si les données sont bien chargées
if df.empty:
    raise ValueError("Le fichier chargé est vide.")

# Calcul de la matrice de corrélation
corr_matrix = df.iloc[:, 1:].corr()  # Exclure 'jour_annee' si présent

# Visualisation de la matrice de corrélation
plt.figure(figsize=(12, 8))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Matrice de corrélation des niveaux des nappes phréatiques")

# Sauvegarder la figure
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
plt.show()

print(f"Matrice de corrélation enregistrée sous {OUTPUT_FILE}")