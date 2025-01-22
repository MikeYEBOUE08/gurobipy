import json
import pandas as pd
import numpy as np
import gurobipy as gp
from gurobipy import GRB

# Charger les données du fichier JSON
try:
    with open("data/data/portfolio-example.json", "r") as f:
        data = json.load(f)
except FileNotFoundError:
    print("Le fichier 'portfolio-example.json' est introuvable. Veuillez vérifier le chemin.")
    exit(1)

# Paramètres des données
n = data["num_assets"]  # Nombre d'actifs
sigma = np.array(data["covariance"])  # Matrice de covariance
mu = np.array(data["expected_return"])  # Espérances de rendements
mu_0 = data["target_return"]  # Rendement cible
k = data["portfolio_max_size"]  # Taille maximale du portefeuille

# Modèle de Gurobi
with gp.Model("portfolio") as model:
    # Création des variables
    x = model.addVars(n, vtype=GRB.BINARY, name="x")  # Inclusion dans le portefeuille (binaire)
    w = model.addVars(n, lb=0, ub=1, vtype=GRB.CONTINUOUS, name="w")  # Pondérations des actifs

    # Fonction objectif : Minimise le risque (x' * sigma * x)
    risk_expr = gp.quicksum(w[i] * sigma[i, j] * w[j] for i in range(n) for j in range(n))
    model.setObjective(risk_expr, GRB.MINIMIZE)

    # Contraintes :
    # 1. Rendement cible
    model.addConstr(gp.quicksum(mu[i] * w[i] for i in range(n)) >= mu_0, name="return")

    # 2. Somme des pondérations = 1
    model.addConstr(gp.quicksum(w[i] for i in range(n)) == 1, name="weights_sum")

    # 3. Lien entre variables binaires et pondérations : w[i] > 0 implique x[i] == 1
    for i in range(n):
        model.addConstr(w[i] <= x[i], name=f"link_{i}")

    # 4. Limitation du nombre d'actifs dans le portefeuille
    model.addConstr(gp.quicksum(x[i] for i in range(n)) <= k, name="max_assets")

    # Lancer l'optimisation
    model.optimize()

    # Vérifier si une solution optimale a été trouvée
    if model.Status == GRB.OPTIMAL:
        # Extraire les résultats du portefeuille
        portfolio = [w[i].X for i in range(n)]  # Pondérations optimales
        risk = model.ObjVal  # Valeur du risque optimisé
        expected_return = sum(mu[i] * portfolio[i] for i in range(n))  # Rendement attendu

        # DataFrame des résultats
        df = pd.DataFrame(
            data=portfolio + [risk, expected_return],
            index=[f"asset_{i}" for i in range(n)] + ["risk", "return"],
            columns=["Portfolio"],
        )
        print(df)
    else:
        print("Aucune solution optimale trouvée.")
