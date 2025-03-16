import os
import pandas as pd

# Définition des paramètres
INPUT_FILE = "data_all/nappes_concatenees.csv"  # Fichier d'entrée
OUTPUT_FILE = "data_all/nappes_transforme.csv"  # Fichier de sortie directement dans data_all

# Charger les données
df = pd.read_csv(INPUT_FILE, sep=";", dtype=str)

# Convertir la colonne timestamp_mesure en datetime
if "date_mesure" in df.columns:
    df["date_mesure"] = pd.to_datetime(df["date_mesure"], format="%Y-%m-%d", errors="coerce")
else:
    raise ValueError("La colonne 'date_mesure' est absente du fichier CSV.")

# Convertir les colonnes numériques
df["niveau_nappe_eau"] = pd.to_numeric(df["niveau_nappe_eau"], errors='coerce')

print(df)

# Regrouper les données par jour et prendre la moyenne des valeurs si plusieurs par jour
df["date_mesure"] = df["date_mesure"].dt.date  # Extraire uniquement la date
df_daily = df.groupby(["date_mesure", "code_bss"]).mean().reset_index() #agreg sur moyenne des niveaux

# Pivot des données pour avoir une colonne par piézomètre
df_pivot = df_daily.pivot(index="date_mesure", columns="code_bss", values="niveau_nappe_eau")

# Réinitialiser l'index
df_pivot.reset_index(inplace=True)

# Sauvegarde des données transformées
df_pivot.to_csv(OUTPUT_FILE, sep=";", index=False, encoding="utf-8")

print(f"Données transformées enregistrées dans {OUTPUT_FILE}")