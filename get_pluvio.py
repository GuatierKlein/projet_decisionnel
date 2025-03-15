import pandas as pd
import requests

# Définition des fichiers
INPUT_FILE = "points_eau.csv"  # Fichier contenant les départements
OUTPUT_FILE = "data_all/precipitation_by_departement.csv"  # Fichier de sortie

# Charger les départements à partir du fichier existant
df = pd.read_csv(INPUT_FILE, sep=";", dtype=str)
departements = df["Code Département"].dropna().unique()  # Supprimer les NaN et obtenir une liste unique

# API pour récupérer les précipitations journalières
API_URL = "https://public.opendatasoft.com/api/records/1.0/search/?dataset=donnees-synop-essentielles-omm&q=&rows=10000&facet=departement&facet=date&fields=rr1,date"

def get_precipitation_data(departement):
    """ Récupère la somme des précipitations journalières pour un département """
    try:
        response = requests.get(f"{API_URL}&refine.departement={departement}")
        if response.status_code == 200:
            data = response.json().get("records", [])
            daily_precip = {}
            for record in data:
                print (record)
                date = record["fields"].get("date", "").split("T")[0]  # Extraire uniquement la date
                precip = float(record["fields"].get("rr1", 0))
                daily_precip[date] = daily_precip.get(date, 0) + precip  # Somme des précipitations
            print(f"Précipitations récupérées pour {departement}: {daily_precip}")
            return daily_precip
        else:
            print(f"Aucune donnée reçue pour {departement}")
            return {}
    except Exception as e:
        print(f"Erreur lors de la récupération des précipitations pour {departement}: {e}")
        return {}

# Récupérer les précipitations pour chaque département
data = []
for dep in departements:
    daily_precip = get_precipitation_data(dep)
    for date, precip in daily_precip.items():
        data.append({"Date": date, "Code Département": dep, "Précipitation Totale (mm)": precip})

# Création du DataFrame
precip_df = pd.DataFrame(data)

# Sauvegarde des données
precip_df.to_csv(OUTPUT_FILE, sep=";", index=False, encoding="utf-8")

print(f"Données de précipitation journalières enregistrées dans {OUTPUT_FILE}")
