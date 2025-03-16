import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Définition des fichiers
OUTPUT = "data_pluvio/nappes_precipitations.csv"
INPUT_NAPPES = "data_all/nappes_concatenees.csv"
INPUT_PLUVIO = "data_all/precipitation_by_departement.csv"
INPUT_STATIONS = "points_eau.csv"
INPUT_SOIL = "data_fixed/sol_principal_per_bss.csv"
GRAPH_DIR = "graphs"

# Créer le dossier pour les graphiques s'il n'existe pas
os.makedirs(GRAPH_DIR, exist_ok=True)

# Charger les données des nappes
df_nappes = pd.read_csv(INPUT_NAPPES, sep=";", dtype=str)

# Garder uniquement les colonnes nécessaires
df_nappes = df_nappes[["code_bss", "timestamp_mesure", "date_mesure", "niveau_nappe_eau"]]

# Convertir les types
df_nappes["niveau_nappe_eau"] = pd.to_numeric(df_nappes["niveau_nappe_eau"], errors='coerce')

# Charger les données des stations
df_stations = pd.read_csv(INPUT_STATIONS, sep=";", dtype=str)

# Fusionner les nappes avec les stations pour récupérer les départements
df_nappes = df_nappes.merge(df_stations[["CODE_BSS", "Code Département"]], left_on="code_bss", right_on="CODE_BSS", how="left")

# Charger les données des précipitations
df_precip = pd.read_csv(INPUT_PLUVIO, sep=";", dtype=str)

df_precip["Date"] = pd.to_datetime(df_precip["Date"], errors='coerce')
df_precip["Précipitation Totale (mm)"] = pd.to_numeric(df_precip["Précipitation Totale (mm)"], errors='coerce')

# Convertir la date de mesure pour le groupement
df_nappes["date_mesure"] = pd.to_datetime(df_nappes["date_mesure"], errors='coerce')

# Grouper d'abord par jour, puis par station et département en faisant la moyenne
df_grouped = df_nappes.groupby(["date_mesure", "code_bss", "Code Département"], as_index=False).agg({"niveau_nappe_eau": "mean"})

# Fusionner avec les précipitations par département et date
df_final = df_grouped.merge(df_precip, left_on=["date_mesure", "Code Département"], right_on=["Date", "Code Département"], how="left")

# Supprimer les lignes sans précipitations associées
df_final = df_final.dropna(subset=["Précipitation Totale (mm)"])

# Supprimer la colonne en double "Date"
df_final.drop(columns=["Date"], inplace=True)

# Trier les données par station pour la sortie
df_final = df_final.sort_values(by=["code_bss", "date_mesure"])

# Sauvegarde du fichier final
df_final.to_csv(OUTPUT, sep=";", index=False, encoding="utf-8")

print(f"Données fusionnées, triées par station et enregistrées dans {OUTPUT}")

# Générer et sauvegarder un graphique pour chaque station
stations = df_final["code_bss"].unique()
for station_id in stations:
    df_station = df_final[df_final["code_bss"] == station_id]
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Tracer le niveau de la nappe
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Niveau nappe (m)", color="blue")
    ax1.plot(df_station["date_mesure"], df_station["niveau_nappe_eau"], color="blue", label="Niveau nappe")
    ax1.tick_params(axis="y", labelcolor="blue")
    
    # Ajouter un deuxième axe pour les précipitations
    ax2 = ax1.twinx()
    ax2.set_ylabel("Précipitation (mm)", color="red")
    ax2.bar(df_station["date_mesure"], df_station["Précipitation Totale (mm)"], color="red", alpha=0.5, label="Précipitations")
    ax2.tick_params(axis="y", labelcolor="red")
    
    fig.tight_layout()
    plt.title(f"Évolution du niveau de la nappe vs précipitations ({station_id})")
    
    # Sauvegarde du graphique
    graph_filename = os.path.join(GRAPH_DIR, f"{station_id.replace('/', '_')}_evolution.png")
    plt.savefig(graph_filename)
    plt.close()

    print(f"Graphique sauvegardé : {graph_filename}")

# Analyse de corrélation entre le niveau et les précipitations par station
correlation_results = []
for station_id in stations:
    df_station = df_final[df_final["code_bss"] == station_id]
    if len(df_station) > 1:  # Vérifier qu'il y a assez de données
        correlation = df_station["niveau_nappe_eau"].corr(df_station["Précipitation Totale (mm)"])
        correlation_results.append({"Station": station_id, "Corrélation": correlation})

# Convertir en DataFrame et sauvegarder
df_correlation = pd.DataFrame(correlation_results)
df_correlation.to_csv("data_pluvio/correlation_results.csv", sep=";", index=False, encoding="utf-8")
print("Analyse de corrélation terminée. Résultats sauvegardés dans data_pluvio/correlation_results.csv")

# Visualisation des corrélations
plt.figure(figsize=(12, 6))
sns.barplot(data=df_correlation, x="Station", y="Corrélation", palette="coolwarm")
plt.xticks(rotation=90)
plt.xlabel("Station")
plt.ylabel("Coefficient de Corrélation")
plt.title("Corrélation entre les précipitations et les niveaux de nappes par station")
plt.tight_layout()
plt.savefig(os.path.join(GRAPH_DIR, "correlation_precip.png"))
plt.close()

print("Graphique des corrélations sauvegardé dans graphs/correlation_precip.png")

# Cross-correlation: Décalage temporel entre pluie et montée des nappes
cross_correlation_results = []
max_lag = 365  # Tester jusqu'à 365 jours de décalage futur

for station_id in df_final["code_bss"].unique():
    df_station = df_final[df_final["code_bss"] == station_id]
    if len(df_station) > max_lag:
        precip_series = df_station["Précipitation Totale (mm)"].fillna(0).values
        nappe_series = df_station["niveau_nappe_eau"].fillna(0).values
        
        cross_corr = [np.corrcoef(nappe_series[:-i], precip_series[i:])[0, 1] if i > 0 else np.nan for i in range(1, max_lag + 1)]
        
        max_corr_lag = np.nanargmax(cross_corr) + 1  # +1 car on commence à 1 jour de décalage
        max_corr_value = np.nanmax(cross_corr)
        cross_correlation_results.append({"Station": station_id, "Décalage max (jours)": max_corr_lag, "Corrélation max": max_corr_value})

# Convertir en DataFrame et sauvegarder
df_cross_corr = pd.DataFrame(cross_correlation_results)
df_cross_corr.to_csv("data_pluvio/cross_correlation_results.csv", sep=";", index=False, encoding="utf-8")
print("Analyse de cross-corrélation terminée. Résultats sauvegardés dans data_pluvio/cross_correlation_results.csv")

# Visualisation des cross-corrélations
plt.figure(figsize=(12, 6))
sns.barplot(data=df_cross_corr, x="Station", y="Décalage max (jours)", hue="Corrélation max", palette="coolwarm")
plt.xticks(rotation=90)
plt.xlabel("Station")
plt.ylabel("Décalage temporel (jours)")
plt.title("Décalage optimal entre précipitations et niveaux de nappes par station (futur uniquement)")

# Ajouter des annotations pour voir la corrélation max
for index, row in df_cross_corr.iterrows():
    plt.text(index, row["Décalage max (jours)"], f"{row['Corrélation max']:.2f}", ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(GRAPH_DIR, "cross_correlation_precip.png"))
plt.close()

print("Graphique des cross-corrélations sauvegardé dans graphs/cross_correlation_precip.png")

# Charger les données des sols
df_soil = pd.read_csv(INPUT_SOIL, sep=";", dtype=str)
df_final = df_cross_corr.merge(df_soil, left_on="Station", right_on="CODE_BSS", how="left")

# Analyse de la moyenne du décalage par type de sol
soil_lag_analysis = df_final.groupby("main_soil_type")["Décalage max (jours)"].mean().reset_index()

# Visualisation
plt.figure(figsize=(12, 6))
sns.barplot(data=soil_lag_analysis, x="main_soil_type", y="Décalage max (jours)", palette="coolwarm")
plt.xticks(rotation=90)
plt.xlabel("Type de sol principal")
plt.ylabel("Décalage moyen (jours)")
plt.title("Moyenne du décalage max par type de sol")
plt.tight_layout()
plt.savefig(os.path.join(GRAPH_DIR, "soil_lag_analysis.png"))
plt.close()

print("Graphique de la moyenne du décalage max par type de sol sauvegardé dans graphs/soil_lag_analysis.png")
