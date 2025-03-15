import requests
import pandas as pd
import os
import re

# Définition des paramètres
INPUT_CSV = "points_eau.csv"  # Remplacez par le chemin de votre fichier CSV
OUTPUT_DIR = "data"  # Dossier de sortie des fichiers à la racine du projet
API_URL = "https://hubeau.eaufrance.fr/api/v1/niveaux_nappes/chroniques.csv"

# Vérifier et créer le dossier de sortie si nécessaire
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Charger le fichier CSV d'entrée
df = pd.read_csv(INPUT_CSV, sep=';', dtype=str)  # Charger toutes les colonnes en tant que chaînes

# Vérifier si la colonne 'code_bss' existe
if "CODE_BSS" not in df.columns:
    raise ValueError("Le fichier CSV d'entrée ne contient pas la colonne 'code_bss'")

# Fonction pour nettoyer les noms de fichiers
def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', filename)

# Boucle sur chaque ligne du CSV
for index, row in df.iterrows():
    code_bss = row["CODE_BSS"]
    if pd.isna(code_bss):
        continue  # Passer les valeurs nulles
    
    safe_code_bss = sanitize_filename(code_bss)  # Nettoyer le nom du fichier
    output_file = os.path.join(OUTPUT_DIR, f"{safe_code_bss}.csv")
    
    # Construire les paramètres de la requête
    params = {
        "size": 20000,
        "code_bss": code_bss
    }
    
    # Effectuer la requête HTTP
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Déclenche une erreur HTTP pour les statuts 4xx et 5xx
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"Données sauvegardées pour {code_bss} dans {output_file}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête pour le code_bss {code_bss}: {e}")
        print(f"Requête envoyée: {response.url if 'response' in locals() else 'Non disponible'}")

print("Traitement terminé.")