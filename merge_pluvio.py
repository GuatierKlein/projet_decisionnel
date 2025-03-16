import pandas as pd
import os

# Définition des fichiers d'entrée et de sortie
INPUT_NAPPES = "data_all/nappes_concatenees.csv"
INPUT_STATIONS = "points_eau.csv"
INPUT_PLUVIO = "data_pluvio/precipitation_filtered.csv"
OUTPUT_FILE = "data_pluvio/merged_data.csv"

# Charger les nappes et les stations en mémoire
df_nappes = pd.read_csv(INPUT_NAPPES, sep=";", dtype=str)
df_nappes["date_mesure"] = pd.to_datetime(df_nappes["date_mesure"], errors='coerce').dt.strftime('%Y-%m-%d')
df_nappes["niveau_nappe_eau"] = pd.to_numeric(df_nappes["niveau_nappe_eau"], errors='coerce')

df_stations = pd.read_csv(INPUT_STATIONS, sep=";", dtype=str)

# Fusionner les nappes avec les stations
df_merged = df_nappes.merge(df_stations, left_on="code_bss", right_on="CODE_BSS", how="left")

# Garder uniquement les colonnes nécessaires avant fusion
df_merged = df_merged[["code_bss", "date_mesure", "niveau_nappe_eau", "Code Département"]]

# Assurer que Code Département est en str
df_merged["Code Département"] = df_merged["Code Département"].astype(str)

# Charger tous les chunks dans une liste
chunk_size = 500000  # Taille du chunk (ajuster si nécessaire)
chunks = pd.read_csv(INPUT_PLUVIO, sep=";", dtype=str, chunksize=chunk_size)
precip_data = []

for chunk in chunks:
    chunk["Date"] = pd.to_datetime(chunk["AAAAMMJJ"], format="%Y%m%d", errors='coerce').dt.strftime('%Y-%m-%d')
    chunk["RR"] = pd.to_numeric(chunk["RR"], errors='coerce')  # Ne pas remplacer NaN par 0 pour filtrer plus tard
    chunk = chunk[["Date", "RR", "Code Département"]]  # Garder uniquement les colonnes utiles
    chunk["Code Département"] = chunk["Code Département"].astype(str)
    precip_data.append(chunk)

# Concaténer tous les chunks en un seul DataFrame
df_precip = pd.concat(precip_data, ignore_index=True)

# Prendre la valeur maximale de RR par Date et Département
df_precip = df_precip.groupby(["Date", "Code Département"], as_index=False).agg({"RR": "max"})

# Vérification avant fusion
print("Taille de df_merged:", df_merged.shape)
print("Taille de df_precip après regroupement:", df_precip.shape)

# Fusionner l'ensemble des précipitations avec les nappes
df_final = df_merged.merge(df_precip, left_on=["date_mesure", "Code Département"], right_on=["Date", "Code Département"], how="left")

# Garder uniquement les colonnes finales
df_final = df_final[["date_mesure", "RR", "code_bss", "niveau_nappe_eau"]]

# Supprimer les lignes où RR est NaN
df_final = df_final.dropna(subset=["RR"])

# Sauvegarde du fichier final
df_final.to_csv(OUTPUT_FILE, sep=";", index=False, encoding="utf-8")

print(f"Fusion terminée et enregistrée dans {OUTPUT_FILE}")
