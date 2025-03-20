import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf
import seaborn as sns
from scipy.signal import periodogram, find_peaks

# Définition des chemins pour sauvegarder les résultats
INPUT_NAPPES = "data_all/nappes_concatenees.csv"
OUTPUT_DIR = "data_saiso/"
GRAPH_DIR = "graphs_saiso/"

# Définir les plages de regroupement (ex: ±10% autour de chaque valeur)
expected_cycles = {
    "Hebdomadaire": (7 - 2, 7 + 2),  # 7 jours ± 2 jours
    "Mensuel": (30 - 5, 30 + 5),     # 30 jours ± 5 jours
    "Saisonnalité Courte": (180 - 20, 180 + 20),  # 180 jours ± 20 jours
    "Annuel": (365 - 30, 365 + 30),   # 365 jours ± 30 jours
    "Cycle ENSO": (730 - 100, 730 + 100),   # 2 ans ± 100 jours
    "Cycle Long": (3650 - 500, 3650 + 500)  # 10 ans ± 500 jours
}

def group_peaks(peaks):
    grouped_peaks = {cycle: [] for cycle in expected_cycles}

    for peak in peaks:
        for cycle_name, (low, high) in expected_cycles.items():
            if low <= peak <= high:
                grouped_peaks[cycle_name].append(peak)
    
    # Convertir en moyenne des pics détectés pour chaque catégorie
    grouped_means = {cycle: np.mean(vals) if vals else None for cycle, vals in grouped_peaks.items()}
    
    return grouped_means

def binary_vector(peaks):
    binary_representation = {cycle: 0 for cycle in expected_cycles}
    
    for peak in peaks:
        for cycle_name, (low, high) in expected_cycles.items():
            if low <= peak <= high:
                binary_representation[cycle_name] = 1  # Marquer la catégorie comme détectée
    
    return binary_representation

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

series_peaks = {}

# décomposition 
for code_bss in df_nappes["code_bss"].unique():
    #evolution
    df_station = df_nappes[df_nappes["code_bss"] == code_bss]
    plt.figure()
    plt.plot(df_station.index, df_station['niveau_nappe_eau'], label="Niveau de la nappe", color='blue')
    graph_filename = os.path.join(GRAPH_DIR, f"{code_bss.replace('/', '_')}_evol.png")
    plt.savefig(graph_filename)
    # plt.show()
    plt.close()

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
    # plt.show()
    plt.close()

    # Calcul du spectre de fréquence
    frequencies, power = periodogram(df_station['niveau_nappe_eau'], scaling='spectrum')

    # Conversion des fréquences en périodes (jours), éviter division par zéro
    periods = np.where(frequencies == 0, np.nan, 1 / frequencies)

    # Identifier les pics significatifs dans la courbe de Fourier
    peaks, _ = find_peaks(power, height=np.mean(power) + 2 * np.std(power))  # Seuil de détection
    # garder les 5 plus grands pics
    # peaks = peaks[np.argsort(power[peaks])[-10:]]
    series_peaks[code_bss] = periods[peaks]

    # Extraire les périodes correspondantes aux pics
    significant_periods = periods[peaks]
    significant_powers = power[peaks]

    # Tracé du spectre avec identification des pics
    plt.figure(figsize=(12, 5))
    plt.plot(periods, power, label="Spectre de Fourier")
    plt.scatter(significant_periods, significant_powers, color='red', label="Pics détectés", marker='o')

    # Mettre en évidence les pics détectés
    for i, txt in enumerate(significant_periods):
        plt.annotate(f"{txt:.0f} jours", (significant_periods[i], significant_powers[i]), fontsize=10, ha='right')

    plt.xlim(0, 4000)  # Limite à 10 ans
    plt.xlabel("Période (jours)")
    plt.ylabel("Puissance du signal")
    plt.title("Analyse spectrale - Détection des cycles hydrologiques")
    plt.legend()
    plt.grid()
    graph_filename = os.path.join(GRAPH_DIR, f"{code_bss.replace('/', '_')}_fourrier.png")
    plt.savefig(graph_filename)
    # plt.show()
    plt.close()

# création des vecteurs binaires
binary_vectors = {region: binary_vector(peaks) for region, peaks in series_peaks.items()}
df_binary = pd.DataFrame(binary_vectors).T

# Afficher les résultats sous forme de heatmap
plt.figure(figsize=(10, 5))
sns.heatmap(df_binary, annot=True, cmap="coolwarm", linewidths=0.5, cbar=False)
plt.title("Présence des pics par catégorie pour chaque série hydrologique")
plt.xlabel("Catégorie de Cycle")
plt.ylabel("Séries (Régions)")
graph_filename = os.path.join(GRAPH_DIR, f"pics_heatmap.png")
plt.savefig(graph_filename)

# Ajouter le nom de la station au DataFrame
df_binary.insert(0, "code_bss", df_binary.index)
df_binary.to_csv(OUTPUT_DIR + "pics_binary_vector.csv", sep=";", index=False, encoding="utf-8")