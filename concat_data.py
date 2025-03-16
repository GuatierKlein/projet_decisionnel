import os
import pandas as pd

# Définition des paramètres
INPUT_DIR = "data"  # Dossier contenant les fichiers CSV
OUTPUT_DIR = "data_all"  # Dossier de sortie
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "nappes_concatenees.csv")

# Vérifier et créer le dossier de sortie si nécessaire
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Récupérer tous les fichiers CSV dans le dossier INPUT_DIR
csv_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".csv")]

# Initialiser une liste pour stocker les DataFrames
df_list = []

# Charger et concaténer les fichiers
for file in csv_files:
    file_path = os.path.join(INPUT_DIR, file)
    try:
        df = pd.read_csv(file_path, sep=";", dtype=str)  # Charger en tant que chaînes pour éviter les erreurs
        df = df[["code_bss", "date_mesure", "niveau_nappe_eau"]]  # Ne garder que les colonnes spécifiées
        df_list.append(df)
        print(f"Fichier chargé : {file}")
    except Exception as e: #en cas d'erreur, on abandonne la lecture du csv en quetion
        print(f"Erreur lors de la lecture de {file}: {e}")

# Concaténer toutes les données en un seul DataFrame
if df_list:
    df_all = pd.concat(df_list, ignore_index=True)
    
    # Sauvegarder le fichier final
    df_all.to_csv(OUTPUT_FILE, sep=";", index=False, encoding="utf-8")
    print(f"Données concaténées enregistrées dans {OUTPUT_FILE}")
else:
    print("Aucun fichier CSV valide trouvé pour la concaténation.")
