#
#  TinyUi - Tools Menu
#  Copyright (C) 2025 Oost-hash
#

"""Tools menu."""

from PySide2.QtWidgets import QMenu

from ..dialogs import TrackMapViewer
from ..editors import (
    BrakeEditor, DriverStatsViewer, FuelCalculator, HeatmapEditor,
    TrackInfoEditor, TrackNotesEditor, TyreCompoundEditor,
    VehicleBrandEditor, VehicleClassEditor,
)


class ToolsMenu(QMenu):
    """Tools menu"""

    def __init__(self, title, parent):
        super().__init__(title, parent)
        self._parent = parent

        utility_fuelcalc = self.addAction("Fuel Calculator")
        utility_fuelcalc.triggered.connect(self.open_utility_fuelcalc)

        utility_driverstats = self.addAction("Driver Stats Viewer")
        utility_driverstats.triggered.connect(self.open_utility_driverstats)

        utility_mapviewer = self.addAction("Track Map Viewer")
        utility_mapviewer.triggered.connect(self.open_utility_mapviewer)
        self.addSeparator()

        editor_heatmap = self.addAction("Heatmap Editor")
        editor_heatmap.triggered.connect(self.open_editor_heatmap)

        editor_brakes = self.addAction("Brake Editor")
        editor_brakes.triggered.connect(self.open_editor_brakes)

        editor_compounds = self.addAction("Tyre Compound Editor")
        editor_compounds.triggered.connect(self.open_editor_compounds)

        editor_brands = self.addAction("Vehicle Brand Editor")
        editor_brands.triggered.connect(self.open_editor_brands)

        editor_classes = self.addAction("Vehicle Class Editor")
        editor_classes.triggered.connect(self.open_editor_classes)

        editor_trackinfo = self.addAction("Track Info Editor")
        editor_trackinfo.triggered.connect(self.open_editor_trackinfo)

        editor_tracknotes = self.addAction("Track Notes Editor")
        editor_tracknotes.triggered.connect(self.open_editor_tracknotes)

    def open_utility_fuelcalc(self):
        """Fuel calculator"""
        _dialog = FuelCalculator(self._parent)
        _dialog.show()

    def open_utility_driverstats(self):
        """Track driver stats viewer"""
        _dialog = DriverStatsViewer(self._parent)
        _dialog.show()

    def open_utility_mapviewer(self):
        """Track map viewer"""
        _dialog = TrackMapViewer(self._parent)
        _dialog.show()

    def open_editor_heatmap(self):
        """Edit heatmap preset"""
        _dialog = HeatmapEditor(self._parent)
        _dialog.show()

    def open_editor_brakes(self):
        """Edit brakes preset"""
        _dialog = BrakeEditor(self._parent)
        _dialog.show()

    def open_editor_compounds(self):
        """Edit compounds preset"""
        _dialog = TyreCompoundEditor(self._parent)
        _dialog.show()

    def open_editor_brands(self):
        """Edit brands preset"""
        _dialog = VehicleBrandEditor(self._parent)
        _dialog.show()

    def open_editor_classes(self):
        """Edit classes preset"""
        _dialog = VehicleClassEditor(self._parent)
        _dialog.show()

    def open_editor_trackinfo(self):
        """Edit track info"""
        _dialog = TrackInfoEditor(self._parent)
        _dialog.show()

    def open_editor_tracknotes(self):
        """Edit track notes"""
        _dialog = TrackNotesEditor(self._parent)
        _dialog.show()
