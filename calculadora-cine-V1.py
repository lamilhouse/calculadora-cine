import streamlit as st

# Configuración de página
st.set_page_config(page_title="Calculadora Nómina Cine", page_icon="🎬")

# --- ESTILO CSS DEFINITIVO ---
st.markdown("""
    <style>
    .streamlit-expanderHeader { display: none !important; }
    html, body, [class*="st-"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    div.stButton > button[kind="primary"] {
        background-color: #4682B4;
        color: white;
        border: none;
        border-radius: 8px;
        height: 3em;
    }
    div.stButton > button:not([kind="primary"]) {
        background-color: transparent;
        color: #4682B4;
        border: 1px solid #4682B4;
        border-radius: 8px;
        height: 3em;
    }
    div[data-testid="stHorizontalBlock"] {
        align-items: center !important;
    }
    div[data-testid="stHorizontalBlock"] button {
        border: none !important;
        background-color: transparent !important;
        color: #888 !important;
        box-shadow: none !important;
        padding: 0 !important;
        min-height: 0px !important;
        line-height: 1 !important;
    }
    .stMarkdown p {
        margin-top: 0px !important;
        margin-bottom: 2px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Calculadora de nómina")

# --- LÓGICA DE LIMPIEZA ---
if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0

def limpiar_todo():
    # Borramos todo y subimos el contador para regenerar llaves
    for key in list(st.session_state.keys()):
        if key != 'reset_counter':
            del st.session_state[key]
    st.session_state.reset_counter += 1

# Este ID hará que los widgets se reinicien de verdad
r_id = st.session_state.reset_counter

if 'extras_lista' not in st.session_state: st.session_state.extras_lista = []
if 'dietas' not in st.session_state: 
    st.session_state.dietas = {"comida": 0, "cena": 0, "sin": 0, "con": 0}

# --- DATOS BASE ---
tipo_contrato = st.radio("¿Qué tipo de contrato tienes?", ('📅 Días sueltos', '🗓 Mes'), key=f"tipo_{r_id}")

if 'Días sueltos' in tipo_contrato:
    bruto_dia = st.number_input("¿Cuál es tu salario bruto?", min_value=0.0, step=100.0, format="%g", key=f"bruto_dia_{r_id}")
    horas_base = st.number_input("¿De cuántas horas es la jornada?", min_value=1.0, value=8.0, step=1.0, format="%g", key=f"h_base_{r_id}")
    precio_hora_base = bruto_dia / horas_base if horas_base > 0 else 0
    jornadas = st.number_input("¿Cuántas jornadas son?", min_value=0.0, step=1.0, format="%g", key=f"jornadas_{r_id}")
else:
    salario_mes_bruto = st.number_input("¿Cuál es tu salario bruto?", min_value=0.0, step=100.0, format="%g", key=f"s_mes_{r_id}")
    h_sem = st.number_input("¿Horas semanales?", min_value=1.0, step=1.0, value=40.0, format="%g", key=f"h_sem_{r_id}")
    bruto_dia = salario_mes_bruto / 30
    precio_hora_base = (bruto_dia * 7) / h_sem
    mes_entero = st.radio("¿Has trabajado el mes entero?", ('Sí', 'No'), key=f"mes_entero_{r_id}")
    jornadas = 30.0 if mes_entero == 'Sí' else st.number_input("¿Cuántos días has trabajado?", min_value=0.0, max_value=30.0, step=1.0, format="%g", key=f"dias_mes_{r_id}")

regimen = st.selectbox("Selecciona Régimen de la SS", ["Artistas", "General"], key=f"regimen_{r_id}")
irpf_sugerido = 2 if regimen == "Artistas" else 15
irpf = st.number_input("¿Cuál es tu IRPF?", value=int(irpf_sugerido), step=1, format="%d", key=f"irpf_{r_id}")

st.write("### Otros conceptos")

# --- EXTRAS ---
with st.container(border=True):
    st.write("**Añadir Horas Extras / Festivas**")
    col_qty, col_mult = st.columns(2)
    e_qty = col_qty.number_input("¿Cuántas?", min_value=0.0, step=1.0, format="%g", key=f"e_qty_{r_id}")
    e_mult = col_mult.number_input("Factor (ej. 1,5)", min_value=1.0, value=1.5, step=0.1, format="%g", key=f"e_mult_{r_id}")
    e_tipo = st.radio("Tipo de hora", ('Hora Extra', 'Festiva, otras...'), key=f"e_tipo_{r_id}")
    
    if st.button("Añadir estas horas"):
        if e_qty > 0:
            ss_rate = 0.047 if 'Extra' in e_tipo else 0.0653
            bruto_t = (precio_hora_base * e_mult) * e_qty
            neto_t = bruto_t * (1 - ss_rate - (irpf/100))
            qty_label = f"{e_qty:g}".replace('.', ',')
            st.session_state.extras_lista.append({
                'desc': f"{qty_label}h {e_tipo} (x{e_mult:g})", 
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

# --- DIETAS ---
with st.container(border=True):
    st.write("**Añadir Dietas**")
    c1, c2 = st.columns(2)
    if c1.button("🌯 Media - comida (14,02€)"): st.session_state.dietas["comida"] += 1; st.rerun()
    if c1.button("🍽 Media - cena (16,36€)"): st.session_state.dietas["cena"] += 1; st.rerun()
    if c1.button("🚍 Sin pernocta (30,38€)"): st.session_state.dietas["sin"] += 1; st.rerun()
    if c1.button("💤 Con pernocta (51,39€)"): st.session_state.dietas["con"] += 1; st.rerun()
    
    d_str = []
    if st.session_state.dietas["comida"] > 0: d_str.append(f"🌯 x{st.session_state.dietas['comida']}")
    if st.session_state.dietas["cena"] > 0: d_str.append(f"🍽 x{st.session_state.dietas['cena']}")
    if st.session_state.dietas["sin"] > 0: d_str.append(f"🚍 x{st.session_state.dietas['sin']}")
    if st.session_state.dietas["con"] > 0: d_str.append(f"💤 x{st.session_state.dietas['con']}")
    
    if d_str:
        st.write("---")
        c_res, c_clr = st.columns([0.9, 0.1])
        c_res.write(f"{' | '.join(d_str)}")
        if c_clr.button("X", key=f"clr_dietas_{r_id}"):
            st.session_state.dietas = {k:0 for k in st.session_state.dietas}
            st.rerun()

especial = st.checkbox("¿Alguna jornada especial? (+20€)", key=f"check_esp_{r_id}")
especiales_qty = st.number_input("¿Cuántas?", min_value=1, step=1, format="%d", key=f"qty_esp_{r_id}") if especial else 0

plus_consec = st.checkbox("¿Plus de 4 jornadas especiales consecutivas? (+35€)", key=f"check_plus_{r_id}")
plus_consec_qty = st.number_input("¿Cuántos?", min_value=1, step=1, format="%d", key=f"qty_plus_{r_id}") if plus_consec else 0

liq_opcion = st.selectbox("¿Vacaciones y finiquito aparte?", ['Sí, calcular', 'Está incluido en el bruto', 'Vacaciones aparte', 'Finiquito aparte'], key=f"liq_val_{r_id}")

# --- PROCESADO ---
st.write("")
if st.button("Calcular total", type="primary", use_container_width=True):
    # Aquí b_base y base_liq usan las variables definidas arriba, funcionará perfecto
    b_base = (bruto_dia * jornadas) + (especiales_qty * 20) + (plus_consec_qty * 35)
    n_base = b_base * (1 - 0.0653 - (irpf/100))
    total_extras_neto = sum(item['neto'] for item in st.session_state.extras_lista)
    total_extras_bruto = sum(item['bruto'] for item in st.session_state.extras_lista)
    dietas_total = (st.session_state.dietas["comida"] * 14.02 + st.session_state.dietas["cena"] * 16.36 + st.session_state.dietas["sin"] * 30.38 + st.session_state.dietas["con"] * 51.39)
    
    base_liq = bruto_dia * jornadas
    v_bruto = (base_liq * 0.07) if liq_opcion in ['Sí, calcular', 'Vacaciones aparte'] else 0
    f_bruto = (base_liq * 0.0333) if liq_opcion in ['Sí, calcular', 'Finiquito aparte'] else 0
    liq_neta = (v_bruto + f_bruto) * (1 - (irpf/100))
    
    total_final = n_base + total_extras_neto + dietas_total + liq_neta

    st.markdown("### Resumen")
    dias_label = f"{jornadas:g}".replace('.', ',')
    st.write(f"📅 **Base ({dias_label} días) + Especiales/Plus:**")
    st.write(f"   • {n_base:.2f}€ netos (Bruto: {b_base:.2f}€)")
    if total_extras_neto > 0:
        st.write(f"⚡️ **Extras/Festivas:**")
        st.write(f"   • {total_extras_neto:.2f}€ netos (Bruto: {total_extras_bruto:.2f}€)")
    if dietas_total > 0:
        st.write(f"✈️ **Dietas:** {dietas_total:.2f}€")
    if liq_neta > 0:
        st.write(f"📄 **Liquidación:** {liq_neta:.2f}€ netos")
    st.markdown(f"## Total: {total_final:.2f}€")

for _ in range(3): st.write("")
st.button("Nuevo cálculo", use_container_width=True, on_click=limpiar_todo)

# --- SECCIÓN DE INFORMACIÓN, PRIVACIDAD Y CONTACTO ---
st.write("") 
st.write("---") 

with st.expander("ℹ️ Información, Privacidad y Contacto"):
    st.markdown("""

    ### Cómo tener la app en tu móvil
    Si quieres tener esta calculadora siempre a mano, puedes crear un **acceso directo** en tu pantalla de inicio:
    1. Abre el enlace desde el navegador de tu móvil
    2. Pulsa el botón **Compartir** (en iOS) o los **tres puntos** (en Android).
    3. Selecciona la opción **"Añadir a pantalla de inicio"**.
    4. Si no te aparece en el inicio la encontrarás entre tus apps como "Streamlit"

    ### Normativa y prácticas del sector
    Los cálculos se realizan tomando como referencia la normativa vigente (convenio colectivo, normativa de la Seguridad Social, tablas de IRPF, conceptos salariales estándar...). No obstante, nos encontraremos algún apartado donde la lógica de la app se basa en las prácticas más habituales y extendidas de nuestra industria, lo cual puede hacer que no coincida exactamente tu nómina con el resultado mostrado.  

    ### Privacidad
    Esta aplicación **no almacena ningún dato introducido**. Ni salarios, ni horas, ni retenciones. Al cerrar la pestaña del navegador o pulsar el botón "Nuevo cálculo", todos los datos introducidos desaparecen para siempre.  
    <br>
    **IMPORTANTE** 
    <br>
    Los resultados ofrecidos por esta calculadora son meramente informativos y orientativos. En ningún caso tienen carácter vinculante ni valor legal oficial. Esta herramienta no sustituye el asesoramiento de un profesional gestor o la información proporcionada por los departamentos de RRHH. El creador de esta aplicación no se hace responsable de discrepancias entre los resultados de la app y las nóminas reales.  
    <br>   
    👉 [**Envíanos tus comentarios, dudas, sugerencias...**](https://forms.gle/CWvr3USetYqbdam8A)
    """, unsafe_allow_html=True)
