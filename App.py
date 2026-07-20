import streamlit as st
import pandas as pd
import os
import shutil
import io
from fpdf import FPDF

# 1. LIBRERÍAS DE CONEXIÓN A MYSQL
import mysql.connector
from sqlalchemy import create_engine

# IMPORTACIÓN DE TUS MÓDULOS PROPIOS
from estilos import aplicar_estilos_css, renderizar_tarjeta_completa
from calculos import calcular_disco_requerido, seleccionar_disco_compatible, calcular_infraestructura_y_mano_obra

# Generación del PDF
def generar_pdf_propuesta(camara_final, grabador_final, disco_final, infra, num_camaras, metros_cable, total_cotizacion, alternativas_camaras, requiere_grabador, obtener_ruta_imagen_fn):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_auto_page_break(auto=True, margin=12)
    
    # Lista para rastrear imágenes temporales y borrarlas al finalizar
    imagenes_temporales = []
    
    def obtener_ruta_segura(ruta):
        if not ruta or str(ruta).startswith("http") or not os.path.exists(ruta):
            return None
        try:
            from PIL import Image
            import tempfile
            with Image.open(ruta) as img:
                img_rgb = img.convert("RGB")
                temp_dir = tempfile.gettempdir()
                # Nombre de archivo único temporal
                nombre_base = os.path.basename(ruta)
                temp_path = os.path.join(temp_dir, f"pdf_temp_{nombre_base}.jpg")
                img_rgb.save(temp_path, "JPEG", quality=90)
                imagenes_temporales.append(temp_path)
                return temp_path
        except Exception:
            return ruta

    # --- ENCABEZADO ---
    pdf.set_fill_color(34, 197, 94)
    pdf.rect(0, 0, 210, 6, 'F')
    
    pdf.ln(4)
    y_header = pdf.get_y()
    
    # Columna Izquierda: Logo / Título
    pdf.set_xy(10, y_header)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(34, 197, 94) # Verde
    pdf.cell(100, 7, "Sistemas Z".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(100, 4.5, "PROPUESTA TÉCNICA COMERCIAL".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    pdf.set_x(10)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(100, 3.5, "Solución optimizada por Sistema Experto".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    # Columna Derecha: Información de Contacto
    pdf.set_xy(110, y_header)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(34, 197, 94)
    pdf.cell(90, 4, "CONTACTO Y SOPORTE".encode('latin-1', 'replace').decode('latin-1'), align="R", ln=True)
    
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(51, 65, 85)
    
    pdf.set_x(110)
    pdf.cell(90, 3.5, "WhatsApp: 246 222 2429 | 248 200 6949".encode('latin-1', 'replace').decode('latin-1'), align="R", ln=True)
    pdf.set_x(110)
    pdf.cell(90, 3.5, "Llámanos: 246 462 3274 | 248 487 0880".encode('latin-1', 'replace').decode('latin-1'), align="R", ln=True)
    pdf.set_x(110)
    pdf.cell(90, 3.5, "Correo: ventas@sistemasz.com | Web: sistemasz.com".encode('latin-1', 'replace').decode('latin-1'), align="R", ln=True)
    
    pdf.set_xy(10, y_header + 16)
    pdf.set_draw_color(226, 232, 240)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3.5)

    def formatear_precio(val, multiplicador=1):
        try:
            if val is None or pd.isna(val) or float(val) == 0:
                return "Por cotizar"
            return f"${(float(val) * multiplicador):,.2f} MXN"
        except:
            return "Por cotizar"

    # --- 1. BLOQUES DE EQUIPAMIENTO CON IMÁGENES ---
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, "1. Equipamiento Recomendado", ln=True)
    pdf.ln(1)

    ancho_tarjeta = 61
    espacio_entre = 3
    alto_tarjeta = 55 
    x_inicio = 10
    
    x_actual = x_inicio
    y_actual = pdf.get_y()
    
    # --- TARJETA 1: Cámara ---
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(x_actual, y_actual, ancho_tarjeta, alto_tarjeta, 'DF')
    
    ruta_img_camara = obtener_ruta_imagen_fn(camara_final.get('Modelo'), "CAMARAS")
    ruta_segura_camara = obtener_ruta_segura(ruta_img_camara)
    if ruta_segura_camara:
        pdf.image(ruta_segura_camara, x=x_actual + (ancho_tarjeta - 25)/2, y=y_actual + 4, w=25, h=20)
    
    pdf.set_xy(x_actual + 3, y_actual + 27)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(34, 197, 94)
    pdf.cell(ancho_tarjeta - 6, 4, f"CÁMARA (x{num_camaras})".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    pdf.set_x(x_actual + 3)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(ancho_tarjeta - 6, 4, f"{camara_final.get('Modelo')}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    pdf.set_x(x_actual + 3)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 4, f"Marca: {camara_final.get('Marca')}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    pdf.set_xy(x_actual + 3, y_actual + alto_tarjeta - 6)
    pdf.set_font("Helvetica", "B", 10) 
    pdf.set_text_color(15, 23, 42)
    pdf.cell(ancho_tarjeta - 6, 4, formatear_precio(camara_final.get('Precio'), num_camaras), align="R")

    # --- TARJETA 2: Grabador ---
    if requiere_grabador and grabador_final is not None:
        x_actual += ancho_tarjeta + espacio_entre
        pdf.set_fill_color(248, 250, 252)
        pdf.rect(x_actual, y_actual, ancho_tarjeta, alto_tarjeta, 'DF')
        
        ruta_img_grab = obtener_ruta_imagen_fn(grabador_final.get('MODELO'), "GRABADORAS")
        ruta_segura_grab = obtener_ruta_segura(ruta_img_grab)
        if ruta_segura_grab:
            pdf.image(ruta_segura_grab, x=x_actual + (ancho_tarjeta - 28)/2, y=y_actual + 4, w=28, h=20)
            
        pdf.set_xy(x_actual + 3, y_actual + 27)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(34, 197, 94)
        pdf.cell(ancho_tarjeta - 6, 4, "GRABADOR CENTRAL", ln=True)
        
        pdf.set_x(x_actual + 3)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(ancho_tarjeta - 6, 4, f"{grabador_final.get('MODELO')}", ln=True)
        
        pdf.set_x(x_actual + 3)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(ancho_tarjeta - 6, 4, f"Marca: {grabador_final.get('MARCA')}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
        pdf.set_xy(x_actual + 3, y_actual + alto_tarjeta - 6)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(ancho_tarjeta - 6, 4, formatear_precio(grabador_final.get('PRECIO')), align="R")

    # --- TARJETA 3: Disco Duro ---
    if requiere_grabador and disco_final is not None and not disco_final.empty:
        x_actual += ancho_tarjeta + espacio_entre
        pdf.set_fill_color(248, 250, 252)
        pdf.rect(x_actual, y_actual, ancho_tarjeta, alto_tarjeta, 'DF')
        
        ruta_img_disco = obtener_ruta_imagen_fn(disco_final.get('Modelo'), "DISCO DURO")
        ruta_segura_disco = obtener_ruta_segura(ruta_img_disco)
        if ruta_segura_disco:
            pdf.image(ruta_segura_disco, x=x_actual + (ancho_tarjeta - 22)/2, y=y_actual + 4, w=22, h=20)
            
        pdf.set_xy(x_actual + 3, y_actual + 27)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(34, 197, 94)
        pdf.cell(ancho_tarjeta - 6, 4, "ALMACENAMIENTO", ln=True)
        
        pdf.set_x(x_actual + 3)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(ancho_tarjeta - 6, 4, f"{disco_final.get('Modelo')}", ln=True)
        
        pdf.set_x(x_actual + 3)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(ancho_tarjeta - 6, 4, f"Capacidad: {disco_final.get('Capacidad')}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
        pdf.set_xy(x_actual + 3, y_actual + alto_tarjeta - 6)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(ancho_tarjeta - 6, 4, formatear_precio(disco_final.get('Precio')), align="R")

    pdf.set_xy(x_inicio, y_actual + alto_tarjeta + 3)
    
    # --- 2. INFRAESTRUCTURA ---
    if infra["aplica"]:
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 7, "2. Materiales de Instalación y Accesorios", ln=True)
        pdf.ln(1)
        
        # Cabecera de Tabla
        pdf.set_fill_color(241, 245, 249)
        pdf.set_text_color(71, 85, 105)
        pdf.set_font("Helvetica", "B", 8.5)
        
        pdf.cell(85, 6, " Concepto / Descripción".encode('latin-1', 'replace').decode('latin-1'), border=1, fill=True)
        pdf.cell(30, 6, "Cantidad".encode('latin-1', 'replace').decode('latin-1'), border=1, align="C", fill=True)
        pdf.cell(35, 6, "Costo Unitario".encode('latin-1', 'replace').decode('latin-1'), border=1, align="R", fill=True)
        pdf.cell(40, 6, "Subtotal".encode('latin-1', 'replace').decode('latin-1'), border=1, align="R", fill=True, ln=True)
        
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(51, 65, 85)
        
        # Fila 1: Cable
        pdf.cell(85, 5.5, " Cable UTP Cat5e (Metros)".encode('latin-1', 'replace').decode('latin-1'), border=1)
        pdf.cell(30, 5.5, f"{metros_cable} m", border=1, align="C")
        pdf.cell(35, 5.5, "$10.00 MXN", border=1, align="R")
        pdf.cell(40, 5.5, formatear_precio(infra["costo_cable"]), border=1, align="R", ln=True)
        
        # Fila 2: Transceptores
        if "No requerido" not in str(infra["transceptor_modelo"]):
            pdf.cell(85, 5.5, f" Transceptores de Video: {infra['transceptor_modelo']}".encode('latin-1', 'replace').decode('latin-1'), border=1)
            pdf.cell(30, 5.5, f"{num_camaras} pares", border=1, align="C")
            costo_unit_trans = infra["transceptor_costo"] / num_camaras if num_camaras > 0 else 0
            pdf.cell(35, 5.5, formatear_precio(costo_unit_trans), border=1, align="R")
            pdf.cell(40, 5.5, formatear_precio(infra["transceptor_costo"]), border=1, align="R", ln=True)
            
        # Fila 3: Cajas
        pdf.cell(85, 5.5, " Cajas de derivación plásticas Heavy Duty".encode('latin-1', 'replace').decode('latin-1'), border=1)
        pdf.cell(30, 5.5, f"{infra['cajas_cantidad']} pzas", border=1, align="C")
        costo_unit_caja = infra["cajas_costo"] / infra["cajas_cantidad"] if infra["cajas_cantidad"] > 0 else 0
        pdf.cell(35, 5.5, formatear_precio(costo_unit_caja), border=1, align="R")
        pdf.cell(40, 5.5, formatear_precio(infra["cajas_costo"]), border=1, align="R", ln=True)
        
        # Fila 4: Fuente
        pdf.cell(85, 5.5, f" Fuente de Poder Regulada: {infra['fuente_modelo']}".encode('latin-1', 'replace').decode('latin-1'), border=1)
        pdf.cell(30, 5.5, "1 pza", border=1, align="C")
        pdf.cell(35, 5.5, formatear_precio(infra["fuente_costo"]), border=1, align="R")
        pdf.cell(40, 5.5, formatear_precio(infra["fuente_costo"]), border=1, align="R", ln=True)
        
        # Total infra
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.cell(150, 6, "Total Materiales e Infraestructura".encode('latin-1', 'replace').decode('latin-1'), border=1, align="R")
        pdf.cell(40, 6, formatear_precio(infra["costo_total_infraestructura"] - infra["costo_mano_obra"]), border=1, align="R", ln=True)
        
    pdf.ln(3)
    
    # --- 3. SERVICIOS Y MANO DE OBRA ---
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, "3. Servicios de Instalación y Configuración".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.ln(1)
    
    pdf.set_fill_color(241, 245, 249)
    pdf.set_text_color(71, 85, 105)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.cell(150, 6, " Concepto de Servicio".encode('latin-1', 'replace').decode('latin-1'), border=1, fill=True)
    pdf.cell(40, 6, "Subtotal".encode('latin-1', 'replace').decode('latin-1'), border=1, align="R", fill=True, ln=True)
    
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(150, 5.5, f" Mano de obra de instalacion, canalizacion y configuracion de {num_camaras} camara(s)".encode('latin-1', 'replace').decode('latin-1'), border=1)
    pdf.cell(40, 5.5, formatear_precio(infra["costo_mano_obra"]), border=1, align="R", ln=True)
    
    pdf.cell(150, 5.5, " Configuracion de aplicacion movil para monitoreo remoto".encode('latin-1', 'replace').decode('latin-1'), border=1)
    pdf.cell(40, 5.5, "INCLUIDO", border=1, align="R", ln=True)
    
    pdf.ln(4)
    
    # --- TOTAL COTIZACIÓN ---
    pdf.set_fill_color(240, 253, 244)
    pdf.rect(10, pdf.get_y(), 190, 15, 'F')
    
    pdf.set_xy(15, pdf.get_y() + 3.5)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(22, 163, 74)
    pdf.cell(90, 8, "INVERSIÓN TOTAL ESTIMADA:".encode('latin-1', 'replace').decode('latin-1'))
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(90, 8, formatear_precio(total_cotizacion), align="R", ln=True)
    
    pdf.ln(6)
    
    # --- 4. ALTERNATIVAS ---
    if alternativas_camaras is not None and not alternativas_camaras.empty:
        pdf.add_page()
        y_titulo = pdf.get_y() + 1 
        
        pdf.set_xy(x_inicio, y_titulo)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 5, "4. Opciones de Cámaras Alternativas", ln=True)
        
        y_tarjetas_inicio = pdf.get_y() + 5
        
        ancho_tarjeta_alt = 60
        alto_tarjeta_alt = 40  
        espacio_entre_alt = 5
        
        x_actual = x_inicio
        y_actual = y_tarjetas_inicio
        
        for seq_idx, (idx, alt_row) in enumerate(alternativas_camaras.iterrows()):
            if seq_idx > 0 and seq_idx % 3 == 0:
                x_actual = x_inicio
                y_actual += alto_tarjeta_alt + 10
                if y_actual > 250:
                    pdf.add_page()
                    y_actual = 20
            
            pdf.set_fill_color(248, 250, 252)
            pdf.set_draw_color(226, 232, 240)
            pdf.rect(x_actual, y_actual, ancho_tarjeta_alt, alto_tarjeta_alt, 'DF')
            
            modelo_alt = alt_row.get('Modelo')
            ruta_img_alt = obtener_ruta_imagen_fn(modelo_alt, "CAMARAS")
            ruta_segura_alt = obtener_ruta_segura(ruta_img_alt)
            if ruta_segura_alt:
                pdf.image(ruta_segura_alt, x=x_actual + (ancho_tarjeta_alt - 25)/2, y=y_actual + 3, w=25, h=15)
            
            pdf.set_xy(x_actual + 4, y_actual + 21)
            pdf.set_font("Helvetica", "B", 7.5)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(ancho_tarjeta_alt - 8, 3.5, "OPCIÓN ALTERNATIVA".encode('latin-1', 'replace').decode('latin-1'))
            
            pdf.set_xy(x_actual + 4, y_actual + 25)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(ancho_tarjeta_alt - 8, 4, f"{modelo_alt}".encode('latin-1', 'replace').decode('latin-1'))
            
            pdf.set_xy(x_actual + 4, y_actual + 29)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(100, 116, 139)
            marca_alt = alt_row.get('Marca', 'N/A')
            pdf.cell(ancho_tarjeta_alt - 8, 3.5, f"Marca: {marca_alt}".encode('latin-1', 'replace').decode('latin-1'))
            
            pdf.set_xy(x_actual + 4, y_actual + alto_tarjeta_alt - 5)
            pdf.set_font("Helvetica", "B", 9.5)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(ancho_tarjeta_alt - 8, 4, formatear_precio(alt_row.get('Precio'), 1), align="R")
            
            x_actual += ancho_tarjeta_alt + espacio_entre_alt
            
        pdf.set_xy(x_inicio, y_actual + alto_tarjeta_alt + 5)
        
    # --- SECCIÓN DE TÉRMINOS Y CONDICIONES (SISTEMAS Z) ---
    if pdf.get_y() > 230:
        pdf.add_page()
    else:
        pdf.ln(5)
        
    y_start = pdf.get_y()
    
    # Dibujar una línea divisoria decorativa verde
    pdf.set_draw_color(34, 197, 94)
    pdf.set_line_width(0.4)
    pdf.line(10, y_start, 200, y_start)
    pdf.ln(3.5)
    
    pdf.set_text_color(15, 23, 42)
    
    # Título Términos y Condiciones
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(34, 197, 94)
    pdf.cell(0, 4.5, "TÉRMINOS Y CONDICIONES".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(51, 65, 85)
    
    pdf.cell(0, 4.5, "- Duración de la cotización: 7 días naturales.".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 4.5, "- Pagos únicamente en sucursal.".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.multi_cell(0, 4, "- Las imágenes son ilustrativas, algunos accesorios o características incluidas en las imágenes pueden variar.".encode('latin-1', 'replace').decode('latin-1'))
    
    pdf.ln(2.5)
    y_next = pdf.get_y()
    
    # --- CUADRO DE SEGUIMIENTO Y FECHA ---
    pdf.set_fill_color(240, 253, 244)
    pdf.set_draw_color(187, 247, 208)
    pdf.rect(10, y_next, 190, 15, 'DF')
    
    from datetime import datetime
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    
    pdf.set_xy(13, y_next + 2.5)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(22, 163, 74)
    pdf.cell(100, 3.5, f"Fecha de cotización: {fecha_hoy}".encode('latin-1', 'replace').decode('latin-1'))
    
    pdf.set_xy(13, y_next + 7.5)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(21, 128, 61)
    pdf.cell(180, 4, "NOTA IMPORTANTE: Presentarse con este PDF en la sucursal para el seguimiento del proceso.".encode('latin-1', 'replace').decode('latin-1'))
    
    pdf.ln(10)
    
    # Obtener el PDF como string de caracteres (latin-1) y codificar a bytes para el buffer
    pdf_string = pdf.output(dest='S')
    pdf_bytes = pdf_string.encode('latin-1')
    buffer = io.BytesIO(pdf_bytes)
    
    # Limpiar imágenes temporales creadas
    for temp_p in imagenes_temporales:
        try:
            if os.path.exists(temp_p):
                os.remove(temp_p)
        except Exception:
            pass
            
    return buffer

# 2. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Catálogo Digital de Videovigilancia", layout="wide")
st.title("Catálogo Inteligente y Sistema Experto en Videovigilancia")

aplicar_estilos_css()

# 3. CONFIGURACIÓN DEL MOTOR DE BASE DE DATOS (MYSQL)
USUARIO = st.secrets["DB_USER"]
CONTRASEÑA = st.secrets["DB_PASS"]
HOST = st.secrets["DB_HOST"]
PUERTO = st.secrets["DB_PORT"]
BASE_DATOS = st.secrets["DB_NAME"]

@st.cache_resource
def obtener_engine():
    try:
        url_conexion = f"mysql+mysqlconnector://{USUARIO}:{CONTRASEÑA}@{HOST}:{PUERTO}/{BASE_DATOS}"
        # Se agregan pool_recycle y pool_pre_ping para evitar desconexiones por inactividad
        engine_creado = create_engine(url_conexion, pool_recycle=3600, pool_pre_ping=True)
        # Verificación inicial rápida para asegurar la conexión
        with engine_creado.connect() as conn:
            pass
        return engine_creado
    except Exception as e:
        st.error(f"Error crítico al conectar a la base de datos MySQL: {e}")
        return None

engine = obtener_engine()

# 4. FUNCIÓN PARA BUSCAR IMÁGENES
def obtener_ruta_imagen(modelo, tipo_producto):
    if pd.isna(modelo) or str(modelo).strip().lower() == 'nan':
        return "https://placehold.co/400x300/0f172a/94a3b8?text=Imagen+No+Disponible"
    
    nombre_seguro = str(modelo).replace("/", "_").strip()
    carpeta_mayusculas = str(tipo_producto).strip().upper()
    
    # Detecta la carpeta actual automáticamente de forma agnóstica al sistema operativo (Windows / Linux)
    ruta_base_completa = os.path.join(os.path.dirname(__file__), "IMAGENES")
    carpeta_destino = os.path.join(ruta_base_completa, carpeta_mayusculas)
    
    extensiones = [".jpg", ".jpeg", ".png", ".webp"]
    for ext in extensiones:
        ruta_posible = os.path.join(carpeta_destino, f"{nombre_seguro}{ext}")
        if os.path.exists(ruta_posible):
            return ruta_posible
            
    return "https://placehold.co/400x300/0f172a/94a3b8?text=Imagen+No+Disponible"

# 5. CARGA DE DATOS CENTRALIZADA CON MANEJO DE SESSION_STATE Y CACHÉ
@st.cache_data(ttl=600)
def cargar_tabla_mysql(nombre_tabla):
    if engine is None:
        return pd.DataFrame()
    try:
        query = f"SELECT * FROM {nombre_tabla}"
        df = pd.read_sql(query, con=engine)
        df = df.dropna(how='all')
        
        # Sincronización de ID convirtiendo la columna a numérico 
        col_id = next((c for c in df.columns if c.lower() == 'id'), None)
        if col_id:
            df[col_id] = pd.to_numeric(df[col_id], errors='coerce').fillna(0).astype(int)
            
        return df
    except Exception as e:
        st.error(f"Error al cargar la tabla {nombre_tabla} desde MySQL: {e}")
        return pd.DataFrame()
        
# Inicialización en Session State para renderizado 
if 'inventario_camaras' not in st.session_state:
    st.session_state['inventario_camaras'] = cargar_tabla_mysql("camaras")
if 'inventario_grabadoras' not in st.session_state:
    st.session_state['inventario_grabadoras'] = cargar_tabla_mysql("grabadoras")
if 'inventario_discos' not in st.session_state:
    st.session_state['inventario_discos'] = cargar_tabla_mysql("disco_duro")
if 'inventario_compatibilidad' not in st.session_state:
    st.session_state['inventario_compatibilidad'] = cargar_tabla_mysql("compatibilidad")

df_camaras = st.session_state['inventario_camaras']
df_grabadoras = st.session_state['inventario_grabadoras']
df_discos = st.session_state['inventario_discos']
df_comp = st.session_state['inventario_compatibilidad']

# Limpieza rápida de precios
if 'Precio' in df_camaras.columns: df_camaras['Precio'] = df_camaras['Precio'].fillna(0)
if 'PRECIO' in df_grabadoras.columns: df_grabadoras['PRECIO'] = df_grabadoras['PRECIO'].fillna(0)
if 'Precio' in df_discos.columns: df_discos['Precio'] = df_discos['Precio'].fillna(0)

# 6. ESTRUCTURA DE PESTAÑAS
(pestaña_asistente, pestaña_camaras, pestaña_grabadoras, 
 pestaña_discos, pestaña_admin) = st.tabs([
    "Asistente de Recomendación (IA)", 
    "Catálogo de Cámaras", 
    "Catálogo de Grabadoras (DVR/NVR)", 
    "Almacenamiento (Discos Duros)",
    "Administración"
])

# ==========================================
# SECCIÓN: ASISTENTE DE RECOMENDACIÓN (IA)
# ==========================================
with pestaña_asistente:
    st.header("Diseñador Automático de Sistemas de Seguridad")
    
    if df_comp.empty or df_camaras.empty:
        st.warning("Verifica la conexión a la base de datos MySQL y que las tablas contengan registros.")
    else:
        col_izq, col_der = st.columns([1, 2])
        
        with col_izq:
            st.subheader("Cuestionario")
            opciones_prioridad = df_comp['Prioridad_Cliente'].dropna().unique().tolist()
            prioridad_seleccionada = st.selectbox("1. ¿Qué tipo de solución necesitas?", opciones_prioridad)
            num_camaras = st.number_input("2. ¿Cuántas cámaras necesitas?", min_value=1, max_value=32, value=1)
            
            regla = df_comp[df_comp['Prioridad_Cliente'] == prioridad_seleccionada].iloc[0]
            requiere_grabador = str(regla.get('Requiere_Grabador', 'SI')).strip().upper() == 'SI'
            
            if requiere_grabador:
                entorno = st.selectbox("3. ¿Dónde se van a instalar?", ["Solo en Interiores", "Solo en Exteriores", "En ambos (Interiores y Exteriores)"])
                vision_nocturna = st.selectbox("4. ¿Cómo prefieres la visión en la noche?", ["Tradicional (Blanco y Negro / Infrarrojo)", "A Color 24/7 (Tecnología ColorVu / Luz Blanca)"])
                necesita_audio = st.selectbox("5. ¿Es necesario escuchar o grabar audio?", ["No es necesario", "Sí, en todas las cámaras"])
                dias_grabacion = st.slider("6. Días de historial de respaldo:", min_value=1, max_value=30, value=7)
            else:
                st.info("Nota: Esta categoría utiliza dispositivos autónomos e independientes. No requiere grabador central ni disco duro.")
                entorno, vision_nocturna, necesita_audio, dias_grabacion = "Ambos", "Tradicional", "No es necesario", 0
            
            metros_cable = st.number_input(
                "Metros de cable requeridos (Se recomienda por lo menos 50m por cámara):", 
                min_value=0, value=0, step=1, key="cable_libre_usuario"
            )
                
            boton_calcular = st.button("Generar Recomendación Experta", type="primary")

        with col_der:
            if boton_calcular:
                st.subheader("Propuesta Técnica Recomendada")
                
                cat_filtro = str(regla.get('Categoria_Filtro', '')).strip().lower()
                camaras_filtradas = df_camaras[df_camaras['Tipo'].astype(str).str.strip().str.lower().str.contains(cat_filtro, na=False)]
                
                if len(camaras_filtradas) > 0:
                    camaras_filtradas['Resolucion_Num'] = pd.to_numeric(
                        camaras_filtradas['Resolucion (MP)'].astype(str).str.replace(r'[^\d\.]', '', regex=True), errors='coerce'
                    )
                    camaras_filtradas = camaras_filtradas[camaras_filtradas['Resolucion_Num'] > 0.3]
                    
                    res_minima_val = None
                    for col_name in ['Resolucion (MP)_Minima', 'Resolucion_Minima', 'Resolucion (MP) (MP)_Minima']:
                        if col_name in regla:
                            res_minima_val = regla[col_name]
                            break
                    
                    if pd.notna(res_minima_val):
                        import re
                        numeros = re.findall(r'\d+\.?\d*', str(res_minima_val))
                        res_minima_num = float(numeros[0]) if numeros else 2.0
                        camaras_filtradas = camaras_filtradas[camaras_filtradas['Resolucion_Num'] >= res_minima_num]
                    
                    if requiere_grabador and len(camaras_filtradas) > 0:
                        if entorno == "Solo en Exteriores": 
                            temp_env = camaras_filtradas[camaras_filtradas['Interior/Exterior'].astype(str).str.lower().str.contains("exterior|ambos", na=False)]
                            if len(temp_env) > 0: camaras_filtradas = temp_env
                        elif entorno == "Solo en Interiores": 
                            temp_env = camaras_filtradas[camaras_filtradas['Interior/Exterior'].astype(str).str.lower().str.contains("interior|ambos", na=False)]
                            if len(temp_env) > 0: camaras_filtradas = temp_env
                        
                        if len(camaras_filtradas) > 0:
                            if "Color" in vision_nocturna: 
                                temp_vis = camaras_filtradas[camaras_filtradas['Iluminacion nocturna'].astype(str).str.lower().str.contains("luz blanca|colorvu|color|vu|cálida|calida", na=False)]
                                if len(temp_vis) > 0: camaras_filtradas = temp_vis
                            else: 
                                temp_vis = camaras_filtradas[camaras_filtradas['Iluminacion nocturna'].astype(str).str.lower().str.contains("infrarrojo|ir|exir|smart|led", na=False)]
                                if len(temp_vis) > 0: camaras_filtradas = temp_vis
                        
                        if len(camaras_filtradas) > 0 and necesita_audio == "Sí, en todas las cámaras": 
                            temp_aud = camaras_filtradas[camaras_filtradas['Microfono'].astype(str).str.lower().str.strip().isin(["si", "sí", "yes", "s", "1"])]
                            if len(temp_aud) > 0: camaras_filtradas = temp_aud

                if len(camaras_filtradas) > 0:
                    camaras_filtradas = camaras_filtradas.sort_values(by='Precio')
                    camara_final = camaras_filtradas.iloc[0]
                    alternativas_camaras = camaras_filtradas.iloc[1:3] if len(camaras_filtradas) > 1 else pd.DataFrame()
                    p_camara = float(camara_final.get('Precio', 0))
                    marca_camara_final = str(camara_final.get('Marca', '')).strip().lower()
                    
                    infra = calcular_infraestructura_y_mano_obra(
                        num_camaras=num_camaras, metros_cable=metros_cable, tipo_camara=camara_final.get('Tipo', 'Analoga')
                    )
                    
                    grabador_final = None
                    disco_final = None
                    tipo_camara_real = str(camara_final.get('Tipo', 'Cámara')).strip()

                    if not requiere_grabador:
                        st.success(f"Solución Autónoma Detectada: Equipos independientes tipo {cat_filtro.upper()}.")
                        costo_equipos = p_camara * num_camaras
                        total_cotizacion = costo_equipos + infra["costo_total_infraestructura"]
                        
                        c_unica, _ = st.columns([1, 1])
                        with c_unica:
                            ruta = obtener_ruta_imagen(camara_final.get('Modelo'), "CAMARAS")
                            renderizar_tarjeta_completa(
                                ruta_imagen=ruta, modelo=f"{camara_final.get('Modelo')} (x{num_camaras})",
                                marca=camara_final.get('Marca', 'Generico'), tipo=tipo_camara_real, precio=costo_equipos
                            )
                    else:
                        tipo_grabador_elegido = regla.get('Tipo_Grabador', 'DVR')
                        grabadores_filtrados = df_grabadoras[df_grabadoras['TIPO'].astype(str).str.strip().str.upper() == str(tipo_grabador_elegido).strip().upper()]
                        
                        if len(grabadores_filtrados) == 0:
                            grabadores_filtrados = df_grabadoras[df_grabadoras['TIPO'].astype(str).str.lower().str.contains(str(tipo_grabador_elegido).lower(), na=False)]
                        
                        grabador_final = None
                        cantidad_grabadores = 1
                        
                        if len(grabadores_filtrados) > 0:
                            # Asegurar que la columna de canales sea numérica
                            col_canales = next((c for c in grabadores_filtrados.columns if 'CANAL' in c.upper()), None)
                            if col_canales:
                                grabadores_filtrados[col_canales] = pd.to_numeric(grabadores_filtrados[col_canales], errors='coerce').fillna(0).astype(int)
                            else:
                                col_canales = 'CANALES'
                                if col_canales not in grabadores_filtrados.columns:
                                    grabadores_filtrados[col_canales] = 4
                            
                            # 1. PRIORIDAD 1: Buscar UN SOLO grabador de la MISMA MARCA con canales suficientes
                            mismo_y_capaz = grabadores_filtrados[
                                (grabadores_filtrados['MARCA'].astype(str).str.strip().str.lower() == marca_camara_final) & 
                                (grabadores_filtrados[col_canales] >= num_camaras)
                            ]
                            
                            if len(mismo_y_capaz) > 0:
                                grabador_final = mismo_y_capaz.sort_values(by='PRECIO').iloc[0]
                                cantidad_grabadores = 1
                            else:
                                # 2. PRIORIDAD 2: Buscar UN SOLO grabador de OTRA MARCA con canales suficientes
                                cualquier_marca_capaz = grabadores_filtrados[grabadores_filtrados[col_canales] >= num_camaras]
                                if len(cualquier_marca_capaz) > 0:
                                    grabador_final = cualquier_marca_capaz.sort_values(by='PRECIO').iloc[0]
                                    cantidad_grabadores = 1
                                else:
                                    # 3. PRIORIDAD 3: Ningún DVR individual alcanza. Se necesitan múltiples DVRs.
                                    # Buscamos el de mayor capacidad priorizando que sea de la misma marca
                                    mismo_marca_todos = grabadores_filtrados[grabadores_filtrados['MARCA'].astype(str).str.strip().str.lower() == marca_camara_final]
                                    
                                    if len(mismo_marca_todos) > 0:
                                        grabadores_ordenados = mismo_marca_todos.sort_values(by=col_canales, ascending=False)
                                    else:
                                        grabadores_ordenados = grabadores_filtrados.sort_values(by=col_canales, ascending=False)
                                    
                                    grabador_mayor_capacidad = grabadores_ordenados.iloc[0]
                                    canales_maximos = int(grabador_mayor_capacidad[col_canales])
                                    
                                    if canales_maximos > 0:
                                        import math
                                        cantidad_grabadores = math.ceil(num_camaras / canales_maximos)
                                    else:
                                        cantidad_grabadores = 1
                                        
                                    grabador_final = grabador_mayor_capacidad
                                    st.warning(f"⚠️ El número de cámaras ({num_camaras}) excede la capacidad de canales de un solo grabador. Se recomiendan **{cantidad_grabadores} grabadores** del modelo {grabador_final.get('MODELO')} ({canales_maximos} canales c/u).")
                        else:
                            grabador_final = df_grabadoras.iloc[0]
                            st.warning(f"⚠️ No se encontró grabador de tipo '{tipo_grabador_elegido}'. Se asignó uno genérico.")
                        
                        # CÁLCULO DE RESPALDO Y DISCO DURO (IGUAL AL NÚMERO DE REQUISITOS DE DVR)
                        res_calculo = str(camara_final.get('Resolucion (MP)', '2'))
                        tb_necesarios = calcular_disco_requerido(num_camaras, res_calculo, dias_grabacion)
                        disco_final = seleccionar_disco_compatible(df_discos, tb_necesarios)
                        
                        p_grabador = float(grabador_final.get('PRECIO', 0)) * cantidad_grabadores
                        
                        # REGLA DEL DISCO DURO: La cantidad de discos es exactamente igual a la cantidad de DVRs
                        cantidad_discos = cantidad_grabadores
                        p_disco = (float(disco_final.get('Precio', 0)) if not disco_final.empty else 0) * cantidad_discos
                        
                        # AJUSTE AUTOMÁTICO DE FUENTE DE PODER ADICIONAL EN INFRAESTRUCTURA
                        if cantidad_grabadores > 1:
                            fuente_costo_original = infra["fuente_costo"]
                            infra["fuente_costo"] = fuente_costo_original * cantidad_grabadores
                            infra["costo_total_infraestructura"] = (
                                infra["costo_cable"] + infra["cajas_costo"] + 
                                infra["transceptor_costo"] + infra["fuente_costo"] + 
                                infra["costo_mano_obra"]
                            )
                            infra["fuente_modelo"] = f"{infra['fuente_modelo']} (x{cantidad_grabadores} Unidades por Grabadores Múltiples)"

                        costo_equipos = (p_camara * num_camaras) + p_grabador + p_disco
                        total_cotizacion = costo_equipos + infra["costo_total_infraestructura"]
                        
                        st.success(f"Sistema Centralizado Diseñado Exitosamente (Cálculo de Respaldo: {tb_necesarios:.2f} TB necesarios):")
                        
                        # Formateo correcto de textos fijos para evitar duplicidad de tarjetas visuales en CSS
                        tipo_grabador_limpio = str(grabador_final.get('TIPO', 'Grabador'))
                        
                        if isinstance(disco_final, pd.DataFrame) and not disco_final.empty:
                            disco_final = disco_final.iloc[0]

                        tipo_disco_limpio = f"Disco Duro ({disco_final['Capacidad']})" if 'Capacidad' in disco_final and pd.notna(disco_final['Capacidad']) else "Almacenamiento"
                        marca_disco_real = str(disco_final['Marca']).strip() if 'Marca' in disco_final and pd.notna(disco_final['Marca']) else "Genérico"
                        
                        # --- RENDERIZADO DE LAS 3 TARJETAS (UN SOLO CUADRO POR COMPONENTE) ---
                        c1, c2, c3 = st.columns(3)
                        
                        with c1:
                            ruta_c = obtener_ruta_imagen(camara_final.get('Modelo'), "CAMARAS")
                            renderizar_tarjeta_completa(
                                ruta_imagen=ruta_c, 
                                modelo=f"{camara_final.get('Modelo')} (x{num_camaras})", 
                                marca=camara_final.get('Marca', 'Generico'), 
                                tipo=tipo_camara_real, 
                                precio=p_camara * num_camaras
                            )
                            
                        with c2:
                            ruta_g = obtener_ruta_imagen(grabador_final.get('MODELO'), "GRABADORAS")
                            # Colocamos el multiplicador directamente en la cadena del modelo
                            modelo_grabador_visual = f"{grabador_final.get('MODELO', 'N/A')} (x{cantidad_grabadores})" if cantidad_grabadores > 1 else str(grabador_final.get('MODELO', 'N/A'))
                            
                            renderizar_tarjeta_completa(
                                ruta_imagen=ruta_g, 
                                modelo=modelo_grabador_visual, 
                                marca=grabador_final.get('MARCA', 'Generico'), 
                                tipo=tipo_grabador_limpio, 
                                precio=p_grabador
                            )
                            
                        with c3:
                            ruta_d = obtener_ruta_imagen(disco_final.get('Modelo'), "DISCO DURO")
                            # Colocamos el multiplicador directamente en la cadena del modelo del disco duro
                            modelo_disco_visual = f"{disco_final.get('Modelo', 'No disponible')} (x{cantidad_discos})" if cantidad_discos > 1 else str(disco_final.get('Modelo', 'No disponible'))
                            
                            renderizar_tarjeta_completa(
                                ruta_imagen=ruta_d, 
                                modelo=modelo_disco_visual, 
                                marca=marca_disco_real, 
                                tipo=tipo_disco_limpio, 
                                precio=p_disco
                            )
                    
                    if infra["aplica"]:
                        st.write("---")
                        st.markdown("### Desglose de Infraestructura e Instalación")
                        col_inf1, col_inf2 = st.columns(2)
                        with col_inf1:
                            st.write(f"• **Cable de red/coaxial:** {metros_cable} metros. (+${infra['costo_cable']:,.2f} MXN)")
                            st.write(f"• **Cajas de derivación:** {infra['cajas_cantidad']} pzas Heavy Duty. (+${infra['cajas_costo']:,.2f} MXN)")
                        with col_inf2:
                            st.write(f"• **Transceptores (Baluns):** {infra['transceptor_modelo']}. (+${infra['transceptor_costo']:,.2f} MXN)")
                            st.write(f"• **Fuente de Poder:** {infra['fuente_modelo']}. (+${infra['fuente_costo']:,.2f} MXN)")
                        st.info(f"**Mano de obra técnica calificada:** +${infra['costo_mano_obra']:,.2f} MXN")
                    
                    st.markdown(f"## Inversión Total Estimada del Sistema: <b style='color:#22C55E;'>${total_cotizacion:,.2f} MXN</b>", unsafe_allow_html=True)

                    pdf_data = generar_pdf_propuesta(
                        camara_final=camara_final, grabador_final=grabador_final, disco_final=disco_final,
                        infra=infra, num_camaras=num_camaras, metros_cable=metros_cable, total_cotizacion=total_cotizacion,
                        alternativas_camaras=alternativas_camaras, requiere_grabador=requiere_grabador, obtener_ruta_imagen_fn=obtener_ruta_imagen
                    )
                    st.download_button(
                        label="Descargar Cotización en PDF", data=pdf_data, file_name=f"Cotizacion_{prioridad_seleccionada}_{num_camaras}Camaras.pdf",
                        mime="application/pdf", key="btn_descarga_pdf"
                    )

                    if not alternativas_camaras.empty:
                        st.write("---")
                        st.markdown("<h2 style='color: #FFFFFF; border-left: 5px solid #22C55E; padding-left: 10px;'>Alternativas de Cámaras Disponibles</h2>", unsafe_allow_html=True)
                        cols_alt = st.columns(2)
                        for idx, (_, alt_row) in enumerate(alternativas_camaras.reset_index().iterrows()):
                            with cols_alt[idx]:
                                ruta_alt = obtener_ruta_imagen(alt_row.get('Modelo'), "CAMARAS")
                                renderizar_tarjeta_completa(
                                    ruta_imagen=ruta_alt, modelo=alt_row.get('Modelo', 'N/A'),
                                    marca=alt_row.get('Marca', 'Generico'), tipo=str(alt_row.get('Tipo', 'Cámara')).strip(), precio=float(alt_row.get('Precio', 0))
                                )
                else:
                    st.error("No se encontraron equipos que coincidan con los criterios.")

# ==========================================
# FUNCIONES PARA DETALLES 
# ==========================================
@st.dialog("Ficha Técnica de Cámara")
def mostrar_detalle_camara(row):
    ruta = obtener_ruta_imagen(row.get('Modelo'), "CAMARAS")
    from estilos import obtener_src_imagen
    src_img = obtener_src_imagen(ruta)
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown(f'<img src="{src_img}" style="width:100%; border-radius:8px;">', unsafe_allow_html=True)
        if float(row.get('Precio', 0)) > 0: 
            st.markdown(f"### <b style='color:#22C55E;'>${float(row.get('Precio', 0)):,.2f} MXN</b>", unsafe_allow_html=True)
        else: 
            st.warning("Precio: Por cotizar")
    with col2:
        st.markdown(f"## {row.get('Modelo')}")
        st.markdown(f"**Marca:** {row.get('Marca')}")
        for columna in row.index:
            if columna.upper() not in ['MODELO', 'MARCA', 'PRECIO', 'ID', 'INDEX', 'LEVEL_0']:
                valor = row[columna]
                if pd.notna(valor) and str(valor).strip() != '' and str(valor).lower() != 'nan':
                    st.markdown(f"**{columna}:** {valor}")

@st.dialog("Ficha Técnica de Grabadora")
def mostrar_detalle_grabadora(row):
    ruta = obtener_ruta_imagen(row.get('MODELO'), "GRABADORAS")
    from estilos import obtener_src_imagen
    src_img = obtener_src_imagen(ruta)
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown(f'<img src="{src_img}" style="width:100%; border-radius:8px;">', unsafe_allow_html=True)
        if float(row.get('PRECIO', 0)) > 0: 
            st.markdown(f"### <b style='color:#22C55E;'>${float(row.get('PRECIO', 0)):,.2f} MXN</b>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"## {row.get('MODELO')}")
        st.markdown(f"**Marca:** {row.get('MARCA', 'N/A')}")
        st.markdown(f"**Tipo:** {row.get('TIPO', 'DVR/NVR')}")
        for col_name in row.index:
            if col_name.upper() not in ['MODELO', 'MARCA', 'TIPO', 'PRECIO', 'INDEX', 'LEVEL_0', 'ID']:
                val = row[col_name]
                if pd.notna(val) and str(val).strip() != '':
                    st.markdown(f"**{col_name.replace('_', ' ').title()}:** {val}")

@st.dialog("Ficha Técnica de Almacenamiento")
def mostrar_detalle_disco(row):
    ruta = obtener_ruta_imagen(row.get('Modelo'), "DISCO DURO")
    from estilos import obtener_src_imagen
    src_img = obtener_src_imagen(ruta)
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown(f'<img src="{src_img}" style="width:100%; border-radius:8px;">', unsafe_allow_html=True)
        if float(row.get('Precio', 0)) > 0: 
            st.markdown(f"### <b style='color:#22C55E;'>${float(row.get('Precio', 0)):,.2f} MXN</b>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"## {row.get('Modelo', 'N/A')}")
        st.markdown(f"**Marca:** {row.get('Marca', 'Genérico')}")
        st.markdown(f"**Capacidad:** Disco Duro ({row.get('Capacidad', 'N/A')})")

# ==========================================
# SECCIONES: CATÁLOGOS COMPLETOS
# ==========================================
with pestaña_camaras:
    if not df_camaras.empty:
        st.subheader(f"Inventario de Cámaras ({len(df_camaras)} modelos)")
        cols_c = st.columns(3)
        for index, row in df_camaras.reset_index().iterrows():
            with cols_c[index % 3]:
                ruta = obtener_ruta_imagen(row.get('Modelo'), "CAMARAS")
                tags = [f"{row.get('Resolucion (MP)')} MP", row.get('Interior/Exterior')]
                renderizar_tarjeta_completa(
                    ruta_imagen=ruta, modelo=row.get('Modelo', 'N/A'), marca=row.get('Marca', 'Genérico'),
                    tipo=row.get('Tipo', 'Cámara'), precio=float(row.get('Precio', 0)), datos_rapidos=[t for t in tags if pd.notna(t)]
                )
                if st.button(f"Ver ficha técnica", key=f"btn_cam_{index}", use_container_width=True):
                    mostrar_detalle_camara(row)

with pestaña_grabadoras:
    if not df_grabadoras.empty:
        st.subheader(f"Inventario de Grabadoras ({len(df_grabadoras)} modelos)")
        cols_g = st.columns(3)
        for index, row in df_grabadoras.reset_index().iterrows():
            with cols_g[index % 3]:
                ruta = obtener_ruta_imagen(row.get('MODELO'), "GRABADORAS")
                tags_g = [row.get('TIPO')]
                renderizar_tarjeta_completa(
                    ruta_imagen=ruta, modelo=row.get('MODELO', 'N/A'), marca=row.get('MARCA', 'Genérico'),
                    tipo=row.get('TIPO', 'DVR/NVR'), precio=float(row.get('PRECIO', 0)), datos_rapidos=tags_g
                )
                if st.button(f"Ver ficha técnica", key=f"btn_grab_{index}", use_container_width=True):
                    mostrar_detalle_grabadora(row)

with pestaña_discos:
    if not df_discos.empty:
        st.subheader(f"Inventario de Almacenamiento ({len(df_discos)} modelos)")
        cols_d = st.columns(3)
        for index, row in df_discos.reset_index().iterrows():
            with cols_d[index % 3]:
                ruta = obtener_ruta_imagen(row.get('Modelo'), "DISCO DURO")
                capacidad_val = row.get('Capacidad', 'N/A')
                renderizar_tarjeta_completa(
                    ruta_imagen=ruta, modelo=row.get('Modelo', 'N/A'), marca=row.get('Marca', 'Genérico'),                      
                    tipo=f"Disco Duro ({capacidad_val})", precio=float(row.get('Precio', 0)), datos_rapidos=[f"{capacidad_val}"]
                )
                if st.button(f"Ver ficha técnica", key=f"btn_disc_{index}", use_container_width=True):
                    mostrar_detalle_disco(row)

# ==========================================
# SECCIÓN: PANEL DE ADMINISTRACIÓN (CRUD)
# ==========================================
with pestaña_admin:
    st.header("Panel de Control de Inventario")
    
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
        
    if not st.session_state['autenticado']:
        col_login, _ = st.columns([1, 2])
        with col_login:
            st.subheader("Acceso Restringido")
            clave_ingresada = st.text_input("Introduce la contraseña de administrador:", type="password")
            if st.button("Iniciar Sesión", type="primary"):
                if clave_ingresada == "Sistemasz12":
                    st.session_state['autenticado'] = True
                    st.success("Acceso concedido.")
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta. Inténtalo de nuevo.")
                    
    else:
        col_vacia, col_logout = st.columns([5, 1])
        with col_logout:
            if st.button("Cerrar Sesion", use_container_width=True):
                st.session_state['autenticado'] = False
                st.rerun()
                
        st.markdown("### Gestion de Inventario Centralizado")
        tabla_a_gestionar = st.selectbox("Selecciona el catalogo que deseas gestionar:", ["Cámaras", "Grabadoras", "Discos Duros"])
        
        if tabla_a_gestionar == "Cámaras":
            nombre_tabla_sql = "camaras"
            carpeta_imagenes = "CAMARAS"
            key_session = "inventario_camaras"
            df_actual = df_camaras.copy()
            columna_id = "ID" if "ID" in df_actual.columns else "id"
            columna_modelo = "Modelo"
        elif tabla_a_gestionar == "Grabadoras":
            nombre_tabla_sql = "grabadoras"
            carpeta_imagenes = "GRABADORAS"
            key_session = "inventario_grabadoras"
            df_actual = df_grabadoras.copy()
            columna_id = "ID" if "ID" in df_actual.columns else "id"
            columna_modelo = "MODELO"
        else:
            nombre_tabla_sql = "disco_duro"
            carpeta_imagenes = "DISCOS"
            key_session = "inventario_discos"
            df_actual = df_discos.copy()
            columna_id = "ID" if "ID" in df_actual.columns else "id"
            columna_modelo = "Modelo"

        op_crear, op_editar, op_eliminar = st.tabs(["Anadir Registro", "Modificar Registro", "Quitar Registro"])

        # -----------------------------------------------------------------
        # OPERACIÓN: AÑADIR REGISTRO
        # -----------------------------------------------------------------
        with op_crear:
            st.markdown(f"#### Registrar nuevo articulo en: {tabla_a_gestionar}")
            
            with st.form(key=f"form_crear_{nombre_tabla_sql}", clear_on_submit=True):
                datos_nuevos = {}
                columnas_interes = [col for col in df_actual.columns if col.lower() != columna_id.lower()]
                
                val_modelo = st.text_input(f"{columna_modelo} (Obligatorio):", key="new_model_input")
                datos_nuevos[columna_modelo] = val_modelo
                
                for col in columnas_interes:
                    if col == columna_modelo: 
                        continue
                    if "precio" in col.lower() or "marca" in col.lower() or "tipo" in col.lower():
                        if "precio" in col.lower():
                            datos_nuevos[col] = st.number_input(f"{col}:", min_value=0.0, step=50.0, value=0.0)
                        else:
                            datos_nuevos[col] = st.text_input(f"{col}:")
                    else:
                        if "resolucion" in col.lower() and tabla_a_gestionar == "Cámaras":
                            datos_nuevos[col] = st.number_input(f"{col} (Numero sin MP):", min_value=0.0, step=1.0, value=2.0)
                        else:
                            datos_nuevos[col] = st.text_input(f"{col}:")
                            
                archivo_imagen = st.file_uploader("Cargar Imagen del Producto:", type=["jpg", "jpeg", "png", "webp"])
                boton_guardar_nuevo = st.form_submit_button("Guardar Producto en Sistema", type="primary")
                
                if boton_guardar_nuevo:
                    if val_modelo.strip() == "":
                        st.error(f"El campo '{columna_modelo}' es estrictamente obligatorio.")
                    else:
                        try:
                            # =========================================================
                            # ID subsecuente
                            # =========================================================
                            if not df_actual.empty and columna_id in df_actual.columns:
                                # Buscamos el ID máximo actual y le sumamos 1
                                id_maximo = pd.to_numeric(df_actual[columna_id], errors='coerce').max()
                                nuevo_id = int(id_maximo) + 1 if pd.notna(id_maximo) else 1
                            else:
                                nuevo_id = 1
                            
                            datos_nuevos[columna_id] = nuevo_id
                            

                            if archivo_imagen is not None:
                                nombre_archivo_limpio = "".join(c for c in val_modelo if c.isalnum() or c in (' ', '-', '_')).strip()
                                extension = os.path.splitext(archivo_imagen.name)[1]
                                nombre_final_imagen = f"{nombre_archivo_limpio}{extension}"
                                
                                folder_type = "DISCO DURO" if carpeta_imagenes == "DISCOS" else carpeta_imagenes
                                # Ruta agnóstica al sistema operativo
                                ruta_destino = os.path.join(os.path.dirname(__file__), "IMAGENES", folder_type, nombre_final_imagen)
                                os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                                
                                with open(ruta_destino, "wb") as f:
                                    f.write(archivo_imagen.getbuffer())

                                columna_imagen_db = next((c for c in df_actual.columns if any(k in c.lower() for k in ["imagen", "ruta", "url", "foto"])), None)
                                if columna_imagen_db:
                                    datos_nuevos[columna_imagen_db] = nombre_final_imagen
                            
                            # Enviamos el DataFrame incluyendo la columna ID
                            df_nuevo_reg = pd.DataFrame([datos_nuevos])
                            df_nuevo_reg.to_sql(nombre_tabla_sql, con=engine, if_exists='append', index=False)
                            
                            # Limpiamos cachés para sincronizar la app
                            st.cache_data.clear()
                            st.cache_resource.clear()
                            
                            # Recargamos los session states frescos
                            st.session_state['inventario_camaras'] = cargar_tabla_mysql("camaras")
                            st.session_state['inventario_grabadoras'] = cargar_tabla_mysql("grabadoras")
                            st.session_state['inventario_discos'] = cargar_tabla_mysql("disco_duro")
                            
                            st.success(f"Producto '{val_modelo}' añadido correctamente con ID subsecuente #{nuevo_id}.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al guardar el registro: {e}")

        # -----------------------------------------------------------------
        # OPERACIÓN: MODIFICAR REGISTRO (CON CONSERVACIÓN DE REEMPLAZO)
        # -----------------------------------------------------------------
        with op_editar:
            st.markdown(f"#### Modificar Ficha Técnica de {tabla_a_gestionar}")
            if df_actual.empty:
                st.info("No hay registros disponibles para editar.")
            else:
                lista_modelos = df_actual[columna_modelo].dropna().unique().tolist()
                modelo_a_editar = st.selectbox("Selecciona el artículo a editar:", lista_modelos, key="sb_edit_modelo")
                
                fila_original = df_actual[df_actual[columna_modelo] == modelo_a_editar].iloc[0]
                id_registro = fila_original[columna_id]
                
                with st.form(key=f"form_editar_{nombre_tabla_sql}"):
                    datos_editados = {}
                    columnas_interes = [col for col in df_actual.columns if col.lower() != columna_id.lower()]
                    
                    val_modelo_actual = str(fila_original[columna_modelo])
                    nuevo_modelo_input = st.text_input(f"{columna_modelo}:", value=val_modelo_actual)
                    datos_editados[columna_modelo] = nuevo_modelo_input
                    
                    columna_imagen_db = next((c for c in df_actual.columns if any(k in c.lower() for k in ["imagen", "ruta", "url", "foto"])), None)
                    
                    for col in columnas_interes:
                        if col == columna_modelo or col == columna_imagen_db: 
                            continue
                        valor_actual = fila_original[col]
                        valor_defecto_txt = "" if pd.isna(valor_actual) or str(valor_actual).lower() == 'nan' else str(valor_actual)
                        
                        try: valor_defecto_num = 0.0 if pd.isna(valor_actual) else float(valor_actual)
                        except: valor_defecto_num = 0.0
                            
                        if "precio" in col.lower() or "marca" in col.lower() or "tipo" in col.lower():
                            if "precio" in col.lower(): 
                                datos_editados[col] = st.number_input(f"{col}:", min_value=0.0, step=50.0, value=valor_defecto_num)
                            else: 
                                datos_editados[col] = st.text_input(f"{col}:", value=valor_defecto_txt)
                        else:
                            if "resolucion" in col.lower() and tabla_a_gestionar == "Cámaras":
                                datos_editados[col] = st.number_input(f"{col}:", min_value=0.0, step=1.0, value=valor_defecto_num)
                            else: 
                                datos_editados[col] = st.text_input(f"{col}:", value=valor_defecto_txt)
                                
                    archivo_imagen_nueva = st.file_uploader("Reemplazar o Actualizar Imagen Actual:", type=["jpg", "jpeg", "png", "webp"])
                    boton_actualizar = st.form_submit_button("Actualizar Registro Completo", type="primary")
                    
                    if boton_actualizar:
                        try:
                            nombre_limpio_viejo = "".join(c for c in val_modelo_actual if c.isalnum() or c in (' ', '-', '_')).strip()
                            nombre_limpio_nuevo = "".join(c for c in nuevo_modelo_input if c.isalnum() or c in (' ', '-', '_')).strip()
                            
                            folder_type = "DISCO DURO" if carpeta_imagenes == "DISCOS" else carpeta_imagenes
                            # Ruta agnóstica al sistema operativo
                            dir_fotos = os.path.join(os.path.dirname(__file__), "IMAGENES", folder_type)
                            
                            nombre_final_imagen = None

                            # --- CONTROL INTELIGENTE DE IMÁGENES: REEMPLAZO FÍSICO ---
                            if archivo_imagen_nueva is not None:
                                # Eliminar imágenes anteriores con el nombre base del artículo para no acumular duplicados
                                if os.path.exists(dir_fotos):
                                    for archivo in os.listdir(dir_fotos):
                                        nom_base, _ = os.path.splitext(archivo)
                                        if nom_base == nombre_limpio_viejo:
                                            try: os.remove(os.path.join(dir_fotos, archivo))
                                            except: pass
                                
                                ext = os.path.splitext(archivo_imagen_nueva.name)[1]
                                nombre_final_imagen = f"{nombre_limpio_nuevo}{ext}"
                                ruta_nueva = os.path.join(dir_fotos, nombre_final_imagen)
                                os.makedirs(dir_fotos, exist_ok=True)
                                with open(ruta_nueva, "wb") as f: 
                                    f.write(archivo_imagen_nueva.getbuffer())
                                    
                            else:
                                # Renombrado físico automático en el disco duro si se cambió el nombre del modelo
                                if nombre_limpio_viejo != nombre_limpio_nuevo and os.path.exists(dir_fotos):
                                    for archivo in os.listdir(dir_fotos):
                                        nom_base, ext = os.path.splitext(archivo)
                                        if nom_base == nombre_limpio_viejo:
                                            nombre_final_imagen = f"{nombre_limpio_nuevo}{ext}"
                                            shutil.move(os.path.join(dir_fotos, archivo), os.path.join(dir_fotos, nombre_final_imagen))
                                            break

                            if nombre_final_imagen and columna_imagen_db:
                                datos_editados[columna_imagen_db] = nombre_final_imagen
                            elif columna_imagen_db:
                                col_image_val = fila_original.get(columna_imagen_db)
                                if pd.notna(col_image_val) and str(col_image_val).strip() != "" and str(col_image_val).lower() != "nan":
                                    datos_editados[columna_imagen_db] = col_image_val

                            # Lanzamiento seguro de Query UPDATE dinámico
                            set_clause = ", ".join([f"`{col}` = :param_{i}" for i, col in enumerate(datos_editados.keys())])
                            query = f"UPDATE `{nombre_tabla_sql}` SET {set_clause} WHERE `{columna_id}` = :id_registro"
                            
                            parametros_sql = {}
                            for i, (col_name, val) in enumerate(datos_editados.items()):
                                if isinstance(val, str) and val.strip() == "":
                                    if any(k in col_name.upper() for k in ['PRECIO', 'RESOLUCION', 'CANALES', 'MAX', 'BAHIAS']): 
                                        parametros_sql[f"param_{i}"] = None
                                    else: 
                                        parametros_sql[f"param_{i}"] = ""
                                else:
                                    parametros_sql[f"param_{i}"] = val.item() if hasattr(val, 'item') else val
                                    
                            parametros_sql["id_registro"] = int(id_registro.item()) if hasattr(id_registro, 'item') else int(id_registro)
                            
                            from sqlalchemy import text
                            with engine.begin() as conexion: 
                                conexion.execute(text(query), parametros_sql)
                                
                            st.cache_data.clear()
                            st.cache_resource.clear()
                            st.session_state['inventario_camaras'] = cargar_tabla_mysql("camaras")
                            st.session_state['inventario_grabadoras'] = cargar_tabla_mysql("grabadoras")
                            st.session_state['inventario_discos'] = cargar_tabla_mysql("disco_duro")
                            
                            st.success("Registro modificado correctamente en la base de datos.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al actualizar el registro: {e}")

        # -----------------------------------------------------------------
        # OPERACIÓN: ELIMINAR REGISTRO
        # -----------------------------------------------------------------
        with op_eliminar:
            st.markdown(f"#### Dar de Baja Articulo de {tabla_a_gestionar}")
            if df_actual.empty:
                st.info("No hay registros disponibles para eliminar.")
            else:
                lista_modelos_del = df_actual[columna_modelo].dropna().unique().tolist()
                modelo_a_eliminar = st.selectbox("Selecciona el modelo que deseas remover:", lista_modelos_del, key="sb_del_modelo")
                
                fila_a_borrar = df_actual[df_actual[columna_modelo] == modelo_a_eliminar].iloc[0]
                id_a_borrar = fila_a_borrar[columna_id]
                
                st.warning(f"¿Deseas eliminar el modelo {modelo_a_eliminar}?")
                confirmacion = st.checkbox("Confirmo la remocion permanente de este articulo.")
                boton_eliminar = st.button("Proceder con la Baja Permanente", type="primary", disabled=not confirmacion)
                
                if boton_eliminar and confirmacion:
                    try:
                        from sqlalchemy import text
                        query = text(f"DELETE FROM `{nombre_tabla_sql}` WHERE `{columna_id}` = :id_target")
                        with engine.begin() as conexion: conexion.execute(query, {"id_target": int(id_a_borrar)})
                            
                        st.cache_data.clear()
                        st.cache_resource.clear()
                        st.session_state['inventario_camaras'] = cargar_tabla_mysql("camaras")
                        st.session_state['inventario_grabadoras'] = cargar_tabla_mysql("grabadoras")
                        st.session_state['inventario_discos'] = cargar_tabla_mysql("disco_duro")
                        
                        st.success(f"El modelo '{modelo_a_eliminar}' ha sido removido.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al eliminar el registro: {e}")