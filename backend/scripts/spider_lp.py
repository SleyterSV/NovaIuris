import os
import time
import requests
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN DEL BOT CURADO DE ALTA VELOCIDAD ---
BASE_URL = "https://lpderecho.pe/category/jurisprudencia/page/"
CARPETA_DESTINO = os.path.abspath(os.path.join(os.path.dirname(__file__), '../raw_docs/jurisprudencia'))
PAGINAS_A_RASPAR = 150  # Analizará aprox 1500 posts recientes

# Filtro de excelencia: Solo descargará "oro jurídico"
PALABRAS_CLAVE_IMPACTO = [
    "casación", "casacion",
    "plenario",
    "precedente",
    "tc", "tribunal",
    "corte suprema",
    "sentencia",
    "expediente",
    "habeas"
]

# Headers para simular ser un navegador humano
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def crear_carpeta():
    """Asegura que el directorio exista."""
    if not os.path.exists(CARPETA_DESTINO):
        os.makedirs(CARPETA_DESTINO)
        print(f"📁 Carpeta creada: {CARPETA_DESTINO}")

def es_jurisprudencia_relevante(titulo):
    """Filtra la paja y deja solo la jurisprudencia clave."""
    titulo_min = titulo.lower()
    return any(palabra in titulo_min for palabra in PALABRAS_CLAVE_IMPACTO)

def descargar_pdf(pdf_url, titulo_articulo):
    """Descarga el documento y lo nombra de forma limpia."""
    try:
        respuesta = requests.get(pdf_url, headers=HEADERS, stream=True, timeout=15)
        if respuesta.status_code == 200:
            nombre_limpio = "".join([c if c.isalnum() else "_" for c in titulo_articulo])[:90]
            ruta_archivo = os.path.join(CARPETA_DESTINO, f"{nombre_limpio}.pdf")
            
            with open(ruta_archivo, 'wb') as f:
                for chunk in respuesta.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"✅ [DESCARGADO] {nombre_limpio}.pdf")
        else:
            print(f"❌ Error {respuesta.status_code} al descargar: {pdf_url}")
    except Exception as e:
        print(f"⚠️ Error de conexión al descargar PDF: {e}")

def iniciar_spider():
    print("🕷️ Iniciando LP Spider Bot (Modo Curado de Alta Velocidad)...")
    crear_carpeta()
    documentos_encontrados = 0

    for pagina in range(1, PAGINAS_A_RASPAR + 1):
        url_pagina = f"{BASE_URL}{pagina}/"
        print(f"\n📄 Analizando página {pagina}...")
        
        try:
            respuesta_cat = requests.get(url_pagina, headers=HEADERS, timeout=15)
            if respuesta_cat.status_code != 200:
                print(f"⚠️ Fin del escaneo o bloqueo temporal en página {pagina}.")
                break
                
            sopa_cat = BeautifulSoup(respuesta_cat.text, 'html.parser')
            
            # Buscamos directamente las etiquetas de título (h3 o h2)
            titulos_html = sopa_cat.find_all(['h3', 'h2'])
            
            for etiqueta in titulos_html:
                enlace_post = etiqueta.find('a')
                if not enlace_post or not enlace_post.get('href'):
                    continue
                    
                url_post = enlace_post['href']
                titulo_post = enlace_post.text.strip()
                
                # Ignorar encabezados pequeños que no son artículos
                if len(titulo_post) < 15:
                    continue
                
                # APLICAR EL FILTRO DE EXCELENCIA
                if es_jurisprudencia_relevante(titulo_post):
                    
                    # --- OPTIMIZACIÓN DE VELOCIDAD EXTREMA ---
                    # Verificar disco duro ANTES de hacer la petición web
                    nombre_limpio = "".join([c if c.isalnum() else "_" for c in titulo_post])[:90]
                    ruta_archivo = os.path.join(CARPETA_DESTINO, f"{nombre_limpio}.pdf")
                    
                    if os.path.exists(ruta_archivo):
                        print(f"⏭️  Omitido (Ya en memoria): {titulo_post[:50]}...")
                        continue # Salta inmediatamente al siguiente artículo
                    # -----------------------------------------

                    respuesta_post = requests.get(url_post, headers=HEADERS, timeout=10)
                    sopa_post = BeautifulSoup(respuesta_post.text, 'html.parser')
                    
                    pdf_url = None
                    
                    # PLAN A: Buscar el botón exacto de descarga que vimos en tu video
                    enlace_boton = sopa_post.find('a', string=lambda t: t and 'descargue' in t.lower() and 'pdf' in t.lower())
                    if enlace_boton and enlace_boton.get('href'):
                        pdf_url = enlace_boton['href']
                    else:
                        # PLAN B: Respaldo, buscar el primer link .pdf real
                        enlace_generico = sopa_post.find('a', href=lambda h: h and h.lower().endswith('.pdf'))
                        if enlace_generico:
                            pdf_url = enlace_generico['href']

                    # Si encontramos una URL válida, descargamos
                    if pdf_url:
                        print(f"🎯 Relevante: {titulo_post[:60]}...")
                        descargar_pdf(pdf_url, titulo_post)
                        documentos_encontrados += 1
                    
                    # Pausa Anti-Ban de 1.5 segundos para cuidar tu IP
                    time.sleep(1.5)
                
        except Exception as e:
            print(f"🚨 Error en la página {pagina}: {e}")

    print(f"\n🏁 Escaneo finalizado. Se extrajeron {documentos_encontrados} documentos de alto impacto.")

if __name__ == "__main__":
    iniciar_spider()