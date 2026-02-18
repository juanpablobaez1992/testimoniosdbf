import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env si existe
load_dotenv()

# --- API KEYS ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# --- WORDPRESS SETTINGS ---
WP_URL          = os.getenv("WP_URL", "https://www.debuenafedigital.com")
WP_USER         = os.getenv("WP_USER")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

# --- CATEGORIES (IDs) ---
WP_CATEGORIA_TESTIMONIOS    = int(os.getenv("WP_CATEGORIA_TESTIMONIOS", 15))
WP_CATEGORIA_ESPIRITUALIDAD = int(os.getenv("WP_CATEGORIA_ESPIRITUALIDAD", 8))

# --- PREFERENCIAS DE IMÁGENES ---
PEXELS_QUERIES = [
    "spirituality", "faith", "hope", "prayer", "nature serenity", 
    "community help", "reflection", "peace", "compassion", "gratitude"
]
