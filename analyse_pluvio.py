import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.signal import correlate, find_peaks

# Définition des fichiers
INPUT_MERGED = "data_pluvio/merged_data.csv"  # Remplace toutes les sources par le fichier fusionné
GRAPH_DIR = "graphs"
DO_GRAPHS = False
RESULTS_CSV = "data_pluvio/best_cross_correlation.csv"

# Créer le dossier pour les graphiques s'il n'existe pas
os.makedirs(GRAPH_DIR, exist_ok=True)

# Charger les données fusionnées
df_final = pd.read_csv(INPUT_MERGED, sep=";", dtype=str)

df_final["date_mesure"] = pd.to_datetime(df_final["date_mesure"], errors='coerce')
df_final["RR"] = pd.to_numeric(df_final["RR"], errors='coerce')
df_final["niveau_nappe_eau"] = pd.to_numeric(df_final["niveau_nappe_eau"], errors='coerce')

# Générer et sauvegarder un graphique pour chaque station
if(DO_GRAPHS):
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
        ax2.bar(df_station["date_mesure"], df_station["RR"], color="red", alpha=0.5, label="Précipitations")
        ax2.tick_params(axis="y", labelcolor="red")
        
        fig.tight_layout()
        plt.title(f"Évolution du niveau de la nappe vs précipitations ({station_id})")
        
        # Sauvegarde du graphique
        graph_filename = os.path.join(GRAPH_DIR, f"{station_id.replace('/', '_')}_evolution.png")
        plt.savefig(graph_filename)
        plt.close()

        print(f"Graphique sauvegardé : {graph_filename}")

# Cross-correlation: Décalage temporel entre pluie et montée des nappes
cross_correlation_results = []
max_lag = 400  # Tester jusqu'à 400 jours de décalage futur

for station_id in df_final["code_bss"].unique():
    df_station = df_final[df_final["code_bss"] == station_id]
    if len(df_station) > max_lag:
        precip_series = df_station["RR"].fillna(0).values
        nappe_series = df_station["niveau_nappe_eau"].fillna(0).values

        #,oramlisation
        precip_series = (precip_series - np.mean(precip_series)) / np.std(precip_series)
        nappe_series = (nappe_series - np.mean(nappe_series)) / np.std(nappe_series)
        
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

# Liste pour stocker les résultats
results = []

# Calculer la meilleure cross-corrélation sur 400 jours parmi les pics des données
for station_id in df_final["code_bss"].unique():
    df_station = df_final[df_final["code_bss"] == station_id].dropna()
    
    if len(df_station) > 400:
        rr_series = df_station["RR"].values
        nappe_series = df_station["niveau_nappe_eau"].values
        
        # Normalisation des séries
        rr_mean, rr_std = np.mean(rr_series), np.std(rr_series)
        nappe_mean, nappe_std = np.mean(nappe_series), np.std(nappe_series)
        
        rr_series = (rr_series - rr_mean) / (rr_std if rr_std != 0 else 1e-8)
        nappe_series = (nappe_series - nappe_mean) / (nappe_std if nappe_std != 0 else 1e-8)
        
        # Détection des pics significatifs dans les données RR
        rr_peaks, _ = find_peaks(df_station["RR"], height=np.mean(df_station["RR"]) + np.std(df_station["RR"]))
        
        best_lag = None
        best_corr = -np.inf
        
        for peak in rr_peaks:
            if peak + 400 < len(nappe_series):
                rr_window = rr_series[peak:peak + 400]
                nappe_window = nappe_series[peak:peak + 400]
                
                cross_corr = correlate(nappe_window, rr_window, mode='full')[len(rr_window)-1:]
                cross_corr /= (np.linalg.norm(nappe_window) * np.linalg.norm(rr_window))
                lags = np.arange(0, len(rr_window))
                
                max_corr = np.max(cross_corr)
                if max_corr > best_corr:
                    best_corr = max_corr
                    best_lag = lags[np.argmax(cross_corr)]
        
        if best_lag is not None:
            results.append([station_id, best_lag, best_corr])

# Sauvegarder les résultats dans un fichier CSV
df_results = pd.DataFrame(results, columns=["station_id", "best_lag", "best_corr"])
df_results.to_csv(RESULTS_CSV, sep=";", index=False, encoding="utf-8")
print(f"Résultats sauvegardés dans {RESULTS_CSV}")

# Tracer un bar chart des meilleurs décalages et corrélations
plt.figure(figsize=(12, 6))
ax = sns.barplot(data=df_results, x="station_id", y="best_lag", palette="viridis")
plt.xticks(rotation=90)
plt.xlabel("Station ID")
plt.ylabel("Meilleur Décalage (jours)")
plt.title("Meilleur Décalage en Jours pour Chaque Station")

# Ajouter des annotations pour voir la corrélation max
for index, row in df_results.iterrows():
    ax.text(index, row["best_lag"] + 2, f"{row['best_corr']:.2f}", ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

plt.tight_layout()
plt.savefig(os.path.join(GRAPH_DIR, "best_lag_bar_chart.png"))
plt.close()

print("Graphique des meilleurs décalages enregistré avec annotations.")
