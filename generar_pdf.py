import os
from jinja2 import Environment, FileSystemLoader
from pyhtml2pdf import converter

def generar_pdf_con_chrome(archivo_plantilla, archivo_salida, datos):
    # 1. Obtener la ruta exacta de la carpeta donde está este script
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Configurar Jinja2 para buscar estrictamente en esa carpeta
    entorno = Environment(loader=FileSystemLoader(directorio_actual))
    plantilla = entorno.get_template(archivo_plantilla)
    
    # 3. Inyectar los datos en la plantilla
    html_renderizado = plantilla.render(datos)
    
    # 4. Crear un archivo HTML temporal en esa misma carpeta
    archivo_temporal = os.path.join(directorio_actual, "temp_renderizado.html")
    with open(archivo_temporal, "w", encoding="utf-8") as f:
        f.write(html_renderizado)
    
    try:
        # 5. Obtener la ruta absoluta del archivo temporal para Chrome
        ruta_absoluta = f"file:///{os.path.abspath(archivo_temporal).replace(chr(92), '/')}"
        
        # 6. Convertir el archivo a PDF
        converter.convert(ruta_absoluta, archivo_salida)
        
    finally:
        # 7. Limpieza: Borrar el archivo HTML temporal
        if os.path.exists(archivo_temporal):
            os.remove(archivo_temporal)