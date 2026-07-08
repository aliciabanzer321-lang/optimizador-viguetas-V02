"""
app.py
------
Optimizador de Mezcla de Producción de Viguetas — Método Simplex.
Interfaz con identidad visual de "plano técnico" (blueprint) de ingeniería civil.

Ejecutar con:
    streamlit run app.py
"""

import datetime

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from simplex_solver import solve_simplex

st.set_page_config(page_title="Optimizador de Producción de Viguetas",
                    page_icon="📐", layout="wide")

# ============================================================================
# ESTILO — identidad visual "plano técnico" (blueprint)
# ============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --blue-deep: #0B2A43;
    --blue-panel: #123B5C;
    --blue-line: rgba(255,255,255,0.08);
    --ink: #EAF2F8;
    --ink-dim: #9FB8CC;
    --orange: #FF7A1A;
    --green-ok: #4CAF7D;
    --red-crit: #E85C4A;
}

.stApp {
    background-color: var(--blue-deep);
    background-image:
        linear-gradient(var(--blue-line) 1px, transparent 1px),
        linear-gradient(90deg, var(--blue-line) 1px, transparent 1px);
    background-size: 28px 28px;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--ink); }

.titleblock {
    border: 1.5px solid var(--ink-dim);
    background: var(--blue-panel);
    padding: 18px 24px;
    margin-bottom: 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}
.titleblock-left { display: flex; align-items: center; gap: 18px; }
.titleblock h1 {
    font-family: 'Oswald', sans-serif;
    font-weight: 600;
    font-size: 1.55rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    color: var(--ink);
    margin: 0;
    line-height: 1.15;
}
.titleblock .subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--ink-dim);
    margin-top: 4px;
}
.titleblock-meta {
    display: grid;
    grid-template-columns: repeat(4, auto);
    gap: 0;
    border: 1px solid var(--ink-dim);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
}
.titleblock-meta div { padding: 6px 12px; border-right: 1px solid var(--ink-dim); }
.titleblock-meta div:last-child { border-right: none; }
.titleblock-meta .label { color: var(--ink-dim); display: block; font-size: 0.62rem; letter-spacing: 0.05em; }
.titleblock-meta .value { color: var(--orange); font-weight: 700; }

.section-label {
    font-family: 'Oswald', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-size: 1.0rem;
    color: var(--ink);
    border-bottom: 2px solid var(--orange);
    padding-bottom: 6px;
    margin: 8px 0 16px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-label .tag {
    background: var(--orange);
    color: var(--blue-deep);
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 0.7rem;
    padding: 2px 7px;
}

.stButton>button {
    background: var(--orange);
    color: var(--blue-deep);
    font-family: 'Oswald', sans-serif;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border: none;
    border-radius: 2px;
    padding: 0.6rem 1.4rem;
}
.stButton>button:hover { background: #ffa04d; color: var(--blue-deep); }

[data-testid="stMetric"] {
    background: var(--blue-panel);
    border: 1px solid var(--ink-dim);
    border-left: 4px solid var(--orange);
    padding: 12px 16px;
}
[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; color: var(--orange); }
[data-testid="stMetricLabel"] { font-family: 'Inter', sans-serif; color: var(--ink-dim); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.04em; }

[data-testid="stDataFrame"], [data-testid="stDataEditor"] { border: 1px solid var(--ink-dim); }
[data-testid="stExpander"] { border: 1px solid var(--ink-dim); background: var(--blue-panel); }

.footnote {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--ink-dim);
    border-top: 1px solid var(--ink-dim);
    padding-top: 10px;
    margin-top: 24px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Ícono de viga simplemente apoyada con líneas de cota (SVG, firma visual)
# ----------------------------------------------------------------------------
BEAM_SVG = """
<svg width="86" height="60" viewBox="0 0 86 60" xmlns="http://www.w3.org/2000/svg">
  <g stroke="#FF7A1A" stroke-width="1.4">
    <line x1="10" y1="6" x2="10" y2="16"/><line x1="24" y1="6" x2="24" y2="16"/>
    <line x1="38" y1="6" x2="38" y2="16"/><line x1="52" y1="6" x2="52" y2="16"/>
    <line x1="66" y1="6" x2="66" y2="16"/><line x1="76" y1="6" x2="76" y2="16"/>
  </g>
  <path d="M10 6 L76 6" stroke="#FF7A1A" stroke-width="1.4" fill="none"/>
  <rect x="8" y="16" width="70" height="6" fill="#EAF2F8"/>
  <polygon points="14,22 8,32 20,32" fill="none" stroke="#EAF2F8" stroke-width="1.4"/>
  <circle cx="72" cy="28" r="5" fill="none" stroke="#EAF2F8" stroke-width="1.4"/>
  <line x1="66" y1="33" x2="78" y2="33" stroke="#EAF2F8" stroke-width="1.4"/>
  <line x1="8" y1="46" x2="78" y2="46" stroke="#9FB8CC" stroke-width="1"/>
  <line x1="8" y1="43" x2="8" y2="49" stroke="#9FB8CC" stroke-width="1"/>
  <line x1="78" y1="43" x2="78" y2="49" stroke="#9FB8CC" stroke-width="1"/>
  <text x="43" y="58" font-family="JetBrains Mono, monospace" font-size="8" fill="#9FB8CC" text-anchor="middle">L</text>
</svg>
"""

today = datetime.date.today().strftime("%d/%m/%Y")

titleblock_html = (
'<div class="titleblock">'
'<div class="titleblock-left">'
f'{BEAM_SVG}'
'<div>'
'<h1>Optimizador de Producción de Viguetas</h1>'
'<div class="subtitle">Programación Lineal — Método Simplex · Mezcla óptima de fabricación</div>'
'</div>'
'</div>'
'<div class="titleblock-meta">'
'<div><span class="label">PLANO N°</span><span class="value">OPT-01</span></div>'
'<div><span class="label">ESCALA</span><span class="value">S/E</span></div>'
f'<div><span class="label">FECHA</span><span class="value">{today}</span></div>'
'<div><span class="label">REV</span><span class="value">A</span></div>'
'</div>'
'</div>'
)
st.markdown(titleblock_html, unsafe_allow_html=True)

# ------------------------------------------------------------------
# Datos de ejemplo (precargados) — el usuario puede editarlos libremente
# ------------------------------------------------------------------
DEFAULT_PRODUCTS = pd.DataFrame({
    "Tipo de Vigueta": ["V-10 (10 cm)", "V-12 (12 cm)", "V-15 (15 cm)"],
    "Utilidad unit. (Bs)": [18.0, 25.0, 32.0],
    "Acero (kg/u)": [1.2, 1.6, 2.1],
    "Hormigón (m3/u)": [0.015, 0.019, 0.024],
    "Mano de obra (h/u)": [0.30, 0.35, 0.42],
    "Horas de molde (h/u)": [0.50, 0.55, 0.65],
    "Demanda máx. (u)": [800, 600, 400],
})

DEFAULT_RESOURCES = pd.DataFrame({
    "Recurso": ["Acero (kg)", "Hormigón (m3)", "Mano de obra (h)", "Horas de molde (h)"],
    "Disponibilidad": [1500.0, 20.0, 350.0, 500.0],
})

if "products" not in st.session_state:
    st.session_state.products = DEFAULT_PRODUCTS.copy()
if "resources" not in st.session_state:
    st.session_state.resources = DEFAULT_RESOURCES.copy()

# ------------------------------------------------------------------
# Sección 1: Datos de entrada
# ------------------------------------------------------------------
st.markdown('<div class="section-label"><span class="tag">01</span> Datos de producción</div>',
            unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("**Tipos de vigueta y consumo de recursos por unidad**")
    st.session_state.products = st.data_editor(
        st.session_state.products,
        num_rows="dynamic",
        use_container_width=True,
        key="products_editor",
    )

with col2:
    st.markdown("**Disponibilidad de recursos**")
    st.session_state.resources = st.data_editor(
        st.session_state.resources,
        num_rows="dynamic",
        use_container_width=True,
        key="resources_editor",
    )

products_df = st.session_state.products.dropna(how="all")
resources_df = st.session_state.resources.dropna(how="all")

resource_cols = [c for c in products_df.columns
                  if c not in ("Tipo de Vigueta", "Utilidad unit. (Bs)", "Demanda máx. (u)")]

# ------------------------------------------------------------------
# Sección 2: Optimización
# ------------------------------------------------------------------
st.markdown('<div class="section-label"><span class="tag">02</span> Optimización</div>',
            unsafe_allow_html=True)

usar_demanda = st.checkbox(
    "Incluir demanda máxima por tipo de vigueta como restricción adicional",
    value=True,
    help="Si tu empresa tiene un límite de pedidos/demanda por tipo, actívalo para no "
         "sobreproducir un solo tipo aunque sea el más rentable."
)

if st.button("▶ Optimizar producción", type="primary"):
    try:
        product_names = products_df["Tipo de Vigueta"].tolist()
        n = len(product_names)

        c = products_df["Utilidad unit. (Bs)"].to_numpy(dtype=float)

        A_rows, b_rows, constraint_labels = [], [], []
        for _, row in resources_df.iterrows():
            resource_name = row["Recurso"]
            matched_col = None
            for col in resource_cols:
                if col.split(" (")[0].strip().lower() in resource_name.lower() or \
                   resource_name.split(" (")[0].strip().lower() in col.lower():
                    matched_col = col
                    break
            if matched_col is None:
                st.error(f"No se pudo emparejar el recurso '{resource_name}' con ninguna "
                         f"columna de consumo. Verifica que los nombres coincidan "
                         f"(ej. 'Acero (kg)' en recursos y 'Acero (kg/u)' en productos).")
                st.stop()
            A_rows.append(products_df[matched_col].to_numpy(dtype=float))
            b_rows.append(float(row["Disponibilidad"]))
            constraint_labels.append(resource_name)

        A = np.array(A_rows)
        b = np.array(b_rows)

        if usar_demanda and "Demanda máx. (u)" in products_df.columns:
            for j in range(n):
                dem = products_df["Demanda máx. (u)"].iloc[j]
                if pd.notna(dem):
                    fila = np.zeros(n)
                    fila[j] = 1.0
                    A = np.vstack([A, fila])
                    b = np.append(b, float(dem))
                    constraint_labels.append(f"Demanda máx. {product_names[j]}")

        result = solve_simplex(c, A, b, var_names=product_names)

        if result.status != "optimal":
            st.error(f"⚠ {result.message}")
        else:
            st.success(f"✓ {result.message}")

            st.markdown('<div class="section-label"><span class="tag">03</span> Resultados</div>',
                        unsafe_allow_html=True)

            col_a, col_b = st.columns([1, 1])

            res_df = pd.DataFrame({
                "Tipo de Vigueta": product_names,
                "Cantidad a producir": np.round(result.x, 2),
                "Utilidad unitaria (Bs)": c,
                "Utilidad total (Bs)": np.round(result.x * c, 2),
            })

            with col_a:
                st.dataframe(res_df, use_container_width=True, hide_index=True)
                st.metric("UTILIDAD TOTAL MÁXIMA", f"Bs {result.z:,.2f}")

            with col_b:
                chart = alt.Chart(res_df).mark_bar(color="#FF7A1A", size=32).encode(
                    x=alt.X("Tipo de Vigueta:N", title=None, sort=None,
                            axis=alt.Axis(labelColor="#EAF2F8", labelFont="JetBrains Mono")),
                    y=alt.Y("Cantidad a producir:Q", title="Unidades",
                            axis=alt.Axis(labelColor="#EAF2F8", titleColor="#9FB8CC", grid=True, gridColor="#1c4364")),
                    tooltip=["Tipo de Vigueta", "Cantidad a producir"]
                ).properties(height=280, background="transparent").configure_view(strokeWidth=0)
                st.altair_chart(chart, use_container_width=True)

            st.markdown("**Uso de recursos — cuellos de botella resaltados**")
            n_res = len(resources_df)
            usage = A[:n_res] @ result.x
            disponible = b[:n_res]
            pct = 100 * usage / disponible

            uso_df = pd.DataFrame({
                "Recurso": constraint_labels[:n_res],
                "Disponible": disponible,
                "Utilizado": np.round(usage, 2),
                "% Utilización": np.round(pct, 1),
            })

            def color_estado(p):
                if p >= 95:
                    return "#E85C4A"
                elif p >= 80:
                    return "#FF7A1A"
                return "#4CAF7D"

            uso_df["_color"] = uso_df["% Utilización"].apply(color_estado)

            bars = alt.Chart(uso_df).mark_bar(size=22).encode(
                y=alt.Y("Recurso:N", title=None, sort="-x",
                        axis=alt.Axis(labelColor="#EAF2F8", labelFont="JetBrains Mono", labelLimit=200)),
                x=alt.X("% Utilización:Q", title="% utilizado", scale=alt.Scale(domain=[0, 110]),
                        axis=alt.Axis(labelColor="#EAF2F8", titleColor="#9FB8CC", gridColor="#1c4364")),
                color=alt.Color("_color:N", scale=None, legend=None),
                tooltip=["Recurso", "Disponible", "Utilizado", "% Utilización"]
            ).properties(height=32 * len(uso_df) + 40, background="transparent")

            regla_100 = alt.Chart(pd.DataFrame({"x": [100]})).mark_rule(
                color="#EAF2F8", strokeDash=[4, 3]).encode(x="x:Q")

            st.altair_chart((bars + regla_100).configure_view(strokeWidth=0), use_container_width=True)
            st.dataframe(uso_df.drop(columns="_color"), use_container_width=True, hide_index=True)

            criticos = uso_df[uso_df["% Utilización"] >= 95]["Recurso"].tolist()
            if criticos:
                st.warning(f"⚠ Recurso(s) crítico(s) (≥95% de uso, limitan la producción): "
                           f"{', '.join(criticos)}")

            csv = res_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Descargar resultados (CSV)", csv,
                                "resultado_optimizacion_viguetas.csv", "text/csv")

            with st.expander("🔍 Ver iteraciones del método Simplex (tableau paso a paso)"):
                for snap in result.iterations:
                    st.markdown(f"**Iteración {snap['iteration']}**")
                    cols = snap["col_names"] + ["RHS"]
                    tdf = pd.DataFrame(snap["tableau"], columns=cols)
                    tdf.index = [f"Fila {snap['col_names'][b] if b < len(snap['col_names']) else b}"
                                 for b in snap["basis"]] + ["Z"]
                    st.dataframe(tdf.round(3), use_container_width=True)

    except Exception as e:
        st.error(f"Ocurrió un error al optimizar: {e}")

st.markdown(
    '<div class="footnote">MODELO: Programación Lineal · Método Simplex (implementación propia, '
    'tabular con variables de holgura) · Todas las restricciones se manejan como ≤ con disponibilidad ≥ 0.</div>',
    unsafe_allow_html=True
)
