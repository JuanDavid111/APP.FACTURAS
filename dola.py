import requests

def tasaBCV():
    # Endpoints de la API pública
    url_bcv = "https://ve.dolarapi.com/v1/dolares/oficial"

    
    try:
        # Hacemos las peticiones GET a la API
        respuesta_bcv = requests.get(url_bcv)

        # Validamos que la petición fue exitosa (código 200)
        respuesta_bcv.raise_for_status()
        
        # Convertimos la respuesta a formato JSON (diccionario en Python)
        datos_bcv = respuesta_bcv.json()

        # Extraemos el valor "promedio" (la tasa en Bs)
        precio_bcv = datos_bcv.get("promedio")
        
        return precio_bcv
        
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la tasa del BCV: {e}")
        return None


if __name__ == "__main__":
    tasaBCV()



def tasaParalelo():
    url_paralelo = "https://ve.dolarapi.com/v1/dolares/paralelo"
    
    try:
        respuesta_paralelo = requests.get(url_paralelo)
        respuesta_paralelo.raise_for_status()
        datos_paralelo = respuesta_paralelo.json()
        precio_paralelo = datos_paralelo.get("promedio")
        
        return precio_paralelo
        
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la tasa del Paralelo: {e}")
        return None