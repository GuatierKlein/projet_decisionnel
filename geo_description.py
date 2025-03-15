import pandas as pd
import requests

# Définition du fichier d'entrée
INPUT_FILE = "points_eau.csv"  # Nom du fichier d'entrée

# Charger les données
print("Chargement des données...")
df = pd.read_csv(INPUT_FILE, sep=";", dtype=str)

# API pour récupérer les départements via le code INSEE de la commune
API_URL = "https://geo.api.gouv.fr/communes/"

def get_departement(code_insee):
    try:
        response = requests.get(f"{API_URL}{code_insee}?fields=nom,codeDepartement")
        if response.status_code == 200:
            data = response.json()
            return data["codeDepartement"], data["nom"]
        else:
            return None, None
    except Exception as e:
        print(f"Erreur lors de la récupération du département pour {code_insee}: {e}")
        return None, None

# Ajouter les colonnes Département et Nom Département directement dans le fichier d'entrée
df["Code Département"], df["Nom Département"] = zip(*df["CODE_INSEE_COMMUNE"].apply(get_departement))

# Sauvegarde du fichier avec les nouvelles colonnes
df.to_csv(INPUT_FILE, sep=";", index=False, encoding="utf-8")

print(f"Les colonnes 'Code Département' et 'Nom Département' ont été ajoutées au fichier {INPUT_FILE}")