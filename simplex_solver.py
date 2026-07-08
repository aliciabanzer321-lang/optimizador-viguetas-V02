"""
simplex_solver.py
------------------
Implementación del Método Simplex (tabular, forma estándar de maximización)
para el problema:

    Max  Z = c1*x1 + c2*x2 + ... + cn*xn
    s.a. A x <= b   (todas las restricciones de tipo <=, b >= 0)
         x  >= 0

Se usa el método Simplex clásico con variables de holgura (slack variables),
y se guarda el historial de cada tableau para poder mostrarlo paso a paso
en la interfaz (fines didácticos, consistente con MAT-374).

Regla de entrada: columna más negativa en la fila Z (regla estándar).
Regla de salida:  razón mínima (b_i / a_ij) con a_ij > 0.
Regla anti-ciclos: Bland's rule como desempate.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np


@dataclass
class SimplexResult:
    status: str                     # "optimal", "unbounded", "infeasible"
    x: Optional[np.ndarray] = None  # solución óptima (solo variables originales)
    z: Optional[float] = None       # valor óptimo de la función objetivo
    iterations: List[dict] = field(default_factory=list)  # historial de tableaus
    message: str = ""


def solve_simplex(c: np.ndarray, A: np.ndarray, b: np.ndarray,
                   var_names: Optional[List[str]] = None) -> SimplexResult:
    """
    Resuelve un problema de maximización en forma estándar con el método Simplex.

    Parámetros
    ----------
    c : vector de coeficientes de la función objetivo (longitud n)
    A : matriz de restricciones (m x n), todas del tipo <=
    b : vector de disponibilidad de recursos (longitud m), debe ser >= 0
    var_names : nombres de las variables originales (opcional, para reportes)

    Retorna
    -------
    SimplexResult
    """
    c = np.array(c, dtype=float)
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)

    m, n = A.shape  # m restricciones, n variables originales

    if np.any(b < 0):
        return SimplexResult(status="infeasible",
                              message="Todos los recursos disponibles (b) deben ser >= 0. "
                                      "Este solver básico no maneja b negativo (requeriría Fase I).")

    if var_names is None:
        var_names = [f"x{j+1}" for j in range(n)]

    n_slack = m
    total_cols = n + n_slack + 1  # + columna RHS

    # Tableau inicial: [A | I | b], fila Z: [-c | 0 | 0]
    tableau = np.zeros((m + 1, total_cols))
    tableau[:m, :n] = A
    tableau[:m, n:n + n_slack] = np.eye(n_slack)
    tableau[:m, -1] = b
    tableau[m, :n] = -c
    tableau[m, n:n + n_slack] = 0
    tableau[m, -1] = 0

    # Variables básicas iniciales = las de holgura
    basis = list(range(n, n + n_slack))

    col_names = var_names + [f"s{i+1}" for i in range(n_slack)]

    result = SimplexResult(status="optimal", iterations=[])

    max_iter = 200
    for it in range(max_iter):
        z_row = tableau[m, :-1]

        # Guardar snapshot del tableau actual (antes de pivotear)
        result.iterations.append({
            "iteration": it,
            "tableau": tableau.copy(),
            "basis": basis.copy(),
            "col_names": col_names,
        })

        # Condición de optimalidad: no hay coeficientes negativos en fila Z
        if np.all(z_row >= -1e-9):
            break

        # --- Variable entrante: la más negativa (Bland's rule en empates) ---
        candidates = np.where(z_row < -1e-9)[0]
        entering = candidates[np.argmin(z_row[candidates])]

        # --- Prueba de razón mínima para variable saliente ---
        col = tableau[:m, entering]
        ratios = np.full(m, np.inf)
        positive = col > 1e-9
        ratios[positive] = tableau[:m, -1][positive] / col[positive]

        if np.all(~positive):
            return SimplexResult(status="unbounded",
                                  message=f"El problema es no acotado (la variable "
                                          f"{col_names[entering]} puede crecer indefinidamente). "
                                          f"Revisa que todas las restricciones de recursos estén bien definidas.")

        leaving = np.argmin(ratios)

        # --- Pivoteo (Gauss-Jordan) ---
        pivot = tableau[leaving, entering]
        tableau[leaving, :] /= pivot
        for row in range(m + 1):
            if row != leaving:
                tableau[row, :] -= tableau[row, entering] * tableau[leaving, :]

        basis[leaving] = entering
    else:
        result.status = "infeasible"
        result.message = "Se alcanzó el número máximo de iteraciones sin converger."
        return result

    # Extraer solución
    x = np.zeros(n)
    for i, b_idx in enumerate(basis):
        if b_idx < n:
            x[b_idx] = tableau[i, -1]

    result.x = x
    result.z = float(np.dot(c, x))
    result.message = "Solución óptima encontrada."
    return result
