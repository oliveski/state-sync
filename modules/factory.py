from modules.equation_parser import EquationParser
from modules.equation_of_state import (
    AmbientPressure, ThermalPressure, ElectronicPressure,
    EquationOfState
)


def create_eos(parser: EquationParser) -> EquationOfState:
    """Instantiate EOS with full validation before construction."""

    ambient_model = parser.model_ambient
    thermal_model = parser.model_thermal
    electronic_model = parser.model_electronic

    ambient_registry = AmbientPressure.REGISTRY
    thermal_registry = ThermalPressure.REGISTRY
    electronic_registry = ElectronicPressure.REGISTRY

    errors = []

    # --- Ambient validation ---
    ambient_cls = None
    if ambient_model != 'none':
        ambient_cls = ambient_registry.get(ambient_model)
        if not ambient_cls:
            errors.append(f"Unknown ambient model '{ambient_model}'")
        else:
            required = ambient_cls.REQUIRED_PARAMS
            missing = required - set(parser.params.keys())
            if missing:
                errors.append(f"Ambient '{ambient_model}' needs: {missing}")

    # --- Thermal validation ---
    thermal_cls = None
    if thermal_model != 'none':
        thermal_cls = thermal_registry.get(thermal_model)
        if not thermal_cls:
            errors.append(f"Unknown thermal model '{thermal_model}'")
        else:
            required = thermal_cls.REQUIRED_PARAMS
            missing = required - set(parser.params.keys())
            if missing:
                errors.append(f"Thermal '{thermal_model}' needs: {missing}")

    # --- Electronics validation ---
    electronic_cls = None
    if electronic_model != 'none':
        # Similar pattern for electronic models to be implemented
        pass

    if errors:
        raise ValueError("\n".join(errors))

    if ambient_cls:
        ambient_params = {
                k: v
                for k, v in parser.params.items()
                if k in ambient_cls.REQUIRED_PARAMS
        }

    if thermal_cls:
        thermal_params = {
                k: v
                for k, v in parser.params.items()
                if k in thermal_cls.REQUIRED_PARAMS
        }

    if electronic_cls:
        electronic_params = {
                k: v
                for k, v in parser.params.items()
                if k in electronic_cls.REQUIRED_PARAMS
        }


    return EquationOfState(
        ambient=AmbientPressure(ambient_params, ambient_model) if ambient_cls else None,
        thermal=ThermalPressure(thermal_params, thermal_model) if thermal_cls else None,
        electronic=ElectronicPressure(electronic_params, electronic_model) if electronic_cls else None
    )
