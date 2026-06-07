import os
from jinja2 import Environment, FileSystemLoader
from pyhtml2pdf import converter
import io 

def generar_pdf_con_chrome(archivo_plantilla,datos):
    # 1. Obtener la ruta exacta de la carpeta donde está este script
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Configurar Jinja2 para buscar estrictamente en esa carpeta
    entorno = Environment(loader=FileSystemLoader(directorio_actual))
    plantilla = entorno.get_template(archivo_plantilla)
    
    # 3. Inyectar los datos en la plantilla
    html_renderizado = plantilla.render(datos)
    
    # 4. Convertir el HTML a PDF usando pyhtml2pdf
    # Usamos un buffer en memoria para evitar problemas de rutas
    buffer_pdf = io.BytesIO()
    converter.convert(html_renderizado, buffer_pdf)
    return buffer_pdf
