# tinyui/ui/common/validators.py
from PySide2.QtCore import QRegularExpression
from PySide2.QtGui import QDoubleValidator, QIntValidator, QRegularExpressionValidator

QVAL_INTEGER = QIntValidator(-999999, 999999)
QVAL_FLOAT = QDoubleValidator(-999999.9999, 999999.9999, 6)
QVAL_COLOR = QRegularExpressionValidator(QRegularExpression("^#[0-9a-fA-F]*"))
QVAL_HEATMAP = QRegularExpressionValidator(QRegularExpression("[0-9a-zA-Z_]*"))
QVAL_FILENAME = QRegularExpressionValidator(QRegularExpression('[^\\\\/:*?"<>|]*'))
