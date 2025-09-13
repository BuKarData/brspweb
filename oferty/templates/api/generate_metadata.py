import os
from datetime import datetime
import hashlib
from jinja2 import Environment, FileSystemLoader

# --- Ścieżki ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # oferty/templates/api
TEMPLATE_DIR = BASE_DIR  # szablon jest w tym samym folderze
REPORTS_DIR = os.path.join(BASE_DIR, '../../raporty')  # raporty w katalogu nadrzędnym "raporty"

# --- Pliki raportów ---
reports_files = [
    ("braspol-jsonld", "raport_2025-09-13.jsonld", "application/ld+json", "Ceny nieruchomości - JSON-LD"),
    ("braspol-csv", "Raport ofert firmy Braspol_2025-09-13.csv", "text/csv", "Ceny nieruchomości - CSV"),
    ("braspol-xlsx", "Raport ofert firmy Braspol_2025-09-13.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "Ceny nieruchomości - Excel XLSX"),
]

# --- Funkcja generująca MD5 ---
def md5sum(filename):
    full_path = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Plik raportu nie istnieje: {full_path}")
    with open(full_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

# --- Tworzenie listy raportów ---
reports = []
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

# --- Daty ---
current_date = datetime.now().strftime("%Y-%m-%d")
current_date_nodash = datetime.now().strftime("%Y%m%d")

# --- Wczytanie szablonu Jinja2 ---
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
template = env.get_template("metadata_template.xml")

# --- Renderowanie XML ---
output_xml = template.render(
    current_date=current_date,
    current_date_nodash=current_date_nodash,
    reports=reports
)

# --- Zapis do metadata.xml w tym samym folderze ---
output_file = os.path.join(BASE_DIR, "metadata.xml")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(output_xml)

print(f"metadata.xml wygenerowany w {BASE_DIR} z aktualną datą {current_date}")
