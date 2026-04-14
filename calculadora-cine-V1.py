import streamlit as st

# Configuración de página
st.set_page_config(page_title="Calculadora Nómina Cine", page_icon="🎬")

# Estilo CSS para arreglar los errores visuales y el espaciado
st.markdown("""
    <style>
    /* Uniformar fuentes */
    html, body, [class*="st-"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Estilo para los botones principales */
    .stButton > button {
        border-radius: 8px;
        height: 3em;
    }
    /* Botón Calcular (Azul acero) */
    div.stButton > button[kind="primary"] {
        background-color: #4682B4;
        border: none;
    }
    /* Botón Nuevo cálculo (Diseño discreto) */
    div.stButton > button:first-child[data-testid="baseButton-secondary"] {
        background-color: transparent;
        color: #4682B4;
        border: 1px solid #4682B4;
    }
    /* Quitar el recuadro de los botones X de borrar */
    div[data-testid="stHorizontalBlock"] button {
        border: none !important;
        background-color: transparent !important;
        color: gray !important;
        box-shadow: none !important;
        height: auto !important;
        padding: 0 !important;
    }
    /* Reducir espacio entre líneas de acumulados */
    .stMarkdown p {
        margin-bottom: 5px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Calculadora de nómina")

# Inicialización de estados
if 'extras_lista' not in st.session_state: st.session_state.extras_lista = []
if 'dietas' not in st.session_state: 
    st.session_state.dietas = {"comida": 0, "cena": 0, "sin": 0, "con": 0}

# --- SELECTOR DE CONTRATO ---
tipo_contrato = st.radio("¿Qué tipo de contrato tienes?", ('📅 Días sueltos', '🗓 Mes'))

if 'Días sueltos' in tipo_contrato:
    bruto_dia = st.number_input("¿Cuál es tu salario bruto?", min_value=0.0, step=1.0, format="%.f")
    horas_base = st.number_input("¿De cuántas horas es la jornada?", min_value=1.0, value=8.0, step=1.0, format="%.f")
    precio_hora_base = bruto_dia / horas_base if horas_base > 0 else 0
    jornadas = st.number_input("¿Cuántas jornadas son?", min_value=1, step=1)
else:
    salario_mes_bruto = st.number_input("¿Cuál es tu salario bruto?", min_value=0.0, step=1.0, format="%.f")
    h_sem = st.number_input("¿Horas semanales?", min_value=1.0, step=1.0, value=40.0, format="%.f")
    bruto_dia = salario_mes_bruto / 30
    precio_hora_base = (bruto_dia * 7) / h_sem
    mes_entero = st.radio("¿Has trabajado el mes entero?", ('Sí', 'No'))
    jornadas = 30 if mes_entero == 'Sí' else st.number_input("¿Cuántos días has trabajado?", min_value=1, max_value=30, step=1)

# --- RÉGIMEN E IRPF ---
regimen = st.selectbox("Selecciona Régimen de la SS", ["Artistas", "General"])
irpf_sugerido = 2 if regimen == "Artistas" else 15
irpf = st.number_input("¿Cuál es tu IRPF? (0 para mínimo)", value=int(irpf_sugerido), step=1, format="%d")

st.subheader("Otros conceptos")

# --- EXTRAS (Sin flechas raras en el título) ---
with st.expander("Añadir Horas Extras / Festivas", expanded=False):
    col_qty, col_mult = st.columns(2)
    e_qty = col_qty.number_input("¿Cuántas?", min_value=0.0, step=1.0, format="%.f")
    e_mult = col_mult.number_input("Factor (ej. 1,5)", min_value=1.0, value=1.5, step=0.1)
    e_tipo = st.radio("Tipo de hora", ('Hora Extra', 'Festiva, otras...'))
    
    if st.button("Añadir estas horas"):
        if e_qty > 0:
            ss_rate = 0.047 if 'Extra' in e_tipo else 0.0653
            bruto_t = (precio_hora_base * e_mult) * e_qty
            neto_t = bruto_t * (1 - ss_rate - (irpf/100))
            st.session_state.extras_lista.append({'desc': f"{int(e_qty)}h {e_tipo} (x{e_mult})", 'bruto': bruto_t, 'neto': neto_t})
            st.rerun()

    if st.session_state.extras_lista:
        st.write("**Añadidas:**")
        for i, ex in enumerate(st.session_state.extras_lista):
            c_ex, c_del = st.columns([0.9, 0.1])
            c_ex.write(f"⚡️ {ex['desc']}")
            if c_del.button("X", key=f"del_ex_{i}"):
                st.session_state.extras_lista.pop(i)
                st.rerun()

# --- DIETAS (Con precios recuperados) ---
with st.expander("Añadir Dietas", expanded=False):
    c1, c2 = st.columns(2)
    if c1.button("🌯 Media comida (14,02€)"): st.session_state.dietas["comida"] += 1; st.rerun()
    if c2.button("🍽 Media cena (16,36€)"): st.session_state.dietas["cena"] += 1; st.rerun()
    if c1.button("🚍 Sin pernocta (30,38€)"): st.session_state.dietas["sin"] += 1; st.rerun()
    if c2.button("💤 Con pernocta (51,39€)"): st.session_state.dietas["con"] += 1; st.rerun()
    
    d_str = []
    if st.session_state.dietas["comida"] > 0: d_str.append(f"🌯 x{st.session_state.dietas['comida']}")
    if st.session_state.dietas["cena"] > 0: d_str.append(f"🍽 x{st.session_state.dietas['cena']}")
    if st.session_state.dietas["sin"] > 0: d_str.append(f"🚍 x{st.session_state.dietas['sin']}")
    if st.session_state.dietas["con"] > 0: d_str.append(f"💤 x{st.session_state.dietas['con']}")
    
    if d_str:
        st.write("**Acumulado:**")
        st.write(" | ".join(d_str))
        if st.button("Limpiar dietas"):
            st.session_state.dietas = {k:0 for k in st.session_state.dietas}
            st.rerun()

especial = st.checkbox("¿Alguna jornada especial? (+20€)")
especiales_qty = st.number_input("¿Cuántas?", min_value=1, step=1) if especial else 0

liq_opcion = st.selectbox("¿Las vacaciones y el finiquito van aparte?", ['No, calcular', 'Ambas', 'Sólo vacaciones', 'Sólo finiquito'])

# --- CÁLCULO Y RESULTADOS ---
if st.button("Calcular total", type="primary", use_container_width=True):
    # Lógica de suma
    b_base = (bruto_dia * jornadas) + (especiales_qty * 20)
    n_base = b_base * (1 - 0.0653 - (irpf/100))
    total_extras_neto = sum(item['neto'] for item in st.session_state.extras_lista)
    total_extras_bruto = sum(item['bruto'] for item in st.session_state.extras_lista)
    dietas_total = (st.session_state.dietas["comida"] * 14.02 + st.session_state.dietas["cena"] * 16.36 + 
                    st.session_state.dietas["sin"] * 30.38 + st.session_state.dietas["con"] * 51.39)
    base_liq = bruto_dia * jornadas
    v_bruto = (base_liq * 0.07) if liq_opcion in ['Ambas', 'Sólo vacaciones'] else 0
    f_bruto = (base_liq * 0.0333) if liq_opcion in ['Ambas', 'Sólo finiquito'] else 0
    liq_bruta = v_bruto + f_bruto
    liq_neta = liq_bruta * (1 - (irpf/100))
    
    total_final = n_base + total_extras_neto + dietas_total + liq_neta

    st.markdown("### Resumen Final")
    st.write(f"📅 **Base ({jornadas} días):**")
    st.write(f"   • {n_base:.2f}€ netos (Bruto: {b_base:.2f}€)")
    if total_extras_neto > 0:
        st.write(f"⚡️ **Extras/Festivas:**")
        st.write(f"   • {total_extras_neto:.2f}€ netos (Bruto: {total_extras_bruto:.2f}€)")
    if dietas_total > 0:
        st.write(f"✈️ **Dietas:** {dietas_total:.2f}€")
    if liq_neta > 0:
        st.write(f"📄 **Liquidación:**")
        st.write(f"   • {liq_neta:.2f}€ netos (Bruto: {liq_bruta:.2f}€)")
    st.markdown(f"## Total: {total_final:.2f}€")

# Botón de reinicio separado
for _ in range(3): st.write("")
if st.button("Nuevo cálculo", use_container_width=True):
    st.session_state.extras_lista = []
    st.session_state.dietas = {"comida": 0, "cena": 0, "sin": 0, "con": 0}
    st.rerun()
