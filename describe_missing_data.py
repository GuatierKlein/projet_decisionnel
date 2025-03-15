import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Définition des paramètres
INPUT_FILE = "data_all/nappes_concatenees.csv"  # Fichier concaténé

# Charger les données
df = pd.read_csv(INPUT_FILE, sep=";", dtype=str)

# Convertir les colonnes numériques
numeric_cols = ["niveau_nappe_eau", "profondeur_nappe"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')  # Convertir en nombre, forcer les erreurs en NaN

# Analyse des valeurs manquantes
missing_counts = df.isna().sum()
missing_percent = (missing_counts / len(df)) * 100

# Créer un DataFrame récapitulatif
df_missing = pd.DataFrame({
    "Colonne": df.columns,
    "Valeurs Manquantes": missing_counts.values,
    "% Manquant": missing_percent.values
})

print(df_missing)  # Affiche le tableau des valeurs manquantes dans la console
df_missing.to_csv("data_all/missing_data_analysis.csv", sep=";", index=False)  # Sauvegarde l'analyse dans un CSV


# Visualisation des valeurs manquantes
plt.figure(figsize=(12, 6))
sns.heatmap(df.isna(), cbar=False, cmap="viridis", yticklabels=False)
plt.title("Carte des valeurs manquantes")
plt.show()

# Afficher les colonnes les plus touchées
plt.figure(figsize=(10, 5))
sns.barplot(y=df_missing["Colonne"], x=df_missing["% Manquant"], palette="coolwarm")
plt.xlabel("% de valeurs manquantes")
plt.ylabel("Colonnes")
plt.title("Pourcentage de valeurs manquantes par colonne")
plt.show()

print("Analyse des données manquantes terminée.")
