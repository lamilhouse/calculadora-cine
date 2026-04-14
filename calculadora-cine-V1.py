import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Calculadora Nómina Cine", page_icon="🎬")

st.title("🎬 Calculadora de nómina")

# 1. Selección de contrato
tipo_contrato = st.radio("¿Qué tipo de contrato tienes?", ("📅 Días sueltos", "🗓 Mes"))

# Variables de estado para cálculos acumulados (dietas y extras)
if 'extras_bruto' not in st.session_state: st.session_state.extras_bruto = 0
if 'extras_neto' not in st.session_state: st.session_state.extras_neto = 0
if 'dietas_total' not in st.session_state: st.session_state.dietas_total = 0

# --- LÓGICA DE ENTRADA ---
if tipo_contrato == "📅 Días sueltos":
    bruto_dia = st.number_input("¿Cuál es tu salario bruto diario?", min_value=0.0, step=10.0)
    horas_base = st.number_input("¿De cuántas horas es la jornada?", min_value=1.0, value=8.0)
    precio_hora_base = bruto_dia / horas_base if horas_base > 0 else 0
    jornadas = st.number_input("¿Cuántas jornadas son?", min_value=1, step=1)
else:
    salario_mes_bruto = st.number_input("¿Cuál es tu salario bruto mensual?", min_value=0.0, step=100.0)
    h_sem = st.number_input("¿Horas semanales?", min_value=1.0, value=40.0)
    bruto_dia = salario_mes_bruto / 30
    precio_hora_base = (bruto_dia * 7) / h_sem
    jornadas = st.number_input("¿Cuántos días has trabajado?", min_value=1, max_value=30, value=30)

# --- RÉGIMEN E IRPF ---
col1, col2 = st.columns(2)
with col1:
    regimen = st.selectbox("Régimen SS", ["General", "Artistas"])
with col2:
    irpf_default = 2.0 if regimen == "Artistas" else 15.0
    irpf = st.number_input("IRPF (%)", value=irpf_default)

# --- EXTRAS Y DIETAS (Interfaz simplificada) ---
st.subheader("➕ Añadidos")
with st.expander("Añadir Horas Extras / Festivas"):
    qty = st.number_input("Cantidad de horas", min_value=0.0)
    mult = st.number_input("Factor multiplicador (ej. 1.5)", value=1.5)
    tipo_h = st.radio("Tipo", ["Hora Extra", "Festiva / Otras"])
    if st.button("Añadir estas horas"):
        ss_rate = 0.047 if tipo_h == "Hora Extra" else 0.0653
        b_tramo = (precio_hora_base * mult) * qty
        n_tramo = b_tramo * (1 - ss_rate - (irpf/100))
        st.session_state.extras_bruto += b_tramo
        st.session_state.extras_neto += n_tramo
        st.success(f"Añadidos {b_tramo:.2f}€ brutos")

# Especiales y Liquidación
esp = st.checkbox("¿Jornada especial? (+20€)")
especiales_qty = st.number_input("¿Cuántas especiales?", min_value=0, step=1) if esp else 0

liq = st.selectbox("¿Vacaciones y finiquito van aparte?", ["No", "Ambas", "Sólo vacaciones", "Sólo finiquito"])

# --- CÁLCULO FINAL ---
if st.button("🚀 CALCULAR TOTAL"):
    base_liq = bruto_dia * jornadas
    v_bruto = (base_liq * 0.07) if liq in ["Ambas", "Sólo vacaciones"] else 0
    f_bruto = (base_liq * 0.0333) if liq in ["Ambas", "Sólo finiquito"] else 0
    liq_bruta = v_bruto + f_bruto
    liq_neta = liq_bruta * (1 - (irpf/100))
    
    b_base = (bruto_dia * jornadas) + (especiales_qty * 20)
    n_base = b_base * (1 - 0.0653 - (irpf/100))
    
    total_final = n_base + st.session_state.extras_neto + liq_neta

    st.divider()
    st.header(f"Total Neto: {total_final:.2f}€")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write(f"**Base ({jornadas} días):** {n_base:.2f}€")
        st.write(f"**Extras:** {st.session_state.extras_neto:.2f}€")
    with col_b:
        st.write(f"**Liquidación:** {liq_neta:.2f}€")
        st.write(f"**Bruto base:** {b_base:.2f}€")

if st.button("🔄 Reiniciar"):
    st.session_state.extras_bruto = 0
    st.session_state.extras_neto = 0
    st.rerun()
