# 📐 Optimizador de Producción de Viguetas — Método Simplex

Aplicación web que ayuda a una empresa de prefabricados de hormigón (viguetas
pretensadas) a decidir **cuántas unidades de cada tipo de vigueta fabricar**
para **maximizar la utilidad total**, respetando las restricciones de
recursos: acero, hormigón, mano de obra, horas de molde/curado, etc.

El motor de optimización es una implementación **propia** del método
Simplex (tabular, con variables de holgura) — no depende de librerías de
optimización externas, así se puede ver y entender cada iteración.

## 🔗 Aplicación en vivo

La app está desplegada en Streamlit Community Cloud:
`https://[tu-subdominio].streamlit.app`

*(actualiza este link una vez que despliegues o cambies el subdominio en
Streamlit Cloud)*

## Cómo usarla

1. **Tabla de tipos de vigueta**: edita/agrega/elimina filas con cada tipo
   de vigueta que produce tu empresa (V-10, V-12, V-15, etc.), su utilidad
   por unidad (Bs), y cuánto consume de cada recurso por unidad producida
   (kg de acero, m³ de hormigón, horas de mano de obra, horas de molde).
2. **Tabla de recursos**: define cuánto tienes disponible de cada recurso
   en el periodo a planificar (ej. por semana o por mes). Importante: el
   nombre del recurso debe coincidir con el de la columna de consumo
   (ej. "Acero (kg)" ↔ "Acero (kg/u)").
3. Presiona **"▶ Optimizar producción"**.
4. La app muestra:
   - Cuántas unidades de cada tipo producir y la utilidad total máxima.
   - Un gráfico de la mezcla óptima de producción.
   - El uso de cada recurso, con los **cuellos de botella resaltados en
     rojo/naranja** (recursos que están limitando la producción).
   - Un botón para descargar los resultados en CSV.
   - Un panel opcional con el detalle de cada iteración del método
     Simplex (para fines académicos/auditoría).

## Estructura del proyecto

```
├── app.py                  # Interfaz Streamlit (lo que ve el usuario)
├── simplex_solver.py       # Motor del método Simplex (lógica matemática)
├── requirements.txt        # Dependencias de Python
├── .streamlit/config.toml  # Tema visual (colores tipo "plano técnico")
└── README.md                # Este archivo
```

## Modelo matemático detrás de la app

```
Maximizar   Z = Σ (utilidad_j × x_j)
sujeto a    Σ (consumo_recurso_i,j × x_j) ≤ disponibilidad_recurso_i   ∀ i
            x_j ≤ demanda_máxima_j                                     (opcional)
            x_j ≥ 0
```

Donde `x_j` es la cantidad a producir del tipo de vigueta `j`.

## Actualizar la app desplegada

Como está conectada a este repositorio de GitHub, cualquier cambio que
subas aquí (editar `app.py`, `simplex_solver.py`, etc. y hacer "Commit
changes") se refleja automáticamente en la app en vivo en 1-2 minutos,
sin que tengas que hacer nada más en Streamlit Cloud.

## Correrla localmente (opcional)

Si en algún momento tienes Python instalado en tu computadora y quieres
probarla localmente antes de subir cambios:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Próximos pasos posibles (si quieres ampliarla)

- Exportar el reporte a PDF o Excel con formato de empresa.
- Guardar escenarios anteriores para comparar meses.
- Agregar análisis de sensibilidad (cuánto puede variar el precio de un
  insumo antes de que cambie la solución óptima).
- Poner el logo y nombre real de tu empresa en el cajetín superior.
