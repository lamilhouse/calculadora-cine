{\rtf1\ansi\ansicpg1252\cocoartf2709
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
\
# Configuraci\'f3n de la p\'e1gina\
st.set_page_config(page_title="Calculadora N\'f3mina Cine", page_icon="\uc0\u55356 \u57260 ")\
\
st.title("\uc0\u55356 \u57260  Calculadora de n\'f3mina")\
\
# 1. Selecci\'f3n de contrato\
tipo_contrato = st.radio("\'bfQu\'e9 tipo de contrato tienes?", ("\uc0\u55357 \u56517  D\'edas sueltos", "\u55357 \u56787  Mes"))\
\
# Variables de estado para c\'e1lculos acumulados (dietas y extras)\
if 'extras_bruto' not in st.session_state: st.session_state.extras_bruto = 0\
if 'extras_neto' not in st.session_state: st.session_state.extras_neto = 0\
if 'dietas_total' not in st.session_state: st.session_state.dietas_total = 0\
\
# --- L\'d3GICA DE ENTRADA ---\
if tipo_contrato == "\uc0\u55357 \u56517  D\'edas sueltos":\
    bruto_dia = st.number_input("\'bfCu\'e1l es tu salario bruto diario?", min_value=0.0, step=10.0)\
    horas_base = st.number_input("\'bfDe cu\'e1ntas horas es la jornada?", min_value=1.0, value=8.0)\
    precio_hora_base = bruto_dia / horas_base if horas_base > 0 else 0\
    jornadas = st.number_input("\'bfCu\'e1ntas jornadas son?", min_value=1, step=1)\
else:\
    salario_mes_bruto = st.number_input("\'bfCu\'e1l es tu salario bruto mensual?", min_value=0.0, step=100.0)\
    h_sem = st.number_input("\'bfHoras semanales?", min_value=1.0, value=40.0)\
    bruto_dia = salario_mes_bruto / 30\
    precio_hora_base = (bruto_dia * 7) / h_sem\
    jornadas = st.number_input("\'bfCu\'e1ntos d\'edas has trabajado?", min_value=1, max_value=30, value=30)\
\
# --- R\'c9GIMEN E IRPF ---\
col1, col2 = st.columns(2)\
with col1:\
    regimen = st.selectbox("R\'e9gimen SS", ["General", "Artistas"])\
with col2:\
    irpf_default = 2.0 if regimen == "Artistas" else 15.0\
    irpf = st.number_input("IRPF (%)", value=irpf_default)\
\
# --- EXTRAS Y DIETAS (Interfaz simplificada) ---\
st.subheader("\uc0\u10133  A\'f1adidos")\
with st.expander("A\'f1adir Horas Extras / Festivas"):\
    qty = st.number_input("Cantidad de horas", min_value=0.0)\
    mult = st.number_input("Factor multiplicador (ej. 1.5)", value=1.5)\
    tipo_h = st.radio("Tipo", ["Hora Extra", "Festiva / Otras"])\
    if st.button("A\'f1adir estas horas"):\
        ss_rate = 0.047 if tipo_h == "Hora Extra" else 0.0653\
        b_tramo = (precio_hora_base * mult) * qty\
        n_tramo = b_tramo * (1 - ss_rate - (irpf/100))\
        st.session_state.extras_bruto += b_tramo\
        st.session_state.extras_neto += n_tramo\
        st.success(f"A\'f1adidos \{b_tramo:.2f\}\'80 brutos")\
\
# Especiales y Liquidaci\'f3n\
esp = st.checkbox("\'bfJornada especial? (+20\'80)")\
especiales_qty = st.number_input("\'bfCu\'e1ntas especiales?", min_value=0, step=1) if esp else 0\
\
liq = st.selectbox("\'bfVacaciones y finiquito van aparte?", ["No", "Ambas", "S\'f3lo vacaciones", "S\'f3lo finiquito"])\
\
# --- C\'c1LCULO FINAL ---\
if st.button("\uc0\u55357 \u56960  CALCULAR TOTAL"):\
    base_liq = bruto_dia * jornadas\
    v_bruto = (base_liq * 0.07) if liq in ["Ambas", "S\'f3lo vacaciones"] else 0\
    f_bruto = (base_liq * 0.0333) if liq in ["Ambas", "S\'f3lo finiquito"] else 0\
    liq_bruta = v_bruto + f_bruto\
    liq_neta = liq_bruta * (1 - (irpf/100))\
    \
    b_base = (bruto_dia * jornadas) + (especiales_qty * 20)\
    n_base = b_base * (1 - 0.0653 - (irpf/100))\
    \
    total_final = n_base + st.session_state.extras_neto + liq_neta\
\
    st.divider()\
    st.header(f"Total Neto: \{total_final:.2f\}\'80")\
    \
    col_a, col_b = st.columns(2)\
    with col_a:\
        st.write(f"**Base (\{jornadas\} d\'edas):** \{n_base:.2f\}\'80")\
        st.write(f"**Extras:** \{st.session_state.extras_neto:.2f\}\'80")\
    with col_b:\
        st.write(f"**Liquidaci\'f3n:** \{liq_neta:.2f\}\'80")\
        st.write(f"**Bruto base:** \{b_base:.2f\}\'80")\
\
if st.button("\uc0\u55357 \u56580  Reiniciar"):\
    st.session_state.extras_bruto = 0\
    st.session_state.extras_neto = 0\
    st.rerun()}