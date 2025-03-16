import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Définition des paramètres
# INPUT_FILE = "data_all/nappes_transforme.csv"  # Fichier transformé

# # Charger les données
# df = pd.read_csv(INPUT_FILE, sep=";", dtype=str)


# # Convertir les colonnes numériques
# for col in df.columns:
#     if col != "timestamp_mesure":
#         df[col] = pd.to_numeric(df[col], errors='coerce')

# # Analyse des valeurs manquantes
# missing_counts = df.isna().sum()
# missing_percent = (missing_counts / len(df)) * 100

# df_missing = pd.DataFrame({
#     "Colonne": df.columns,
#     "Valeurs Manquantes": missing_counts.values,
#     "% Manquant": missing_percent.values
# })

# Affichage des résultats
# print(df_missing)  # Affiche le tableau des valeurs manquantes dans la console
# df_missing.to_csv("data_all/missing_data_analysis_after_pivot.csv", sep=";", index=False)
# print("Analyse des données manquantes enregistrée dans 'data_all/missing_data_analysis.csv'")

# # Visualisation des valeurs manquantes
# plt.figure(figsize=(12, 6))
# sns.heatmap(df.isna(), cbar=False, cmap="viridis", yticklabels=False)
# plt.title("Carte des valeurs manquantes par colonne")
# plt.show()

# # Afficher les colonnes les plus touchées
# plt.figure(figsize=(10, 5))
# sns.barplot(y=df_missing["Colonne"], x=df_missing["% Manquant"], palette="coolwarm")
# plt.xlabel("% de valeurs manquantes")
# plt.ylabel("Colonnes")
# plt.title("Pourcentage de valeurs manquantes par colonne")
# plt.show()

# # Graphe du nombre de valeurs manquantes en fonction de la date
# df_missing_by_date = df.set_index("timestamp_mesure").isna().sum(axis=1)

# df_missing_by_date = df_missing_by_date.resample("M").sum()  # Regroupement mensuel

# plt.figure(figsize=(12, 6))
# plt.plot(df_missing_by_date.index, df_missing_by_date.values, marker="o", linestyle="-", color="red")
# plt.xlabel("Date")
# plt.ylabel("Nombre de valeurs manquantes")
# plt.title("Évolution du nombre de valeurs manquantes par date")
# plt.grid()
# plt.show()

# print("Analyse des données manquantes terminée.")