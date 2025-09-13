import os
import hashlib
from datetime import datetime
from django.core.management.base import BaseCommand
from jinja2 import Environment, FileSystemLoader
from django.conf import settings

# katalog z raportami (lokalnie generujesz w tym folderze)
REPORTS_DIR = os.path.join(settings.BASE_DIR, "raporty")

# pliki raportów (dynamiczne nazwy z datą)
current_date = datetime.now().strftime("%Y-%m-%d")
current_date_nodash = datetime.now().strftime("%Y%m%d")

reports_files = [
    ("braspol-jsonld", f"raport_{current_date}.jsonld", "application/ld+json", "Ceny nieruchomości - JSON-LD"),
    ("braspol-csv", f"Raport ofert firmy Braspol_{current_date}.csv", "text/csv", "Ceny nieruchomości - CSV"),
    ("braspol-xlsx", f"Raport ofert firmy Braspol_{current_date}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "Ceny nieruchomości - Excel XLSX"),
]


def md5sum(path: str) -> str:
    """Zwraca sumę MD5 albo pusty string jeśli plik nie istnieje."""
    full_path = os.path.join(REPORTS_DIR, path)
    if not os.path.exists(full_path):
        return ""  # na Railway brak pliku → brak md5
    with open(full_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


class Command(BaseCommand):
    help = "Generuje plik metadata.xml w oferty/api"

    def handle(self, *args, **kwargs):
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

        # Jinja2
        env = Environment(loader=FileSystemLoader(os.path.join(settings.BASE_DIR, "oferty", "templates")))
        template = env.get_template("metadata_template.xml")

        output_xml = template.render(
            current_date=current_date,
            current_date_nodash=current_date_nodash,
            reports=reports
        )

        # zapisujemy plik do oferty/api
        output_folder = os.path.join(settings.BASE_DIR, "oferty", "api")
        os.makedirs(output_folder, exist_ok=True)

        output_file = os.path.join(output_folder, "metadata.xml")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output_xml)

        self.stdout.write(self.style.SUCCESS(f"metadata.xml wygenerowany w {output_file}"))
