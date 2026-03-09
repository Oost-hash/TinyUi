#
#  TinyUi - Editor Service Base
#  Copyright (C) 2026 Oost-hash
#

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from PySide2.QtCore import QObject, Signal
from PySide2.QtWidgets import QFileDialog, QWidget


class FileService(QObject):
    """Centrale service voor bestandsdialogen en I/O."""

    file_opened = Signal(str)  # pad naar geopend bestand
    file_saved = Signal(str)  # pad naar opgeslagen bestand
    error_occurred = Signal(str)

    def __init__(self, base_path: Optional[Path] = None):
        super().__init__()
        self.base_path = base_path or Path.home() / "TinyUI"
        self.base_path.mkdir(parents=True, exist_ok=True)

    # === Bestandskiezers ===
    def get_open_filename(
        self, parent: QWidget, title: str, directory: str, filter: str
    ) -> Optional[str]:
        """Toon Open dialoog en geef gekozen pad terug."""
        filename, _ = QFileDialog.getOpenFileName(parent, title, directory, filter)
        if filename:
            self.file_opened.emit(filename)
        return filename or None

    def get_save_filename(
        self, parent: QWidget, title: str, directory: str, filter: str
    ) -> Optional[str]:
        """Toon Save dialoog en geef gekozen pad terug."""
        filename, _ = QFileDialog.getSaveFileName(parent, title, directory, filter)
        if filename:
            self.file_saved.emit(filename)
        return filename or None

    # === JSON operaties ===
    def load_json(self, path: Union[str, Path]) -> dict:
        """Laad JSON van schijf. Retourneer lege dict bij fout."""
        path = Path(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            self.error_occurred.emit(f"Ongeldige JSON in {path.name}: {e}")
            return {}
        except Exception as e:
            self.error_occurred.emit(f"Fout bij laden {path.name}: {e}")
            return {}

    def save_json(
        self, path: Union[str, Path], data: dict, pretty: bool = True
    ) -> bool:
        """Sla JSON op. Retourneer True bij succes."""
        path = Path(path)
        try:
            with open(path, "w", encoding="utf-8") as f:
                if pretty:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(data, f, ensure_ascii=False)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Fout bij opslaan {path.name}: {e}")
            return False

    # === Directory operaties ===
    def ensure_dir(self, path: Union[str, Path]) -> Path:
        """Zorg dat directory bestaat."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    # === Backup ===
    def create_backup(self, file_path: Union[str, Path]) -> Optional[Path]:
        """Maak een backup van een bestand (kopie met timestamp)."""
        file_path = Path(file_path)
        if not file_path.exists():
            return None

        backup_dir = self.ensure_dir(file_path.parent / "backups")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name

        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            self.error_occurred.emit(f"Backup mislukt: {e}")
            return None
