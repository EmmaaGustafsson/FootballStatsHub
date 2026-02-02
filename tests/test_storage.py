import json
from src.utils import storage

def test_save_and_load_favorites(tmp_path, monkeypatch):
    fake_data_dir = tmp_path / "data"  # Skapar en fake data-mapp

    monkeypatch.setattr(storage, "DATA_DIR", fake_data_dir) # Vi tvingar koden att använda fake-filen och fake-mappen
    monkeypatch.setattr(
        storage,
        "FAVORITES_FILE",
        fake_data_dir / "favorites.json"
    )

    favorites = ["Barcelona", "Arsenal"]  # Testdata

    storage.save_favorites(favorites) # Kör funktionen
    loaded = storage.load_favorites() # Laddar tillbaka datan

    assert loaded == favorites  # Testet lyckas bara om allt fungerar


''' Funktion för att programmet inte ska krascha om filen saknas'''
def test_load_favorites_when_file_missing(tmp_path, monkeypatch):
    fake_data_dir = tmp_path / "data"

    monkeypatch.setattr(storage, "DATA_DIR", fake_data_dir)
    monkeypatch.setattr(
        storage,
        "FAVORITES_FILE",
        fake_data_dir / "favorites.json"
    )

    loaded = storage.load_favorites()

    assert loaded == []
