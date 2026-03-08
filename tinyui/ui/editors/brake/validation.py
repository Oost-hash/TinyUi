#
#  TinyUi - Brake Editor Validation
#  Copyright (C) 2026 Oost-hash
#

from ..core.validation import (
    RangeValidator,
    RequiredFieldValidator,
    UniqueKeyValidator,
    ValidationChain,
)


def create_brake_validator(get_all_brake_names: callable) -> ValidationChain:
    """
    Create validation chain for brake editor.

    Usage:
        validator = create_brake_validator(lambda: list(vm.data.keys()))
        context = validator.validate(brake_data, brake_name)
        if not context.is_valid:
            show_errors(context.errors)
    """
    return (
        ValidationChain()
        .add(
            RequiredFieldValidator(
                {
                    "heatmap": "Heatmap",
                }
            )
        )
        .add(
            RangeValidator(
                "failure_thickness",
                min_val=0,
                max_val=100,
                display_name="Failure Thickness",
            )
        )
        .add(UniqueKeyValidator(get_all_brake_names, "brake_name"))
    )
