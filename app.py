import streamlit as st
from datetime import datetime
import dola     
import base64 # <-- Añade esta línea

# Importamos la función que creaste en el otro archivo
from generar_pdf import generar_pdf_con_chrome

st.set_page_config(page_title="Generador de Cotizaciones", layout="wide")
st.title("Registro de Ventas")

# --- SECCIÓN 1: DATOS GLOBALES ---
col1, col2 , col3 = st.columns(3)
with col1:
    cliente = st.text_input("Nombre del Cliente")
with col2:
    # Selector de opciones
    opcion_tasa = st.radio(
        "Tipo de Tasa", 
        ["BCV", "Paralelo"], 
        horizontal=True # Los pone uno al lado del otro
    )
    
    # Asignamos la variable dependiendo de lo que elija el usuario
    if opcion_tasa == "BCV":
        tasa_a_usar = dola.tasaBCV()
    else:
        tasa_a_usar = dola.tasaParalelo()

    # Mostramos el input numérico
    tasa_dolar = st.number_input("Tasa del Dólar (Bs.)", min_value=0.0, value=tasa_a_usar, step=0.5)
with col3:
    Porcentaje = st.number_input("Porcentaje(%)", min_value=0, value=10, step=10)


descripcion_proyecto = st.text_area("Descripción del Proyecto")

st.markdown("---")
st.subheader("Detalles de Venta")

if 'num_filas' not in st.session_state:
    st.session_state.num_filas = 1

def agregar_fila():
    st.session_state.num_filas += 1

total_acumulado_usd = 0.0

# Aquí guardaremos las filas para enviarlas al PDF
lista_ventas_pdf = []

for i in range(st.session_state.num_filas):
    st.markdown(f"**Venta #{i+1}**")
    c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 1, 1, 1, 1])

    with c1:
        cantidad = st.number_input("Cantidad", min_value=1, value=1, key=f"cant_{i}")
    with c2:
        desc_venta = st.text_input("Descripción de la venta", key=f"desc_{i}")
    with c3:
        # Dividimos la columna 3 en dos sub-columnas internas
        col_h, col_m = st.columns(2)
        with col_h:
            horas = st.number_input("Hrs", min_value=0, value=0, step=1, key=f"h_{i}")
        with col_m:
            # Los minutos están restringidos de 0 a 59
            minutos = st.number_input("Min", min_value=0, max_value=59, value=0, step=1, key=f"m_{i}")
        

        tiempo = horas + (minutos / 60.0)
    # ---------------------------
    with c4:
        consumo = st.number_input("Consumo (g)", min_value=0.0, value=0.0, step=10.0, key=f"consumo_{i}")

# --- TUS CUENTAS MATEMÁTICAS ---
    constante_consumo = 35 * (consumo / 1000)
    consumo_horas = tiempo * 1.5
    total_consumo = constante_consumo + consumo_horas
    total_consumo = total_consumo * (dola.tasaParalelo() / dola.tasaBCV())
    total_consumo = total_consumo / (1 - (Porcentaje / 100))

    with c5:
        # 1. Leemos el estado del interruptor en la memoria ANTES de dibujarlo.
        # Si es la primera vez que carga, le decimos que por defecto sea False.
        editar_precio = st.session_state.get(f"editar_{i}", False)
        
        # 2. Dibujamos la casilla PRIMERO para que se alinee con las de la izquierda.
        if editar_precio:
            precio_u = st.number_input(
                "Precio/Und ($)", 
                min_value=0.0, 
                value=float(total_consumo), 
                step=1.0, 
                key=f"precio_manual_{i}"
            )
        else:
            st.session_state[f"precio_auto_{i}"] = float(total_consumo)
            precio_u = st.number_input(
                "Precio/Und ($)", 
                min_value=0.0, 
                disabled=True, 
                key=f"precio_auto_{i}"
            )
            
        # 3. Dibujamos el interruptor ABAJO. 
        # Al darle clic, actualizará la memoria y recargará la página automáticamente.
        st.toggle("Manual", key=f"editar_{i}")

    # El cálculo de los subtotales queda intacto
    subtotal_usd = cantidad * precio_u
    subtotal_bs = subtotal_usd * tasa_dolar
    total_acumulado_usd += subtotal_usd

    with c6:
        st.metric(label="Subtotal", value=f"${subtotal_usd:.2f}", delta=f"{subtotal_bs:.2f} Bs.", delta_color="off")

    # Guardamos los datos de esta fila específica en la lista
    lista_ventas_pdf.append({
        "cantidad": cantidad,
        "descripcion": desc_venta,
        "consumo": consumo,
        "tiempo": tiempo,
        "precio_u_usd": precio_u,
        "precio_u_bs": precio_u * tasa_dolar,
        "subtotal_usd": subtotal_usd,
        "subtotal_bs": subtotal_bs
    })

st.button("➕ Añadir otra fila de venta", on_click=agregar_fila)
st.markdown("---")

# --- SECCIÓN 3: OPCIONES ADICIONALES ---
st.subheader("Opciones Adicionales")
col_envio, col_desc = st.columns(2)

with col_envio:
    con_envio = st.checkbox("📦 ¿Se hará envío?")
    costo_envio = st.number_input("Costo del envío ($)", min_value=0.0, value=0.0, step=1.0) if con_envio else 0.0

with col_desc:
    con_descuento = st.checkbox("🏷️ ¿Aplicar descuento?")
    porcentaje_descuento = st.number_input("Porcentaje de descuento (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0) if con_descuento else 0.0

st.markdown("---")

# --- SECCIÓN 4: RESUMEN TOTAL ---
st.subheader("Resumen Total")

subtotal_general_usd = total_acumulado_usd
monto_descuento_usd = (subtotal_general_usd + costo_envio) * (porcentaje_descuento / 100)
total_final_usd = (subtotal_general_usd + costo_envio) - monto_descuento_usd
total_final_bs = total_final_usd * tasa_dolar

if con_descuento and porcentaje_descuento > 0:
    st.write(f"**Subtotal (Ventas + Envío):** ${subtotal_general_usd + costo_envio:.2f}")
    st.write(f"**Descuento aplicado ({porcentaje_descuento}%):** -${monto_descuento_usd:.2f}")

st.success(f"**Total a Pagar:** ${total_final_usd:.2f}  |  {total_final_bs:.2f} Bs.")

st.markdown("---")

# --- SECCIÓN 5: GENERACIÓN DE PDF ---
st.subheader("📄 Exportar Documento")
with open("fondo.png", "rb") as img_file:
    fondo_b64 = base64.b64encode(img_file.read()).decode('utf-8')

with open("logo.png", "rb") as image_file:
    imagen_codificada = base64.b64encode(image_file.read()).decode('utf-8')

# Empaquetamos toda la información para enviarla a Jinja2
datos_para_pdf = {
    "logo_base64": imagen_codificada,
    "fondo_base64": fondo_b64,
    "fecha": datetime.now().strftime("%d/%m/%Y"),
    "cliente_nombre": cliente,
    "cliente_proyecto": descripcion_proyecto,
    "lista_ventas": lista_ventas_pdf,
    "tasa_cambio": tasa_dolar,
    "resumen_subtotal_usd": subtotal_general_usd,
    "resumen_subtotal_bs": subtotal_general_usd * tasa_dolar,
    "resumen_descuento_usd": monto_descuento_usd,
    "resumen_descuento_bs": monto_descuento_usd * tasa_dolar,
    "resumen_envio_usd": costo_envio,
    "resumen_envio_bs": costo_envio * tasa_dolar,
    "resumen_total_usd": total_final_usd,
    "resumen_total_bs": total_final_bs
}

nombre_archivo_salida = f"Cotizacion_{cliente.replace(' ', '_')}.pdf"

# El botón de acción
if st.button("Generar PDF de Cotización", type="primary"):
    with st.spinner("Creando documento..."):
        pdf_file = generar_pdf_con_chrome('plantilla.html', datos_para_pdf)
        st.download_button(
                label="⬇️ Descargar PDF",
                data=pdf_file,
                file_name=nombre_archivo_salida,
                mime="application/pdf"
            )
        st.pdf(pdf_file)