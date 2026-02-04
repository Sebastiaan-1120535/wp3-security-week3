import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from data.importer import DataImporter

if __name__ == '__main__':
    if len(sys.argv) < 2:
        base = Path(__file__).parent
        for json_file in base.glob("data-sample*.json"):
            print(f"  - {json_file.name}")
        sys.exit(1)

    json_file = sys.argv[1]
    base_dir = Path(__file__).parent
    db_path = base_dir / 'data' / 'prod.sqlite'


    try:
        importer = DataImporter(str(db_path))
        importer.import_json(json_file)
    except Exception as e:
        sys.exit(1)
