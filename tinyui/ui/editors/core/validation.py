#
#  TinyUi - Validation Framework
#  Copyright (C) 2026 Oost-hash
#

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar


class ValidationSeverity(Enum):
    ERROR = auto()  # Blocks save
    WARNING = auto()  # Shows warning but allows save
    INFO = auto()  # Just informational


@dataclass(frozen=True)
class ValidationResult:
    """Single validation issue."""

    field: str  # Field name or empty for general
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR

    @property
    def is_error(self) -> bool:
        return self.severity == ValidationSeverity.ERROR


class ValidationContext:
    """Holds data being validated and accumulated results."""

    def __init__(self, data: Dict, key: str = ""):
        self.data = data
        self.key = key  # Current item key (e.g., brake name)
        self.results: List[ValidationResult] = []

    def add_error(self, field: str, message: str):
        self.results.append(ValidationResult(field, message, ValidationSeverity.ERROR))

    def add_warning(self, field: str, message: str):
        self.results.append(
            ValidationResult(field, message, ValidationSeverity.WARNING)
        )

    def add_info(self, field: str, message: str):
        self.results.append(ValidationResult(field, message, ValidationSeverity.INFO))

    @property
    def is_valid(self) -> bool:
        return not any(r.is_error for r in self.results)

    @property
    def errors(self) -> List[ValidationResult]:
        return [r for r in self.results if r.severity == ValidationSeverity.ERROR]

    @property
    def warnings(self) -> List[ValidationResult]:
        return [r for r in self.results if r.severity == ValidationSeverity.WARNING]


class Validator(ABC):
    """Base validator - subclass for specific validation logic."""

    @abstractmethod
    def validate(self, context: ValidationContext):
        """Perform validation, add results to context."""
        pass


class ValidationChain:
    """Chains multiple validators together."""

    def __init__(self):
        self._validators: List[Validator] = []

    def add(self, validator: Validator) -> "ValidationChain":
        self._validators.append(validator)
        return self

    def validate(self, data: Dict, key: str = "") -> ValidationContext:
        """Run all validators and return context with results."""
        context = ValidationContext(data, key)

        for validator in self._validators:
            validator.validate(context)
            # Early exit on critical errors? Optional.

        return context


# Common reusable validators


class RequiredFieldValidator(Validator):
    """Validates that required fields are present and not empty."""

    def __init__(self, fields: Dict[str, str]):
        """
        fields: dict of field_name -> display_name
        """
        self._fields = fields

    def validate(self, context: ValidationContext):
        for field, display_name in self._fields.items():
            value = context.data.get(field)
            if value is None or value == "" or value == 0:
                context.add_error(field, f"{display_name} is required")


class RangeValidator(Validator):
    """Validates numeric fields are within range."""

    def __init__(
        self,
        field: str,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        display_name: str = None,
    ):
        self._field = field
        self._min = min_val
        self._max = max_val
        self._display = display_name or field

    def validate(self, context: ValidationContext):
        value = context.data.get(self._field)

        if value is None:
            return  # Let RequiredFieldValidator handle this

        try:
            num = float(value)
        except (TypeError, ValueError):
            context.add_error(self._field, f"{self._display} must be a number")
            return

        if self._min is not None and num < self._min:
            context.add_error(
                self._field, f"{self._display} must be at least {self._min}"
            )

        if self._max is not None and num > self._max:
            context.add_error(
                self._field, f"{self._display} must be at most {self._max}"
            )


class UniqueKeyValidator(Validator):
    """Validates uniqueness across a collection."""

    def __init__(self, get_all_keys: Callable[[], List[str]], field_name: str = "name"):
        self._get_keys = get_all_keys
        self._field = field_name

    def validate(self, context: ValidationContext):
        current_key = context.key
        all_keys = self._get_keys()

        # Check for case-insensitive duplicates (more than one match)
        matches = sum(1 for k in all_keys if k.lower() == current_key.lower())
        if matches > 1:
            context.add_error(
                self._field, f"'{current_key}' already exists (case-insensitive)"
            )


class RegexValidator(Validator):
    """Validates string matches pattern."""

    def __init__(self, field: str, pattern: str, message: str = "Invalid format"):
        import re

        self._field = field
        self._pattern = re.compile(pattern)
        self._message = message

    def validate(self, context: ValidationContext):
        value = context.data.get(self._field, "")
        if value and not self._pattern.match(str(value)):
            context.add_error(self._field, self._message)
