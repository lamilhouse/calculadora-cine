import streamlit as st

# Configuración de página y estilo para ocultar decimales feos en los inputs
st.set_page_config(page_title="Calculadora Nómina Cine", page_icon="🎬")
st.markdown("""
    <style>
    button[title="View fullscreen"] {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("🎬 Calculadora de nómina")

# Inicialización del cerebro (session_state) para que no olvide lo acumulado
if 'extras_lista' not in st.session_state: st.session_state.extras_lista = []
if 'dietas_lista' not in st.session_state: st.session_state.dietas_lista = []

# --- SELECTOR DE CONTRATO ---
tipo_contrato = st.radio("¿Qué tipo de contrato tienes?", ('📅 Días sueltos', '🗓 Mes'))

# --- BLOQUE DÍAS SUELTOS ---
if 'Días sueltos' in tipo_contrato:
    bruto_dia = st.number_input("¿Cuál es tu salario bruto?", min_value=0.0, step=1.0, format="%.f")
    horas_base = st.number_input("¿De cuántas horas es la jornada?", min_value=1.0, step=1.0, format="%.f")
    precio_hora_base = bruto_dia / horas_base if horas_base > 0 else 0
    jornadas = st.number_input("¿Cuántas jornadas son?", min_value=1, step=1)

# --- BLOQUE MES ---
else:
    salario_mes_bruto = st.number_input("¿Cuál es tu salario bruto?", min_value=0.0, step=1.0, format="%.f")
    h_sem = st.number_input("¿Horas semanales?", min_value=1.0, step=1.0, value=40.0, format="%.f")
    bruto_dia = salario_mes_bruto / 30
    precio_hora_base = (bruto_dia * 7) / h_sem
    
    mes_entero = st.radio("¿Has trabajado el mes entero?", ('Sí', 'No'))
    if mes_entero == 'Sí':
        jornadas = 30
    else:
        jornadas = st.number_input("¿Cuántos días has trabajado?", min_value=1, max_value=30, step=1)

# --- RÉGIMEN E IRPF ---
regimen = st.selectbox("Selecciona Régimen de la SS", ["Artistas", "General"])
# IRPF Correcto: Artistas 2%, General 15%
irpf_sugerido = 2.0 if regimen == "Artistas" else 15.0
irpf = st.number_input("¿Cuál es tu IRPF? (0 para mínimo)", value=irpf_sugerido, step=0.5)

st.divider()
st.subheader("Otros conceptos")

# --- SISTEMA DE EXTRAS ---
with st.expander("➕ Añadir Horas Extras / Festivas"):
    col_qty, col_mult = st.columns(2)
    with col_qty:
        e_qty = st.number_input("¿Cuántas?", min_value=0.0, step=1.0, format="%.f")
    with col_mult:
        e_mult = st.number_input("¿Factor multiplicador? (Ej. 1,5)", min_value=1.0, value=1.5, step=0.1)
    
    e_tipo = st.radio("¿Qué tipo de hora es?", ('Hora Extra', 'Festiva, otras...'))
    
    if st.button("Añadir Horas"):
        if e_qty > 0:
            ss_rate = 0.047 if 'Extra' in e_tipo else 0.0653
            bruto_t = (precio_hora_base * e_mult) * e_qty
            neto_t = bruto_t * (1 - ss_rate - (irpf/100))
            st.session_state.extras_lista.append({
                'desc': f"{e_qty}h {e_tipo} (x{e_mult})",
                'bruto': bruto_t,
                'neto': neto_t
            })

# --- SISTEMA DE DIETAS ---
with st.expander("✈️ Añadir Dietas"):
    c1, c2 = st.columns(2)
    if c1.button("Media comida (14,02€)"): st.session_state.dietas_lista.append(("Media comida", 14.02))
    if c2.button("Media cena (16,36€)"): st.session_state.dietas_lista.append(("Media cena", 16.36))
    if c1.button("Completa sin pernocta (30,38€)"): st.session_state.dietas_lista.append(("Sin pernocta", 30.38))
    if c2.button("Completa con pernocta (51,39€)"): st.session_state.dietas_lista.append(("Con pernocta", 51.39))

# --- JORNADA ESPECIAL ---
especial = st.checkbox("¿Alguna jornada especial? (+20€)")
especiales_qty = 0
if especial:
    especiales_qty = st.number_input("¿Cuántas?", min_value=1, step=1)

# --- MOSTRAR ACUMULADOS Y BORRAR ---
if st.session_state.extras_lista or st.session_state.dietas_lista:
    st.write("---")
    st.write("**Lista de añadidos:**")
    
    for i, ex in enumerate(st.session_state.extras_lista):
        col_txt, col_btn = st.columns([0.8, 0.2])
        col_txt.write(f"⚡️ {ex['desc']}")
        if col_btn.button("x", key=f"ex_{i}"):
            st.session_state.extras_lista.pop(i)
            st.rerun()
            
    for i, dt in enumerate(st.session_state.dietas_lista):
        col_txt, col_btn = st.columns([0.8, 0.2])
        col_txt.write(f"✈️ {dt[0]} ({dt[1]}€)")
        if col_btn.button("x", key=f"dt_{i}"):
            st.session_state.dietas_lista.pop(i)
            st.rerun()

# --- LIQUIDACIÓN ---
st.write("---")
liq_opcion = st.selectbox("¿Las vacaciones y el finiquito van aparte?", 
                         ['No, calcular', 'Ambas', 'Sólo vacaciones', 'Sólo finiquito'])

# --- CÁLCULO FINAL ---
if st.button("🚀 CALCULAR TOTAL"):
    # Base
    b_base = (bruto_dia * jornadas) + (especiales_qty * 20)
    n_base = b_base * (1 - 0.0653 - (irpf/100))
    
    # Extras
    total_extras_neto = sum(item['neto'] for item in st.session_state.extras_lista)
    total_extras_bruto = sum(item['bruto'] for item in st.session_state.extras_lista)
    
    # Dietas
    total_dietas = sum(item[1] for item in st.session_state.dietas_lista)
    
    # Liquidación
    base_liq = bruto_dia * jornadas
    v_bruto = (base_liq * 0.07) if (liq_opcion == 'Ambas' or liq_opcion == 'Sólo vacaciones') else 0
    f_bruto = (base_liq * 0.0333) if (liq_opcion == 'Ambas' or liq_opcion == 'Sólo finiquito') else 0
    temp_liq_bruta = v_bruto + f_bruto
    vaca_finiquito_neto = temp_liq_bruta * (1 - (irpf/100))
    
    total_final = n_base + total_extras_neto + total_dietas + vaca_finiquito_neto

    # RESUMEN (Textos idénticos al bot)
    st.subheader("💰 Resumen Final 💰")
    st.write(f"📅 **Base ({jornadas} días):**")
    st.write(f"   • {n_base:.2f}€ netos (Bruto: {b_base:.2f}€)")
    
    if total_extras_neto > 0:
        st.write(f"⚡️ **Extras/Festivas:**")
        st.write(f"   • {total_extras_neto:.2f}€ netos (Bruto: {total_extras_bruto:.2f}€)")
        
    if total_dietas > 0:
        st.write(f"✈️ **Dietas:** {total_dietas:.2f}€")
        
    if vaca_finiquito_neto > 0:
        st.write(f"📄 **Liquidación:**")
        st.write(f"   • {vaca_finiquito_neto:.2f}€ netos (Bruto: {temp_liq_bruta:.2f}€)")
        
    st.divider()
    st.subheader(f"🚀 Total: {total_final:.2f}€")

if st.button("🔄 Nuevo cálculo"):
    st.session_state.extras_lista = []
    st.session_state.dietas_lista = []
    st.rerun()
