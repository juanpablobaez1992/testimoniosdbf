import os
import json
import random
import argparse
import requests
import base64
import google.generativeai as genai
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup

# Importar configuración
try:
    import config
except ImportError:
    print("Error: No se encontró config.py. Asegúrate de crearlo siguiendo la guía.")
    exit(1)

# Configurar Gemini
genai.configure(api_key=config.GEMINI_API_KEY)

# --- DEFINICIONES DE CONTENIDO ---

PERFILES = [
    "Un ex-ateo militante que encontro la fe a traves de la ciencia",
    "Una persona que abandono la New Age tras una experiencia de sanacion",
    "Un antiguo miembro de una secta que descubrio la libertad en el catolicismo",
    "Un profesional exitoso que dejo el materialismo tras un retiro de Emaus",
    "Una historia de conversion radical tras una crisis personal profunda",
    "Alguien que encontro a Dios en medio del sufrimiento mas extremo"
]

ANGULOS = [
    "Testimonio de transformacion radical y humana",
    "Cronica de un 'antes y despues' espiritual",
    "Relato de conversion desde el escepticismo",
    "Narrativa de sanacion y encuentro con la Verdad",
    "Historia de entrega y cambio de vida total"
]

FEEDS_CATOLICOS = [
    "http://feeds.feedburner.com/noticiasaci",
    "https://www.religionenlibertad.com/rss/informativo.xml"
]

# --- FUNCIONES CORE ---

def obtener_noticia_real():
    """Busca una historia real de conversión o testimonio en medios católicos."""
    print("Buscando noticias reales en medios catolicos...")
    historias = []
    palabras_clave = ["conversion", "converso", "ateo", "new age", "secta", "testimonio", "emaus", "sanacion", "ex-", "vida radical"]
    
    for url in FEEDS_CATOLICOS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                # Priorizar historias que tengan palabras clave en título o resumen
                texto_total = (entry.title + " " + entry.description).lower()
                if any(kw in texto_total for kw in palabras_clave):
                    historias.append({
                        "titulo_original": entry.title,
                        "resumen_original": entry.description,
                        "link": entry.link
                    })
        except Exception as e:
            print(f"Error leyendo feed {url}: {e}")
    
    if historias:
        # Devolver una historia al azar de las filtradas
        return random.choice(historias)
    
    # Si no hay match con palabras clave, tomar cualquier noticia reciente
    print("No se encontraron historias especificas, tomando una noticia reciente...")
    try:
        feed = feedparser.parse(FEEDS_CATOLICOS[0])
        if feed.entries:
            entry = random.choice(feed.entries[:5])
            return {
                "titulo_original": entry.title,
                "resumen_original": entry.description,
                "link": entry.link
            }
    except:
        pass
    
    return None

def extraer_imagen_de_url(url):
    """Intenta extraer la imagen principal (og:image) de la noticia original."""
    print(f"Intentando extraer imagen original de: {url}...")
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Buscar tag Open Graph image
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]
        
        # Fallback a twitter image si no hay OG
        twitter_image = soup.find("meta", name="twitter:image")
        if twitter_image and twitter_image.get("content"):
            return twitter_image["content"]
            
    except Exception as e:
        print(f"Error extrayendo imagen de la fuente: {e}")
    
    return None

def generar_contenido_ia(noticia_real=None):
    """Usa Gemini para generar el artículo completo y metadata."""
    if noticia_real:
        contexto = f"""
        BASADO EN ESTA NOTICIA REAL:
        Título: {noticia_real['titulo_original']}
        Resumen/Contexto: {noticia_real['resumen_original']}
        Fuente: {noticia_real['link']}
        
        INSTRUCCIÓN ADICIONAL: Mantén la veracidad de los hechos, pero redacta con el tono de 'De Buena Fe Digital'.
        """
        perfil = "Basado en noticia real"
        angulo = "Narrativa periodística veraz"
    else:
        perfil = random.choice(PERFILES)
        angulo = random.choice(ANGULOS)
        contexto = f"PERFIL DEL PROTAGONISTA: {perfil}\nÁNGULO NARRATIVO: {angulo}"
    
    prompt = f"""
    Tu objetivo es escribir un TESTIMONIO DE CONVERSIÓN inspirador y humano.
    CONCENTRACIÓN EXCLUSIVA: La historia debe centrarse en un cambio de vida radical, 
    un encuentro con Dios tras una vida de alejamiento, escepticismo o pertenencia a otras creencias (protestantismo, mormonismo, misticismo, ateísmo, New Age).
    NO escribas reflexiones sobre espiritualidad general si no hay una transformación personal de fondo.
    
    CONTEXTO DE LA HISTORIA:
    {contexto}
    
    REQUISITOS DEL ARTÍCULO:
    - Longitud: 600-750 palabras.
    - Estructura: HTML con H2 y H3 jerarquizados.
    - REQUISITO DE IMÁGENES INTERNAS: Inserta EXACTAMENTE dos marcadores de posición `[[IMAGEN_1]]` y `[[IMAGEN_2]]` repartidos de forma equilibrada entre los párrafos del cuerpo del artículo.
    - REQUISITO DE ENLACES: Integra de forma natural un enlace (<a>) a la noticia fuente ({noticia_real['link'] if noticia_real else '#'}) mencionando que es la noticia original o la fuente del testimonio.
    - Idioma: Español.
    - Título: Periodístico, emotivo, optimizado para clicks (máximo 60 caracteres).
    - Extracto: 2 oraciones breves y potentes.
    - Yoast SEO:
        - Focus Keyphrase: Una frase de 1-3 palabras clave.
        - SEO Title: Igual o similar al título periodístico.
        - Meta Descripción: 140-155 caracteres invitando a leer.
    - Alt Text Imagen Destacada: Descripción clara en español.
    - Keyword de búsqueda Pexels para imagen destacada: Término en inglés.
    - Imágenes adicionales: Proporciona 2 queries de Pexels y sus respectivos Alt Texts para las imágenes internas.
    - Etiquetas: Lista de 3-5 palabras clave breves (ej: "Conversion", "Emaus", "Sanacion").
    
    RESPONDE ÚNICAMENTE CON UN JSON VÁLIDO CON ESTA ESTRUCTURA:
    {{
      "titulo": "...",
      "contenido_html": "...",
      "extracto": "...",
      "focus_keyphrase": "...",
      "seo_title": "...",
      "meta_description": "...",
      "alt_text": "...",
      "pexels_query": "...",
      "img_internas": [
        {{ "query": "...", "alt": "..." }},
        {{ "query": "...", "alt": "..." }}
      ],
      "etiquetas": ["tag1", "tag2", "tag3"]
    }}
    """
    
    model = genai.GenerativeModel("gemini-flash-latest")
    response = model.generate_content(prompt)
    
    try:
        # Extraer JSON de la respuesta (manejar markdown y texto extra)
        text = response.text.strip()
        # Buscar el bloque JSON si existe
        if "```json" in text:
            text = text.split("```json")[-1].split("```")[0].strip()
        elif "{" in text:
            # Intentar encontrar el primer { y el ultimo }
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                text = text[start:end+1]
                
        return json.loads(text)
    except Exception as e:
        print(f"Error parseando respuesta de IA: {e}")
        return None

def buscar_imagen_pexels(query):
    """Busca una imagen en Pexels y devuelve la URL de descarga."""
    headers = {"Authorization": config.PEXELS_API_KEY}
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
    
    try:
        res = requests.get(url, headers=headers)
        data = res.json()
        if data.get("photos"):
            return data["photos"][0]["src"]["large"]
    except Exception as e:
        print(f"Error en Pexels para '{query}': {e}")
    
    # Fallback a una imagen de la lista de configuración
    fallback_query = random.choice(config.PEXELS_QUERIES)
    print(f"Pexels falló para '{query}', intentando fallback con '{fallback_query}'")
    url = f"https://api.pexels.com/v1/search?query={fallback_query}&per_page=1"
    res = requests.get(url, headers=headers)
    data = res.json()
    return data["photos"][0]["src"]["large"] if data.get("photos") else None

def subir_media_wordpress(image_url, alt_text):
    """Descarga imagen y la sube a la librería de medios de WP."""
    try:
        # Descargar imagen
        img_res = requests.get(image_url, timeout=15)
        if img_res.status_code != 200:
            return None
        img_data = img_res.content
        filename = f"foto_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(100,999)}.jpg"
        
        # Credenciales Base64
        credentials = f"{config.WP_USER}:{config.WP_APP_PASSWORD}"
        token = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {token}",
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "image/jpeg"
        }
        
        res = requests.post(f"{config.WP_URL}/wp-json/wp/v2/media", headers=headers, data=img_data)
        if res.status_code == 201:
            media_json = res.json()
            media_id = media_json["id"]
            media_url = media_json["source_url"]
            # Actualizar alt text
            requests.post(
                f"{config.WP_URL}/wp-json/wp/v2/media/{media_id}",
                headers={"Authorization": f"Basic {token}"},
                json={"alt_text": alt_text}
            )
            return {"id": media_id, "url": media_url}
        else:
            print(f"Error subiendo imagen a WP: {res.text}")
            return None
    except Exception as e:
        print(f"Excepcion subiendo media: {e}")
        return None

def obtener_o_crear_etiquetas(nombres):
    """Busca los IDs de las etiquetas en WP. Si no existen, intenta crearlas."""
    credentials = f"{config.WP_USER}:{config.WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    headers = {"Authorization": f"Basic {token}"}
    
    tag_ids = []
    for nombre in nombres:
        try:
            # Buscar si existe
            res = requests.get(f"{config.WP_URL}/wp-json/wp/v2/tags?search={nombre}", headers=headers)
            exact_match = [t for t in res.json() if t["name"].lower() == nombre.lower()]
            
            if exact_match:
                tag_ids.append(exact_match[0]["id"])
            else:
                # Crear si no existe
                res_create = requests.post(f"{config.WP_URL}/wp-json/wp/v2/tags", headers=headers, json={"name": nombre})
                if res_create.status_code == 201:
                    tag_ids.append(res_create.json()["id"])
        except Exception as e:
            print(f"Error procesando etiqueta '{nombre}': {e}")
            
    return tag_ids

def publicar_en_wordpress(data, media_id):
    """Crea el borrador del post en WordPress."""
    credentials = f"{config.WP_USER}:{config.WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Buscando IDs para etiquetas: {data.get('etiquetas', [])}")
    tag_ids = obtener_o_crear_etiquetas(data.get("etiquetas", []))
    
    post_data = {
        "title": data.get("titulo", "Sin Título"),
        "content": data.get("contenido_html", ""),
        "excerpt": data.get("extracto", ""),
        "status": "draft",
        "categories": [config.WP_CATEGORIA_TESTIMONIOS],
        "tags": tag_ids,
        "featured_media": media_id,
        "meta": {
            "_yoast_wpseo_focuskw": data.get("focus_keyphrase", ""),
            "_yoast_wpseo_title": data.get("seo_title", ""),
            "_yoast_wpseo_metadesc": data.get("meta_description", "")
        }
    }
    
    res = requests.post(f"{config.WP_URL}/wp-json/wp/v2/posts", headers=headers, json=post_data)
    if res.status_code == 201:
        print(f"¡Éxito! Borrador creado: {res.json()['link']}")
        return res.json()["link"]
    else:
        print(f"Error publicando post: {res.text}")
        return None

def guardar_log(data, status):
    """Guarda registro en log_articulos.jsonl"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "titulo": data["titulo"],
        "status": status
    }
    with open("log_articulos.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

# --- FLUJO PRINCIPAL ---

def main():
    parser = argparse.ArgumentParser(description="Generador de Artículos De Buena Fe")
    parser.add_argument("--preview", action="store_true", help="Solo previsualizar, no publicar")
    args = parser.parse_args()
    
    print("Obteniendo noticia real de fuentes catolicas...")
    noticia = obtener_noticia_real()
    
    if noticia:
        print(f"Fuente encontrada: {noticia['titulo_original']}")
    else:
        print("No se pudo obtener una noticia real, usando perfiles genéricos.")

    print("Generando contenido con IA...")
    articulo = generar_contenido_ia(noticia)
    if not articulo:
        return

    print("Determinando imagen DESTACADA para el articulo...")
    img_url_destacada = None
    if noticia and noticia.get("link"):
        img_url_destacada = extraer_imagen_de_url(noticia["link"])
    
    if img_url_destacada:
        print("Se utilizara la imagen original de la fuente como destacada.")
    else:
        print(f"No se encontro imagen original, buscando destacada en Pexels para: {articulo['pexels_query']}...")
        img_url_destacada = buscar_imagen_pexels(articulo["pexels_query"])

    # Manejo de imágenes internas (solo si no es preview o si queremos ver URLs en preview)
    img_internas_urls = []
    for i, meta_img in enumerate(articulo.get("img_internas", [])):
        print(f"Buscando imagen interna {i+1} en Pexels para: {meta_img['query']}...")
        url = buscar_imagen_pexels(meta_img["query"])
        if url:
            img_internas_urls.append({"url": url, "alt": meta_img["alt"]})

    if args.preview:
        print("\n=== PREVIEW DEL ARTÍCULO ===")
        print(f"TÍTULO: {articulo['titulo']}")
        print(f"SEO: {articulo['seo_title']} | KW: {articulo['focus_keyphrase']}")
        print(f"IMAGEN DESTACADA: {img_url_destacada}")
        etiquetas = articulo.get('etiquetas', [])
        print(f"ETIQUETAS: {', '.join(etiquetas) if etiquetas else 'Ninguna'}")
        
        preview_html = articulo["contenido_html"]
        for i, img in enumerate(img_internas_urls):
            marker = f"[[IMAGEN_{i+1}]]"
            img_tag = f"\n[IMAGEN INTERNA {i+1}: {img['url']} - ALT: {img['alt']}]\n"
            preview_html = preview_html.replace(marker, img_tag)
            
        print("-" * 30)
        print(preview_html)
        print("-" * 30)
        guardar_log(articulo, "preview")
    else:
        # 1. Subir imagen destacada
        media_id_destacada = None
        if img_url_destacada:
            print("Subiendo imagen destacada a WordPress...")
            res_media = subir_media_wordpress(img_url_destacada, articulo["alt_text"])
            if res_media:
                media_id_destacada = res_media["id"]
        
        # 2. Subir imágenes internas y reemplazar marcadores
        html_final = articulo["contenido_html"]
        for i, img in enumerate(img_internas_urls):
            marker = f"[[IMAGEN_{i+1}]]"
            print(f"Subiendo imagen interna {i+1} a WordPress...")
            res_media = subir_media_wordpress(img["url"], img["alt"])
            if res_media:
                # Crear bloque de imagen estilo Gutenberg/WP
                wp_img_html = f"""
                <figure class="wp-block-image size-large">
                    <img src="{res_media['url']}" alt="{img['alt']}" class="wp-image-{res_media['id']}"/>
                    <figcaption>{img['alt']}</figcaption>
                </figure>
                """
                html_final = html_final.replace(marker, wp_img_html)
            else:
                html_final = html_final.replace(marker, "") # Quitar marcador si falla

        articulo["contenido_html"] = html_final

        print("Creando borrador en WordPress con imágenes internas y links...")
        wp_link = publicar_en_wordpress(articulo, media_id_destacada)
        
        if wp_link:
            guardar_log(articulo, "published")

if __name__ == "__main__":
    main()
