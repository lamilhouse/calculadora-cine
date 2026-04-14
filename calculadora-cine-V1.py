import streamlit as st

# Configuración de página
st.set_page_config(page_title="Calculadora Nómina Cine", page_icon="🎬")

# --- ESTILO CSS DEFINITIVO ---
st.markdown("""
    <style>
    /* Adiós a las flechas y textos locos de los expanders */
    .streamlit-expanderHeader { display: none !important; }
    
    /* Uniformar fuentes */
    html, body, [class*="st-"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Botón Calcular (Azul acero) */
    div.stButton > button[kind="primary"] {
        background-color: #4682B4;
        color: white;
        border: none;
        border-radius: 8px;
        height: 3em;
    }
    
    /* Botón Nuevo cálculo (Discreto) */
    div.stButton > button:not([kind="primary"]) {
        background-color: transparent;
        color: #4682B4;
        border: 1px solid #4682B4;
        border-radius: 8px;
        height: 3em;
    }

    /* Botones X: eliminamos el recuadro para que sea solo la letra */
    div[data-testid="stHorizontalBlock"] button {
        border: none !important;
        background-color: transparent !important;
        color: #888 !important;
        box-shadow: none !important;
        padding: 0 !important;
        min-height: 0px !important;
        line-height: 1 !important;
    }

    /* Interlineado mínimo para que el resumen sea compacto */
    .stMarkdown p {
        margin-top: 0px !important;
        margin-bottom: 2px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Calculadora de nómina")

# --- FUNCIÓN DE LIMPIEZA ---
def limpiar_todo():
    for key in st.session_state.keys():
        del st.session_state[key]

# Inicialización de listas si no existen
if 'extras_lista' not in st.session_state: st.session_state.extras_lista = []
if 'dietas' not in st.session_state: 
    st.session_state.dietas = {"comida": 0, "cena": 0, "sin": 0, "con": 0}

# --- DATOS BASE DEL CONTRATO ---
tipo_contrato = st.radio("¿Qué tipo de contrato tienes?", ('📅 Días sueltos', '🗓 Mes'), key="tipo_contrato")

if 'Días sueltos' in tipo_contrato:
    bruto_dia = st.number_input("¿Cuál es tu salario bruto?", min_value=0.0, step=1.0, format="%.f", key="bruto_dia")
    horas_base = st.number_input("¿De cuántas horas es la jornada?", min_value=1.0, value=8.0, step=1.0, format="%.f", key="h_base")
    precio_hora_base = bruto_dia / horas_base if horas_base > 0 else 0
    jornadas = st.number_input("¿Cuántas jornadas son?", min_value=1, step=1, key="jornadas_sueltas")
else:
    salario_mes_bruto = st.number_input("¿Cuál es tu salario bruto?", min_value=0.0, step=1.0, format="%.f", key="s_mes")
    h_sem = st.number_input("¿Horas semanales?", min_value=1.0, step=1.0, value=40.0, format="%.f", key="h_sem")
    bruto_dia = salario_mes_bruto / 30
    precio_hora_base = (bruto_dia * 7) / h_sem
    mes_entero = st.radio("¿Has trabajado el mes entero?", ('Sí', 'No'), key="mes_entero")
    jornadas = 30 if mes_entero == 'Sí' else st.number_input("¿Cuántos días has trabajado?", min_value=1, max_value=30, step=1, key="dias_mes")

# --- RÉGIMEN E IRPF ---
regimen = st.selectbox("Selecciona Régimen de la SS", ["Artistas", "General"], key="regimen")
irpf_sugerido = 2 if regimen == "Artistas" else 15
irpf = st.number_input("¿Cuál es tu IRPF?", value=int(irpf_sugerido), step=1, format="%d", key="irpf_val")

st.write("### Otros conceptos")

# --- BLOQUE EXTRAS ---
with st.container(border=True):
    st.write("**Añadir Horas Extras / Festivas**")
    col_qty, col_mult = st.columns(2)
    e_qty = col_qty.number_input("¿Cuántas?", min_value=0.0, step=1.0, format="%.f", key="e_qty")
    e_mult = col_mult.number_input("Factor (ej. 1,5)", min_value=1.0, value=1.5, step=0.1, key="e_mult")
    e_tipo = st.radio("Tipo de hora", ('Hora Extra', 'Festiva, otras...'), key="e_tipo")
    
    if st.button("Añadir estas horas"):
        if e_qty > 0:
            ss_rate = 0.047 if 'Extra' in e_tipo else 0.0653
            bruto_t = (precio_hora_base * e_mult) * e_qty
            neto_t = bruto_t * (1 - ss_rate - (irpf/100))
            st.session_state.extras_lista.append({
                'desc': f"{int(e_qty)}h {e_tipo} (x{e_mult})", 
                'bruto': bruto_t, 
                'neto': neto_t
            })
            st.rerun()

    if st.session_state.extras_lista:
        st.write("---")
        for i, ex in enumerate(st.session_state.extras_lista):
            c_ex, c_del = st.columns([0.9, 0.1])
            c_ex.write(f"⚡️ {ex['desc']}")
            if c_del.button("X", key=f"del_ex_{i}"):
                st.session_state.extras_lista.pop(i)
                st.rerun()

# --- BLOQUE DIETAS ---
with st.container(border=True):
    st.write("**Añadir Dietas**")
    c1, c2 = st.columns(2)
    if c1.button("🌯 Media - comida (14,02€)"): st.session_state.dietas["comida"] += 1; st.rerun()
    if c2.button("🍽 Media - cena (16,36€)"): st.session_state.dietas["cena"] += 1; st.rerun()
    if c1.button("🚍 Sin pernocta (30,38€)"): st.session_state.dietas["sin"] += 1; st.rerun()
    if c2.button("💤 Con pernocta (51,39€)"): st.session_state.dietas["con"] += 1; st.rerun()
    
    d_str = []
    if st.session_state.dietas["comida"] > 0: d_str.append(f"🌯 x{st.session_state.dietas['comida']}")
    if st.session_state.dietas["cena"] > 0: d_str.append(f"🍽 x{st.session_state.dietas['cena']}")
    if st.session_state.dietas["sin"] > 0: d_str.append(f"🚍 x{st.session_state.dietas['sin']}")
    if st.session_state.dietas["con"] > 0: d_str.append(f"💤 x{st.session_state.dietas['con']}")
    
    if d_str:
        st.write("---")
        c_res, c_clr = st.columns([0.9, 0.1])
        c_res.write(f"{' | '.join(d_str)}")
        if c_clr.button("X", key="clear_dietas"):
            st.session_state.dietas = {k:0 for k in st.session_state.dietas}
            st.rerun()

# --- JORNADAS ESPECIALES Y PLUS CONSECUTIVAS ---
especial = st.checkbox("¿Alguna jornada especial? (+20€)", key="check_esp")
especiales_qty = st.number_input("¿Cuántas?", min_value=1, step=1, key="qty_esp") if especial else 0

plus_consec = st.checkbox("¿Algún plus por 4 jornadas especiales consecutivas? (+35€)", key="check_plus")
plus_consec_qty = st.number_input("¿Cuántos?", min_value=1, step=1, key="qty_plus") if plus_consec else 0

liq_opcion = st.selectbox("¿Las vacaciones y el finiquito van aparte?", ['No, calcular', 'Todo aparte', 'Vacaciones aparte', 'Finiquito aparte'], key="liq_val")

# --- PROCESADO DE CÁLCULO ---
st.write("")
if st.button("Calcular total", type="primary", use_container_width=True):
    # 1. Base (Salario base + jornadas especiales + plus consecutivas)
    b_base = (bruto_dia * jornadas) + (especiales_qty * 20) + (plus_consec_qty * 35)
    n_base = b_base * (1 - 0.0653 - (irpf/100))
    
    # 2. Extras acumulados
    total_extras_neto = sum(item['neto'] for item in st.session_state.extras_lista)
    total_extras_bruto = sum(item['bruto'] for item in st.session_state.extras_lista)
    
    # 3. Dietas acumuladas
    dietas_total = (st.session_state.dietas["comida"] * 14.02 + 
                    st.session_state.dietas["cena"] * 16.36 + 
                    st.session_state.dietas["sin"] * 30.38 + 
                    st.session_state.dietas["con"] * 51.39)
    
    # 4. Vacaciones y finiquito
    base_liq = bruto_dia * jornadas
    v_bruto = (base_liq * 0.07) if liq_opcion in ['Todo aparte', 'Vacaciones aparte'] else 0
    f_bruto = (base_liq * 0.0333) if liq_opcion in ['Todo aparte', 'Finiquito aparte'] else 0
    liq_bruta = v_bruto + f_bruto
    liq_neta = liq_bruta * (1 - (irpf/100))
    
    # TOTAL NETO FINAL
    total_final = n_base + total_extras_neto + dietas_total + liq_neta

    st.markdown("### Resumen")
    st.write(f"📅 **Base ({jornadas} días) + Jornadas especiales:**")
    st.write(f"   • {n_base:.2f}€ netos (Bruto: {b_base:.2f}€)")
    if total_extras_neto > 0:
        st.write(f"⚡️ **Extras/Festivas:**")
        st.write(f"   • {total_extras_neto:.2f}€ netos (Bruto: {total_extras_bruto:.2f}€)")
    if dietas_total > 0:
        st.write(f"✈️ **Dietas:** {dietas_total:.2f}€")
    if liq_neta > 0:
        st.write(f"📄 **Liquidación:**")
        st.write(f"   • {liq_neta:.2f}€ netos (Bruto: {liq_bruta:.2f}€)")
    st.markdown(f"## Total: {total_final:.2f}€")

# --- BOTÓN DE REINICIO TOTAL ---
for _ in range(3): st.write("")
st.button("Nuevo cálculo", use_container_width=True, on_click=limpiar_todo)
