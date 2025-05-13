import subprocess

def run_simulation():
    """
    Exécute simulation.py avec la stratégie non_cooperative_strategy.py
    et l'environnement XX_square_diag.txt.
    Retourne le résultat (succès ou échec) et le nombre de steps.
    """
    try:
        # Exécute la commande avec les arguments spécifiés
        result = subprocess.run(
            ["python", "simulation.py", "--strategy-file", "cooperative_strategy.py", "--env", ".\\envs\\XX_square_diag.txt"],
            capture_output=True,
            text=True
        )
        # Analyse la sortie pour extraire les informations
        output = result.stdout
        if "Simulation complete!" in output:
            # Trouve le nombre de steps dans la sortie
            steps_line = [line for line in output.split("\n") if "Simulation completed in" in line]
            if steps_line:
                steps = int(steps_line[0].split("in")[1].split("steps")[0].strip())
                return True, steps
        return False, 0
    except Exception as e:
        print(f"Erreur lors de l'exécution : {e}")
        return False, 0

def main():
    num_runs = 100
    successes = 0
    total_steps = 0

    for i in range(num_runs):
        success, steps = run_simulation()
        if success:
            successes += 1
            total_steps += steps
        print(f"Run {i + 1}/{num_runs} - Success: {success}, Steps: {steps}")

    # Calcul des statistiques
    success_rate = (successes / num_runs) * 100
    avg_steps = total_steps / successes if successes > 0 else 0

    print("\n--- Résultats ---")
    print(f"Nombre de réussites : {successes}/{num_runs}")
    print(f"Taux de réussite : {success_rate:.2f}%")
    print(f"Nombre moyen de steps (en cas de succès) : {avg_steps:.2f}")

if __name__ == "__main__":
    main()