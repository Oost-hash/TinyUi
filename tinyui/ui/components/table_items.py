"""Reusable table item types for QTableWidget."""

from PySide2.QtWidgets import QTableWidgetItem

from tinyui.backend.validator import is_string_number


class FloatTableItem(QTableWidgetItem):
    """Float type QTableWidgetItem with validation"""

    def __init__(self, value: float):
        """Convert & set float value to string"""
        super().__init__()
        self._value = 0.0
        self.setValue(value)

    def setValue(self, value: float):
        """Set value"""
        self._value = value
        self.setText(str(value))

    def value(self) -> float:
        """Get value"""
        return self._value

    def validate(self):
        """Validate value, replace invalid value with old value if invalid"""
        value = self.text()
        if is_string_number(value):
            self._value = float(value)
        else:
            self.setText(str(self._value))

    def __lt__(self, other):
        """Sort by value"""
        return self.value() < other.value()


class NumericTableItem(QTableWidgetItem):
    """Numeric QTableWidgetItem with sortable text"""

    def __init__(self, value: float, text: str):
        """Set numeric value & string text"""
        super().__init__()
        self.value = value
        self.setText(text)

    def __lt__(self, other):
        """Sort by value"""
        return self.value < other.value


class ClockTableItem(QTableWidgetItem):
    """Clock type QTableWidgetItem with validation"""

    def __init__(self, value: str):
        super().__init__()
        self._value = ""
        self.setText(value)

    def value(self) -> str:
        """Get value"""
        return self._value

    def validate(self):
        """Validate value, replace invalid value with old value if invalid"""
        value = self.__verify(self.text())
        if value:
            self._value = value
        self.setText(self._value)

    def __lt__(self, other):
        """Sort by value"""
        return self.value() < other.value()

    def __verify(self, clock_time: str) -> str:
        """Validate clock time (Hour:Minute) string"""
        try:
            data = clock_time.split(":")
            if len(data) != 2:
                raise ValueError
            hours = min(max(int(data[0]), 0), 24)
            minutes = min(max(int(data[1]), 0), 60)
            if minutes >= 60:
                hours += 1
                minutes = 0
            if hours >= 24:
                hours = 24
                minutes = 0
            return f"{hours:02d}:{minutes:02d}"
        except (AttributeError, IndexError, ValueError, TypeError):
            return ""
