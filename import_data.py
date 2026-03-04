import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from data.importer import DataImporter

if __name__ == '__main__':
    base_dir = Path(__file__).parent
    db_path = base_dir / 'data' / 'prod.sqlite'

    if len(sys.argv) < 2:
        print("Gebruik: python import_data.py <json_bestand> --clear")
        print("  - clean: Verwijdert de database en laadt deze opnieuw")
        for json_file in base_dir.glob("data-sample*.json"):
            print(f"  - {json_file.name}")
        sys.exit(1)

    json_file = sys.argv[1]
    json_path = base_dir / json_file if not Path(json_file).is_absolute() else Path(json_file)

    clean_up = len(sys.argv) > 2 and sys.argv[2].lower() == '--clear'

    if not json_path.exists():
        print(f"FOUT: Bestand niet gevonden: {json_path}")
        sys.exit(1)

    try:
        importer = DataImporter(str(db_path))

        if clean_up:
            importer.clean_up_database()

        importer.import_json(str(json_path))
    except Exception as e:
        print(f"FOUT: {e}")
        sys.exit(1)

