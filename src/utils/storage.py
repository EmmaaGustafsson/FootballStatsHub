import json
from pathlib import Path
from datetime import datetime
import logging

DATA_DIR = Path("data")
FAVORITES_FILE = DATA_DIR / "favorites.json"

def load_favorites() -> list[str]:     # Funktion som skapar en lista med strängar
    if not FAVORITES_FILE.exists():    # Om det inte finns i filen, skapa tom lista så att programmet inte kraschar
        return []

    try:    # Försöker läsa fil. Om något är fel, hoppa till except
        with FAVORITES_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("favorites", [])
    except json.JSONDecodeError:
        logging.error("Kunde inte läsa favorites.json")
        return []

def save_favorites(favorites: list[str]) -> None:   # Funktion som sparar favoritlag
    DATA_DIR.mkdir(exist_ok=True)    # Om mappen data inte finns, skapa den, gör inget om den redan finns

# Skapar ett dictionary som sparas som JSON
    favorites_data: dict[str, object] = {
        "favorites": favorites,
        "saved_at": datetime.now().isoformat()
    }

    with FAVORITES_FILE.open("w", encoding="utf-8") as file:  # Öppnar fil i write-mode
        json.dump(favorites_data, file, indent=2)   # Konverterar vår data dict till JSON text och skriver in det i filen