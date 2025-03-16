import subprocess
import os

download_data = False

if not os.path.exists("graphs"):
    os.makedirs("graphs")

if not os.path.exists("data"):
    download_data = True
    os.makedirs("data")

if not os.path.exists("data_all"):
    os.makedirs("data_all")

# Liste des scripts à exécuter dans l'ordre
scripts = [
    "geo_description.py", #description géo des données
    "fetch_data.py",  # Récupération des données via API
    "concat_data.py",  # Fusion des fichiers CSV
    "describe_missing_data.py",  # Analyse des valeurs manquantes
    "pivot_data.py",  # Transformation des données (mise en ligne par timestamp)
    "describe_missing_data_after_pivot.py",  # Analyse des valeurs manquantes
    "preprocess_data_all.py", #traitement des données
    "preprocess_data_one_year.py", #traitement des données
    "correlation matrix.py", # correlations entre chaque pizometre sur une années
    "analyse_pluvio.py",
    "analyse_pluvio_clustering_knn.py",
    "analyse_pluvio_clustering_dbscan.py",
    "analyse_geo.py",
    "analyse_pluvio_clustering_and_soil.py"
]

for script in scripts:
    print(f"Exécution du script : {script}")

    if(script == "fetch_data.py" and not download_data):
        continue

    try:
        subprocess.run(["python", script], check=True)
        print(f"✔ {script} exécuté avec succès.\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de {script} : {e}\n")
        break

print("✅ Tous les scripts ont été exécutés (sauf en cas d'erreur).")
