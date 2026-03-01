import os
import shutil
from django.core.management.base import BaseCommand
from sheet_generator.apps import APP_DIR
from django_sopila.settings import MEDIA_ROOT, BASE_DIR

class Command(BaseCommand):
    help = 'Clears data directories (audio, predictions, pdfs)'

    def handle(self, *args, **options):
        # Mapping labels to paths for clearer output
        folders = {
            "Audio (MEDIA_ROOT)": MEDIA_ROOT,
            "HDF5 Predictions": os.path.join(APP_DIR, 'raw_predictions'),
            "Generated PDFs": os.path.join(APP_DIR, 'pdf')
        }

        for label, folder_path in folders.items():
            if os.path.exists(folder_path):
                self.stdout.write(f"Checking: {label}...")
                
                files_in_folder = os.listdir(folder_path)
                count = 0
                
                for filename in files_in_folder:
                    file_path = os.path.join(folder_path, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            count += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  Error deleting {filename}: {e}"))
                
                # Separate print for each folder
                if count > 0:
                    self.stdout.write(self.style.SUCCESS(f"  Successfully deleted {count} files from {label}."))
                else:
                    self.stdout.write(f"  Folder {label} was already empty.")
            else:
                self.stdout.write(self.style.WARNING(f"Directory not found: {label}"))

        self.stdout.write(self.style.MIGRATE_SUCCESS("\nFull cleanup process finished."))