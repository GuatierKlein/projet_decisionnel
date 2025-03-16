import subprocess
import os

if not os.path.exists("graphs"):
    os.makedirs("graphs")

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists("data_all"):
    os.makedirs("data_all")

# Liste des scripts à exécuter dans l'ordre
scripts = [
    "geo_description", #description géo des données
    "fetch_data.py",  # Récupération des données via API
    "concat_data.py",  # Fusion des fichiers CSV
    "describe_missing_data.py",  # Analyse des valeurs manquantes
    "pivot_data.py",  # Transformation des données (mise en ligne par timestamp)
    "describe_missing_data_after_pivot",  # Analyse des valeurs manquantes
    "preprocess_data_all", #traitement des données
    "preprocess_data_one_year", #traitement des données
    "correlation matrix", # correlations entre chaque pizometre sur une années
    "analyse_pluvio",
    "analyse_puvio_clustering_knn",
    "analyse_pluvio_clustering_dbscan",
    "analyse_geo",
    "analyse_pluvio_clustering_and_soil"
]

for script in scripts:
    print(f"Exécution du script : {script}")
    try:
        subprocess.run(["python", script], check=True)
        print(f"✔ {script} exécuté avec succès.\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de {script} : {e}\n")
        break

print("✅ Tous les scripts ont été exécutés (sauf en cas d'erreur).")
