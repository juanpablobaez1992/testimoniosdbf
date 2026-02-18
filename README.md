# ✝️ Generador de Testimonios — De Buena Fe Digital

Automatiza la creación y publicación de testimonios de conversión en WordPress usando IA. El script busca noticias reales en medios católicos, genera un artículo optimizado para SEO con Google Gemini, busca imágenes en Pexels y crea un borrador listo para revisar en tu sitio.

---

## ¿Cómo funciona?

```
📡 RSS Católicos  →  🤖 Gemini AI  →  🖼️ Pexels  →  📝 WordPress (borrador)
```

1. **Busca una noticia real** en feeds RSS de medios católicos (ACI Prensa, Religión en Libertad)
2. **Genera el artículo** con Google Gemini: título, contenido HTML, slug, extracto, etiquetas y metadata Yoast SEO
3. **Obtiene imágenes**: primero intenta extraer la imagen de la fuente original; si falla, busca en Pexels
4. **Publica el borrador** en WordPress vía REST API, con imagen destacada, imágenes internas y metadatos Yoast listos

---

## Requisitos

- Python 3.9+
- Una cuenta en [Google AI Studio](https://aistudio.google.com/) (API key de Gemini)
- Una cuenta en [Pexels](https://www.pexels.com/api/) (API key gratuita)
- WordPress con plugin **Application Passwords** activo (incluido desde WP 5.6)
- Plugin **Yoast SEO** instalado (para los campos de metadata)

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/juanpablobaez1992/testimoniosdbf.git
cd testimoniosdbf

# 2. Crear entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Configuración

Copia el archivo de ejemplo y completa tus credenciales:

```bash
cp .env.example .env
```

Edita `.env` con tus datos:

```env
# Google Gemini
GEMINI_API_KEY=tu_api_key_de_gemini

# Pexels
PEXELS_API_KEY=tu_api_key_de_pexels

# WordPress
WP_URL=https://www.tudominio.com
WP_USER=tu_usuario_wp
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

# IDs de categorías en WordPress
WP_CATEGORIA_TESTIMONIOS=15
WP_CATEGORIA_ESPIRITUALIDAD=8
```

> 💡 **¿Cómo generar el Application Password de WordPress?**
> Ve a **Usuarios → Tu perfil** y baja hasta la sección **"Contraseñas de aplicación"**.

---

## Uso

### Publicar un artículo directamente como borrador en WordPress

```bash
python generar_articulo.py
```

### Previsualizar el artículo sin publicar

```bash
python generar_articulo.py --preview
```

Útil para revisar el contenido generado antes de subirlo. El resultado se muestra en consola y se guarda en `log_articulos.jsonl`.

---

## Estructura del proyecto

```
testimoniosdbf/
├── generar_articulo.py   # Script principal
├── config.py             # Carga de variables de entorno
├── requirements.txt      # Dependencias Python
├── .env.example          # Plantilla de configuración
└── .gitignore            # Excluye .env, logs y archivos temporales
```

---

## Artículo generado — estructura

Cada artículo que produce el script incluye:

| Campo | Descripción |
|---|---|
| `titulo` | Título periodístico del post |
| `slug` | URL amigable sugerida |
| `contenido_html` | Cuerpo completo con H2/H3, negritas e imágenes integradas |
| `extracto` | Resumen de 2 oraciones para redes y listados |
| `focus_keyphrase` | Palabra clave principal (Yoast) |
| `seo_title` | Título optimizado para Google (≤ 60 caracteres) |
| `meta_description` | Meta descripción (140–155 caracteres) |
| `etiquetas` | Tags generados automáticamente |

---

## Notas de seguridad

- El archivo `.env` está excluido del repositorio vía `.gitignore` — **nunca subas tus credenciales**
- Usa siempre **Application Passwords** de WordPress en lugar de tu contraseña principal
- Rota tus API keys si sospechas que fueron expuestas

---

## Licencia

Uso personal / privado. Proyecto desarrollado para [De Buena Fe Digital](https://www.debuenafedigital.com).
