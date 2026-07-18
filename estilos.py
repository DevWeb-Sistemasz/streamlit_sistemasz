import streamlit as st
import base64
import os

def aplicar_estilos_css():
    st.markdown("""
        <style>
        .tarjeta-producto {
            background-color: #1E293B;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 16px;
            height: 460px; /* Incrementamos ligeramente para dar espacio a los datos clave */
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .img-tarjeta {
            width: 100%;
            height: 180px;
            object-fit: cover;
            border-radius: 8px;
            background-color: #0F172A;
        }
        .info-tarjeta {
            margin-top: 10px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }
        .titulo-producto {
            font-size: 1.15em;
            font-weight: bold;
            color: #FFFFFF;
            margin: 0 0 4px 0;
            line-height: 1.25em;
            height: 2.5em;
            overflow: hidden;
        }
        .detalles-producto {
            font-size: 0.85em;
            color: #94A3B8;
            margin: 0 0 8px 0;
            line-height: 1.4em;
        }
        .tag-caracteristica {
            display: inline-block;
            background-color: #334155;
            color: #E2E8F0;
            font-size: 0.75em;
            padding: 2px 8px;
            border-radius: 4px;
            margin-right: 4px;
            margin-bottom: 4px;
        }
        .precio-verde {
            color: #22C55E;
            font-size: 1.15em;
            font-weight: bold;
            margin-top: auto;
            margin-bottom: 8px;
        }
        .por-cotizar {
            color: #EAB308;
            font-size: 1em;
            font-weight: bold;
            background-color: rgba(234, 179, 8, 0.1);
            padding: 4px;
            border-radius: 6px;
            text-align: center;
            margin-top: auto;
            margin-bottom: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

def obtener_src_imagen(ruta_imagen):
    if str(ruta_imagen).startswith("http"):
        return ruta_imagen
    if os.path.exists(ruta_imagen):
        try:
            with open(ruta_imagen, "rb") as archivo_img:
                ext = os.path.splitext(ruta_imagen)[1].replace(".", "").lower()
                if ext == "jpg": ext = "jpeg"
                base64_encoded = base64.b64encode(archivo_img.read()).decode()
                return f"data:image/{ext};base64,{base64_encoded}"
        except Exception:
            pass
    return "https://placehold.co/400x300/0f172a/94a3b8?text=Imagen+No+Disponible"

def renderizar_tarjeta_completa(ruta_imagen, modelo, marca, tipo, precio, datos_rapidos=None):
    """
    Renderiza la tarjeta visual limpia en estilos.py, libre de errores en el DOM.
    """
    src_final = obtener_src_imagen(ruta_imagen)
    
    if precio > 0:
        elemento_precio = f'<div style="color: #22C55E; font-weight: bold; margin-top: 5px;">${precio:,.2f} MXN</div>'
    else:
        elemento_precio = '<div style="color: #8a9fc2; font-style: italic;">Por cotizar</div>'

    html_tags = ""
    if datos_rapidos:
        for tag in datos_rapidos:
            if tag and str(tag).strip() and str(tag).lower() != 'nan':
                html_tags += f'<span style="background-color: #2e3440; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; margin-right: 4px; color: #d8dee9;">{tag}</span>'

    # Un único contenedor padre, sin bloques html separados ni etiquetas huérfanas
    html_tarjeta = f"""
    <div style="background-color: #1e2433; border-radius: 10px; padding: 15px; min-height: 310px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;">
        <img src="{src_final}" style="width: 100%; height: 140px; object-fit: contain; border-radius: 5px; background-color: #141923; display: block; margin: 0 auto;">
        <div style="margin-top: 10px;">
            <div style="color: white; font-size: 1.1rem; font-weight: bold; margin-bottom: 5px;">{modelo}</div>
            <div style="color: #8a9fc2; font-size: 0.85rem; margin-bottom: 8px;"><b>Marca:</b> {marca} | <b>Tipo:</b> {tipo}</div>
            <div style="margin-bottom: 8px; height: 35px; overflow: hidden;">{html_tags}</div>
            {elemento_precio}
        </div>
    </div>
    """
    st.markdown(html_tarjeta, unsafe_allow_html=True)
    #Para el panel de administracion