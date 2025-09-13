import os
import hashlib
from datetime import datetime
from django.core.management.base import BaseCommand
from jinja2 import Environment, FileSystemLoader

# folder generate_metadata.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# pliki raportów i data
REPORTS_DIR = os.path.join(BASE_DIR, "../../raporty")  # jeśli raporty są w projekcie
current_date = datetime.now().strftime("%Y-%m-%d")
current_date_nodash = datetime.now().strftime("%Y%m%d")

reports_files = [
    ("braspol-jsonld", f"raport_{current_date}.jsonld", "application/ld+json", "Ceny nieruchomości - JSON-LD"),
    ("braspol-csv", f"Raport ofert firmy Braspol_{current_date}.csv", "text/csv", "Ceny nieruchomości - CSV"),
    ("braspol-xlsx", f"Raport ofert firmy Braspol_{current_date}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "Ceny nieruchomości - Excel XLSX"),
]

def md5sum(path: str) -> str:
    full_path = os.path.join(REPORTS_DIR, path)
    if not os.path.exists(full_path):
        return ""
    with open(full_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

class Command(BaseCommand):
    help = "Generuje metadata.xml w folderze api"

    def handle(self, *args, **kwargs):
        # lista raportów
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
                "md5": md5sum(file),
            })

        # loader wskazuje bezpośrednio na folder z szablonem
        env = Environment(loader=FileSystemLoader(BASE_DIR))
        template = env.get_template("metadata_template.xml")

        output_xml = template.render(
            current_date=current_date,
            current_date_nodash=current_date_nodash,
            reports=reports
        )

        # zapis w tym samym folderze
        output_file = os.path.join(BASE_DIR, "metadata.xml")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output_xml)

        self.stdout.write(self.style.SUCCESS(f"metadata.xml wygenerowany w {output_file}"))
