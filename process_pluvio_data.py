import pandas as pd
import os
import glob

# Définition des fichiers et dossiers
INPUT_FOLDER = "data_meteo"  # Dossier contenant les fichiers CSV
OUTPUT_FILE = "data_pluvio/precipitation_filtered.csv"  # Fichier de sortie

# Récupérer tous les fichiers CSV dans le dossier
csv_files = glob.glob(os.path.join(INPUT_FOLDER, "*.csv"))

dataframes = []

for file in csv_files:
    # Extraire le numéro du département si disponible, sinon mettre "Unknown"
    filename = os.path.basename(file)
    department_number = filename[2:4] if filename.startswith("Q_") and filename[2:4].isdigit() else "Unknown"
    
    # Charger le fichier CSV en gardant uniquement les colonnes nécessaires
    df = pd.read_csv(file, sep=";", dtype=str, usecols=["AAAAMMJJ", "RR"])
    
    # Convertir AAAAMMJJ en format datetime
    df["Date"] = pd.to_datetime(df["AAAAMMJJ"], format="%Y%m%d", errors='coerce')
    
    # Ajouter la colonne du département
    df["Code Département"] = department_number
    
    # Filtrer les dates après 2000
    df = df[df["Date"] >= "2001-01-01"]
    
    # Ajouter au DataFrame final
    dataframes.append(df)

# Concaténer tous les fichiers en un seul DataFrame
df_final = pd.concat(dataframes, ignore_index=True)

# Sauvegarde du fichier final
df_final.to_csv(OUTPUT_FILE, sep=";", index=False, encoding="utf-8")

print(f"Données filtrées enregistrées dans {OUTPUT_FILE}")