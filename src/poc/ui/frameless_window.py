from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QCursor, QIcon
from PySide6.QtWidgets import QApplication, QMenuBar, QVBoxLayout, QWidget

from .title_bar import TitleBar


class FramelessWindow(QWidget):
    """
    Frameloos venster met eigen titelbalk, menubalk en native resize.
    - De buitenrand heeft een afgeronde hoek en achtergrondkleur via QSS (objectName "mainWindow").
    - Titelbalk en menubalk hebben een eigen achtergrond (geen transparantie).
    - De inhoud (set_content) moet zelf marges hanteren om niet over de afgeronde hoeken te vallen.
    """

    resizeStarted = Signal()
    resizeFinished = Signal()

    RESIZE_MARGIN = 6

    def __init__(
        self,
        title: str = "",
        parent=None,
        closable=True,
        minimizable=False,
        maximizable=True,
        icon: QIcon = None,
    ):
        super().__init__(parent)
        self.setObjectName("mainWindow")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMouseTracking(True)

        self._resizing = False
        self._in_grip = False
        self._last_edges = Qt.Edges()
        self._maximized = False

        # Hoofdlayout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # Titelbalk (normale achtergrond, geen transparantie)
        self.title_bar = TitleBar(title, self, closable, minimizable, maximizable, icon)
        self._main_layout.addWidget(self.title_bar)

        # Menubalk (wordt later aangemaakt)
        self._menubar = None

        # Layout voor inhoud
        self._content_layout = QVBoxLayout()
        self._main_layout.addLayout(self._content_layout)

        self._content = None

        self.installEventFilter(self)

    def set_content(self, widget: QWidget):
        """Vervang de huidige inhoud."""
        if self._content is not None:
            self._content_layout.removeWidget(self._content)
            self._content.deleteLater()
        self._content = widget
        self._content_layout.addWidget(widget)

    def content(self) -> QWidget:
        return self._content

    def menubar(self) -> QMenuBar:
        """Geef de menubalk (maak aan indien nodig)."""
        if self._menubar is None:
            self._menubar = QMenuBar(self)
            self._menubar.setFocusPolicy(Qt.NoFocus)
            self._main_layout.insertWidget(1, self._menubar)
        return self._menubar

    def enable_mouse_tracking_recursive(self):
        self._set_mouse_tracking_recursive(self)

    def _set_mouse_tracking_recursive(self, widget):
        widget.setMouseTracking(True)
        for child in widget.findChildren(QWidget):
            child.setMouseTracking(True)

    def _get_resize_edges(self, pos) -> Qt.Edges:
        r = self.rect()
        edges = Qt.Edges()
        x, y = pos.x(), pos.y()
        if x <= self.RESIZE_MARGIN:
            edges |= Qt.LeftEdge
        if x >= r.width() - self.RESIZE_MARGIN:
            edges |= Qt.RightEdge
        if y <= self.RESIZE_MARGIN:
            edges |= Qt.TopEdge
        if y >= r.height() - self.RESIZE_MARGIN:
            edges |= Qt.BottomEdge
        return edges

    def _cursor_for_edges(self, edges: Qt.Edges) -> QCursor:
        if edges == (Qt.LeftEdge | Qt.TopEdge) or edges == (
            Qt.RightEdge | Qt.BottomEdge
        ):
            return QCursor(Qt.SizeFDiagCursor)
        if edges == (Qt.RightEdge | Qt.TopEdge) or edges == (
            Qt.LeftEdge | Qt.BottomEdge
        ):
            return QCursor(Qt.SizeBDiagCursor)
        if edges & (Qt.LeftEdge | Qt.RightEdge):
            return QCursor(Qt.SizeHorCursor)
        if edges & (Qt.TopEdge | Qt.BottomEdge):
            return QCursor(Qt.SizeVerCursor)
        return QCursor(Qt.ArrowCursor)

    def _enter_grip(self, edges):
        QApplication.setOverrideCursor(self._cursor_for_edges(edges))

    def _update_grip_cursor(self, edges):
        QApplication.changeOverrideCursor(self._cursor_for_edges(edges))

    def _leave_grip(self):
        QApplication.restoreOverrideCursor()

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            maximized = self.windowState() & Qt.WindowMaximized
            if maximized != self._maximized:
                self._maximized = maximized
                self.title_bar.update_maximize_icon(maximized)
        super().changeEvent(event)

    def eventFilter(self, obj, event):
        try:
            if obj is None or not isinstance(obj, QWidget):
                return False
        except RuntimeError:
            return False

        etype = event.type()
        if etype not in (
            QEvent.MouseMove,
            QEvent.MouseButtonPress,
            QEvent.MouseButtonRelease,
        ):
            return False

        if self._maximized:
            if self._in_grip:
                self._leave_grip()
                self._in_grip = False
            return False

        global_pos = event.globalPos()
        local_pos = self.mapFromGlobal(global_pos)
        edges = self._get_resize_edges(local_pos)
        in_grip_now = bool(edges)

        if etype == QEvent.MouseMove and not self._resizing:
            if in_grip_now != self._in_grip:
                if in_grip_now:
                    self._enter_grip(edges)
                else:
                    self._leave_grip()
                self._in_grip = in_grip_now
            elif in_grip_now and edges != self._last_edges:
                self._update_grip_cursor(edges)
            self._last_edges = edges

        elif etype == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            if edges:
                if self._in_grip:
                    self._leave_grip()
                    self._in_grip = False
                self._resizing = True
                self.resizeStarted.emit()
                self.windowHandle().startSystemResize(edges)
                return True

        elif etype == QEvent.MouseButtonRelease and self._resizing:
            self._resizing = False
            self.resizeFinished.emit()
            return True

        return False
