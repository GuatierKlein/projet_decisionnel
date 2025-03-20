import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
import seaborn as sns
from statsmodels.graphics.tsaplots import plot_acf
from scipy.signal import periodogram
from statsmodels.tsa.seasonal import STL

# Définition des chemins pour sauvegarder les résultats
INPUT_NAPPES = "data_all/nappes_concatenees.csv"
OUTPUT_DIR = "data_saiso/"
GRAPH_DIR = "graphs_saiso/"

# Création des dossiers si nécessaire
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(GRAPH_DIR, exist_ok=True)

# Charger les données
df_nappes = pd.read_csv(INPUT_NAPPES, sep=";", dtype=str)

# Garde uniquement les colonnes nécessaires
df_nappes = df_nappes[["code_bss", "date_mesure", "niveau_nappe_eau"]]

# Convertir les colonnes au bon format
df_nappes["niveau_nappe_eau"] = pd.to_numeric(df_nappes["niveau_nappe_eau"], errors='coerce')
df_nappes["date_mesure"] = pd.to_datetime(df_nappes["date_mesure"], errors='coerce')

df_nappes.set_index('date_mesure', inplace=True)
df_nappes['DayOfYear'] = df_nappes.index.dayofyear
df_nappes['Year'] = df_nappes.index.year

# décomposition 
for code_bss in df_nappes["code_bss"].unique():
    #evolution
    df_station = df_nappes[df_nappes["code_bss"] == code_bss]
    plt.figure()
    plt.plot(df_station.index, df_station['niveau_nappe_eau'], label="Niveau de la nappe", color='blue')
    graph_filename = os.path.join(GRAPH_DIR, f"{code_bss.replace('/', '_')}_evol.png")
    plt.savefig(graph_filename)

    #saisonalité
    result = seasonal_decompose(df_station['niveau_nappe_eau'], model='additive', period=365)

    fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
    result.observed.plot(ax=axes[0], title="Série originale")
    result.trend.plot(ax=axes[1], title="Tendance")
    result.seasonal.plot(ax=axes[2], title="Saisonnalité")
    result.resid.plot(ax=axes[3], title="Résidu")
    plt.tight_layout()
    
    graph_filename = os.path.join(GRAPH_DIR, f"{code_bss.replace('/', '_')}_saiso365.png")
    plt.savefig(graph_filename)

    plt.close()
    plot_acf(df_station['niveau_nappe_eau'], lags=1000)
    plt.title("Fonction d'Auto-corrélation (ACF)")
    graph_filename = os.path.join(GRAPH_DIR, f"{code_bss.replace('/', '_')}_ACF.png")
    plt.savefig(graph_filename)

    # Calcul du spectre de fréquence
    frequencies, power = periodogram(df_station['niveau_nappe_eau'], scaling='spectrum')

    plt.figure(figsize=(12, 5))
    plt.plot(1 / frequencies, power)  # Convertir fréquence en période (jours)
    plt.xlim(0, len(df_station) - 1)  # Limiter aux périodes intéressantes
    plt.xlabel("Période (jours)")
    plt.ylabel("Puissance du signal")
    plt.title("Analyse spectrale (Fourier)")
    graph_filename = os.path.join(GRAPH_DIR, f"{code_bss.replace('/', '_')}_fourrier.png")
    plt.savefig(graph_filename)








