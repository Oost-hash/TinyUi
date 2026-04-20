#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.

"""Repository provider for physical persistence stores."""

from __future__ import annotations

import shutil
from pathlib import Path

from runtimeV2.persistence.backends import PersistenceBackend, create_persistence_backend
from runtimeV2.persistence.contracts import (
    BootstrapConfig,
    PersistencePaths,
    PersistenceStoreKind,
    PersistenceStoreRef,
)
from runtimeV2.persistence.registry import PersistenceRegistry
from runtimeV2.persistence.repository import PersistenceRepository


class PersistenceStoreProvider:
    """Open repositories for app and overlay stores."""

    def __init__(
        self,
        *,
        config: BootstrapConfig,
        paths: PersistencePaths,
        registry: PersistenceRegistry,
    ) -> None:
        self._config = config
        self._paths = paths
        self._registry = registry
        self._backends: dict[PersistenceStoreRef, PersistenceBackend] = {}
        self._repositories: dict[PersistenceStoreRef, PersistenceRepository] = {}

    def app_repository(self) -> PersistenceRepository:
        """Return the app store repository."""

        return self.repository(PersistenceStoreRef.app())

    def app_backend(self) -> PersistenceBackend:
        """Return the app store backend."""

        return self._backend(PersistenceStoreRef.app())

    def overlay_repository(self, overlay_uuid: str) -> PersistenceRepository:
        """Return the repository for one overlay store."""

        return self.repository(PersistenceStoreRef.overlay(overlay_uuid))

    def close_overlay(self, overlay_uuid: str) -> None:
        """Close one opened overlay store."""

        store_ref = PersistenceStoreRef.overlay(overlay_uuid)
        self._repositories.pop(store_ref, None)
        backend = self._backends.pop(store_ref, None)
        if backend is not None:
            backend.close()

    def delete_overlay_store(self, overlay_uuid: str) -> None:
        """Close and delete one overlay database file."""

        self.close_overlay(overlay_uuid)
        database_path = self._paths.overlay_database_path(overlay_uuid)
        if database_path.exists():
            database_path.unlink()
        overlay_dir = database_path.parent
        if overlay_dir.exists() and not any(overlay_dir.iterdir()):
            overlay_dir.rmdir()

    def delete_all_stores(self) -> None:
        """Close and delete all persistence database files."""

        self.close()
        if self._paths.app_database_path.exists():
            self._paths.app_database_path.unlink()
        if self._paths.overlays_dir.exists():
            shutil.rmtree(self._paths.overlays_dir)
            self._paths.overlays_dir.mkdir(parents=True, exist_ok=True)

    def repository(self, store_ref: PersistenceStoreRef) -> PersistenceRepository:
        """Return the repository for a physical store."""

        repository = self._repositories.get(store_ref)
        if repository is not None:
            return repository
        repository = PersistenceRepository(self._registry, self._backend(store_ref))
        self._repositories[store_ref] = repository
        return repository

    def close(self) -> None:
        """Close all opened stores."""

        for backend in self._backends.values():
            backend.close()
        self._backends.clear()
        self._repositories.clear()

    def _backend(self, store_ref: PersistenceStoreRef) -> PersistenceBackend:
        backend = self._backends.get(store_ref)
        if backend is not None:
            return backend
        backend = create_persistence_backend(
            self._config,
            sqlite_path=self._database_path(store_ref),
        )
        self._backends[store_ref] = backend
        return backend

    def _database_path(self, store_ref: PersistenceStoreRef) -> Path:
        if store_ref.kind == PersistenceStoreKind.APP:
            return self._paths.app_database_path
        if store_ref.kind == PersistenceStoreKind.OVERLAY:
            return self._paths.overlay_database_path(store_ref.store_id)
        raise ValueError(f"Unsupported persistence store kind: {store_ref.kind}")
