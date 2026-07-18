import pandas as pd

def calcular_disco_requerido(num_camaras, resolucion_texto, dias_grabacion):
    """
    Calcula cuántos Terabytes se necesitan basados en la resolución de la cámara.
    """
    resolucion_texto = str(resolucion_texto).lower()
    
    if "8" in resolucion_texto or "4k" in resolucion_texto:
        gb_por_dia = 60
    elif "5" in resolucion_texto or "6" in resolucion_texto:
        gb_por_dia = 40
    else:
        gb_por_dia = 20  # Estándar para 2 MP / 1080p

    gigabytes_totales = num_camaras * gb_por_dia * dias_grabacion
    tb_necesarios = gigabytes_totales / 1000
    return tb_necesarios


def seleccionar_disco_compatible(df_discos, tb_necesarios):
    """
    Busca en el inventario de discos el más chico que cubra la necesidad matemática.
    """
    if df_discos.empty:
        return pd.Series()
        
    df_discos['Capacidad_Num'] = df_discos['Capacidad'].apply(
        lambda x: int(''.join(filter(str.isdigit, str(x)))) if any(c.isdigit() for c in str(x)) else 1
    )
    
    discos_validos = df_discos[df_discos['Capacidad_Num'] >= tb_necesarios]
    
    if not discos_validos.empty:
        return discos_validos.sort_values(by='Capacidad_Num').iloc[0]
    else:
        return df_discos.sort_values(by='Capacidad_Num').iloc[-1]

def calcular_infraestructura_y_mano_obra(num_camaras, metros_cable, tipo_camara):
    """
    Calcula costos y modelos de transceptores, cajas, fuentes, cable y mano de obra.
    """
    tipo_camara_clean = str(tipo_camara).strip().lower()
    
    res = {
        "aplica": True, # Cambiado a True por defecto para asegurar que se muestre
        "costo_cable": 0.0,
        "transceptor_modelo": "N/A",
        "transceptor_costo": 0.0,
        "cajas_cantidad": 0,
        "cajas_costo": 0.0,
        "fuente_modelo": "N/A",
        "fuente_costo": 0.0,
        "costo_mano_obra": 0.0,
        "costo_total_infraestructura": 0.0
    }
    
    # Identificar si es wifi basándose en el texto
    es_wifi = "wifi" in tipo_camara_clean or "wi-fi" in tipo_camara_clean
    
    # Si la categoría explícitamente no aplica, la excluimos
    if "dashcam" in tipo_camara_clean or "webcam" in tipo_camara_clean:
        res["aplica"] = False
        return res
        
    # 2. Cable
    res["costo_cable"] = float(metros_cable * 10)
    
    # 3. Transceptores (Baluns) - Si no es WiFi, asumimos que es análoga y requiere baluns
    if not es_wifi and num_camaras > 0:
        promedio_metros = metros_cable / num_camaras
        if promedio_metros > 100:
            res["transceptor_modelo"] = "EPCOM TITANIUM TT-101-PV-TURBO"
            res["transceptor_costo"] = float(num_camaras * 389)
        else:
            res["transceptor_modelo"] = "Provision-ISR PTR-102VP-HD+"
            res["transceptor_costo"] = float(num_camaras * 170)
    else:
        res["transceptor_modelo"] = "No requerido (WiFi)"
        res["transceptor_costo"] = 0.0

    # 4. Cajas de derivación Heavy Duty
    res["cajas_cantidad"] = num_camaras
    res["cajas_costo"] = float(num_camaras * 145) 
    
    # 5. Fuente de alimentación
    if num_camaras <= 4:
        res["fuente_modelo"] = "EPCOM P24DC3A"
        res["fuente_costo"] = 450.0  
    else:
        res["fuente_modelo"] = "EPCOM PL36V2A"
        res["fuente_costo"] = 980.0  

    # 6. Mano de obra
    if es_wifi:
        res["costo_mano_obra"] = float(num_camaras * 650)
    else:
        res["costo_mano_obra"] = float(num_camaras * 350)
        
    # Suma total
    res["costo_total_infraestructura"] = (
        res["costo_cable"] + 
        res["transceptor_costo"] + 
        res["cajas_costo"] + 
        res["fuente_costo"] + 
        res["costo_mano_obra"]
    )
    
    return res