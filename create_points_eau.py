import pandas as pd

# Charger les données depuis un fichier CSV
df = pd.read_csv("stations_ades.csv", delimiter=";")

# Renommer et sélectionner les colonnes pertinentes
transformed_df = df.rename(columns={
    "code_bss": "CODE_BSS",
    "bss_id": "BSS_ID",
    "x": "LONGITUDE",
    "y": "LATITUDE",
    "code_commune_insee": "CODE_INSEE_COMMUNE",
    "code_departement": "CODE_DEPARTEMENT"
})

# Filtrer pour ne garder que les départements de métropole
metropolitan_departments = [str(i).zfill(2) for i in range(1, 96)]  # Départements 01 à 95
transformed_df = transformed_df[transformed_df["CODE_DEPARTEMENT"].astype(str).str.zfill(2).isin(metropolitan_departments)]

# Sélectionner l'ordre final des colonnes
transformed_df = transformed_df[[
    "CODE_BSS", "BSS_ID", "LONGITUDE", "LATITUDE", "CODE_INSEE_COMMUNE"
]]

# Sauvegarder le fichier transformé
transformed_df.to_csv("points_eau.csv", sep=";", index=False)

# Afficher un aperçu des premières lignes
print(transformed_df.head())