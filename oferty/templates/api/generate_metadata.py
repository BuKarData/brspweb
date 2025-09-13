import os
from datetime import datetime
import hashlib
from jinja2 import Environment, FileSystemLoader

# BASE_DIR wskazuje na folder, w którym jest generate_metadata.py
BASE_DIR = os.path.dirname(__file__)
REPORTS_DIR = "/Users/kaponers/Downloads/Strony zarządzanie/braspol/raporty"

# Pliki raportów
reports_files = [
    ("braspol-jsonld", "raport_2025-09-13.jsonld", "application/ld+json", "Ceny nieruchomości - JSON-LD"),
    ("braspol-csv", "Raport ofert firmy Braspol_2025-09-13.csv", "text/csv", "Ceny nieruchomości - CSV"),
    ("braspol-xlsx", "Raport ofert firmy Braspol_2025-09-13.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "Ceny nieruchomości - Excel XLSX"),
]

reports = []

def md5sum(path):
    with open(os.path.join(REPORTS_DIR, path), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

for id_, file, fmt, title in reports_files:
    reports.append({
        "id": id_,
        "file": file,
        "format": fmt,
        "title": title,
        "url": f"https://www.braspol.pl/api/{file}",
        "availability": "remote",
        "description": f"Dane w formacie {fmt}",
        "md5": md5sum(file)
    })

current_date = datetime.now().strftime("%Y-%m-%d")
current_date_nodash = datetime.now().strftime("%Y%m%d")

# Wczytanie szablonu
env = Environment(loader=FileSystemLoader(BASE_DIR))
template = env.get_template("metadata_template.xml")

output_xml = template.render(
    current_date=current_date,
    current_date_nodash=current_date_nodash,
    reports=reports
)

# Folder docelowy: istniejący folder api w projekcie oferty
output_folder = os.path.join(BASE_DIR, 'api')
os.makedirs(output_folder, exist_ok=True)  # utworzy folder tylko jeśli go nie ma

# Pełna ścieżka do pliku metadata.xml
output_file = os.path.join(output_folder, 'metadata.xml')

# Zapis gotowego metadata.xml
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(output_xml)

print(f"metadata.xml wygenerowany w {output_folder} z aktualną datą {current_date}")
