from abc import ABC, abstractmethod
from typing import Dict, Union, Optional
import numpy as np


# =============================================================================
# BASE CLASSES
# =============================================================================

class PressureComponent(ABC):
    """Abstract base class for pressure contribution components."""
    
    @abstractmethod
    def __call__(self, V: Union[float, np.ndarray], T: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Calculate pressure contribution for given volume and temperature."""
        pass


# =============================================================================
# AMBIENT PRESSURE SUBMODELS (Isothermal compression at T₀)
# =============================================================================

class BirchMurnaghan(PressureComponent):
    """Third-order Birch-Murnaghan isothermal EOS."""

    REQUIRED_PARAMS = frozenset(['K0', 'K0P', 'VOLUME'])
    
    def __init__(self, params: Dict):
        self.K_0 = float(params['K0'])
        self.K0P = float(params['K0P'])
        self.V_0 = float(params['VOLUME'])
    
    def __call__(self, V, T):
        V = np.asanyarray(V, dtype=float)
        T = np.asanyarray(T, dtype=float)
        V_bc, T_bc = np.broadcast_arrays(V, T)

        eta = (V_bc / self.V_0)**(1/3)
        f_elastic = 0.5 * (eta**-2 - eta**(-8/3))
        
        P = 3 * self.K_0 * f_elastic * (1 + 1.5 * (self.K0P - 4) * f_elastic)

        if np.ndim(V) == 0 and np.ndim(T) == 0:
            return float(P.item())
        return P


class Vinet(PressureComponent):
    """Vinet universal equation of state (isothermal)."""

    REQUIRED_PARAMS = frozenset(['K0', 'K0P', 'VOLUME'])
    
    def __init__(self, params: Dict):
        self.K_0 = float(params['K0'])
        self.K0P = float(params['K0P'])
        self.V_0 = float(params['VOLUME'])
    
    def __call__(self, V, T=None):
        V = np.asanyarray(V, dtype=float)
        phi = (V / self.V_0)**(1/3)
        r = 1 - phi
        
        denom = 3 * r**2
        numer = (3 * self.K_0 * (1 + r))
        exp_factor = np.exp((3/2) * (self.K0P - 1) * r)
        
        # Handle division by zero when V ≈ V_0
        safe_denom = np.where(denom == 0, 1e-16, denom)
        P = (numer / safe_denom) * exp_factor
        
        return P if np.ndim(V) else P.item()


class Murnaghan(PressureComponent):
    """Original Murnaghan EOS (simpler, less accurate at high P)."""

    REQUIRED_PARAMS = frozenset(['K0', 'K0P', 'VOLUME'])
    
    def __init__(self, params: Dict):
        self.K_0 = float(params['K0'])
        self.K0P = float(params['K0P'])
        self.V_0 = float(params['VOLUME'])
    
    def __call__(self, V, T=None):
        V = np.asanyarray(V, dtype=float)
        ratio = V / self.V_0
        
        # Original form (avoid K0P=1 singularity)
        if abs(self.K0P - 1) < 1e-10:
            P = self.K_0 * np.log(ratio)
        else:
            P = (self.K_0 / (self.K0P - 1)) * ((ratio**(-(self.K0P - 1))) - 1)
        
        return -P if np.ndim(V) else -P.item()


# =============================================================================
# AMBIENT PRESSURE COMPONENT WRAPPER
# =============================================================================

class AmbientPressure(PressureComponent):
    """Wrapper that selects specific ambient model based on type."""
    
    REGISTRY = {
        'birch-murnaghan': BirchMurnaghan,
        'bm3': BirchMurnaghan,
        'vinet': Vinet,
        'v': Vinet,
        'murnaghan': Murnaghan,
    }
    
    def __init__(self, params: Dict, model_type: str = 'birch-murnaghan'):
        cls = self.REGISTRY.get(model_type.lower())
        if not cls:
            raise ValueError(f"Unknown ambient model '{model_type}'. Available: {list(self.REGISTRY.keys())}")
        self.submodel = cls(params)
    
    def __call__(self, V, T=None):
        return self.submodel(V, T)


# =============================================================================
# THERMAL PRESSURE SUBMODELS (ΔP from heating at fixed V)
# =============================================================================

class MieGruneisen(PressureComponent):
    """Mie-Grüneisen thermal pressure model."""

    # fix this to check for optional labels (THETA_D == DEBYE_TEMP)
    REQUIRED_PARAMS = frozenset(['ALPHAT', 'THETA_D', 'GRUNEISEN_PARAM', 'DELTA_D'])
    
    def __init__(self, params: Dict):
        self.ALPHAT = float(params.get('ALPHAT', 2.57e-5))
        self.THETA_D = float(params.get('THETA_D', float(params.get('DEBYE_TEMP', 240))))
        self.GAMMA_GRUNEISEN = float(params.get('GRUNEISEN_PARAM', float(params.get('GAMMA', 2.0))))
        self.DELTA_DEBYE = float(params.get('DELTA_D', 5.78e-9))
    
    def __call__(self, V, T):
        V = np.asanyarray(V, dtype=float)
        T = np.asanyarray(T, dtype=float) if np.ndim(T) else np.array([float(T)])
        
        # Debye approximation: integral yields ~ linear dependence at high T
        # Simplified: P_th ≈ α · K · (T - T_ref)
        ref_T = 300.0
        theta_ratio = T / self.THETA_D
        
        # At T ≫ Θᴅ, Debye heat capacity → constant (Dulong-Petit)
        high_temp_approx = 3 * (1 - (theta_ratio)/6 + (theta_ratio)**2/24)
        
        gamma_vol = self.GAMMA_GRUNEISEN  # Could add volume dependence here
        delta_T = self.ALPHAT * T + self.DELTA_DEBYE * (T**2)
        
        P_th = delta_T * gamma_vol * T * high_temp_approx
        
        # Return scalar if input was scalar
        if np.ndim(V) == 0:
            return P_th[0].item() if np.ndim(P_th) else P_th.item()
        return P_th


# =============================================================================
# THERMAL PRESSURE COMPONENT WRAPPER
# =============================================================================

class ThermalPressure(PressureComponent):
    """Wrapper for thermal pressure submodels."""
    
    REGISTRY = {
        'gruneisen': MieGruneisen,
        'mie-gruneisen': MieGruneisen,
        'mg': MieGruneisen,
        'mgd': MieGruneisen,
    }
    
    def __init__(self, params: Dict, model_type: str = 'gruneisen'):
        cls = self.REGISTRY.get(model_type.lower())
        if not cls:
            raise ValueError(f"Unknown thermal model '{model_type}'. Available: {list(self.REGISTRY.keys())}")
        self.submodel = cls(params)
    
    def __call__(self, V, T):
        return self.submodel(V, T)


# =============================================================================
# ELECTRONIC PRESSURE SUBMODELS
# =============================================================================

# Placeholder model to be revised
class FreeElectronGas(PressureComponent):
    """Degenerate electron gas pressure (Sommerfeld expansion)."""

    REQUIRED_PARAMS = frozenset([])
    
    def __init__(self, params: Dict):
        self.GAMMA_ELEC = float(params.get('GAMMA_ELEC', 1.5))
        self.ELECTRON_DENSITY = float(params.get('ELECTRON_DENSITY', 6.4e29))
        self.ELEC_COEF = float(params.get('EL_COEF', 0.0))
    
    def __call__(self, V, T):
        P_total = 0
        
        return P_total


# Placeholder model to be revised
class ThomasFermi(PressureComponent):
    """Thomas-Fermi statistical atom model (high-Z materials)."""

    REQUIRED_PARAMS = frozenset([])
    
    def __init__(self, params: Dict):
        self.Z_ATOMIC = int(params.get('Z_ATOMIC', 78))  # For Pt
        self.A_MASS = float(params.get('A_MASS', 195.08))
        self.RADIUS_CUTOFF = float(params.get('R_RADIUS', 0.1))
    
    def __call__(self, V, T):
        P_total = 0
        return P_total


# =============================================================================
# ELECTRONIC PRESSURE COMPONENT WRAPPER
# =============================================================================

class ElectronicPressure(PressureComponent):
    """Wrapper for electronic pressure submodels."""
    
    REGISTRY = {
        'free-electron': FreeElectronGas,
        'fe': FreeElectronGas,
        'electron_gas': FreeElectronGas,
        'tf': ThomasFermi,
        'thomas-fermi': ThomasFermi,
    }
    
    def __init__(self, params: Dict, model_type: str = 'free-electron'):
        cls = self.REGISTRY.get(model_type.lower())
        if not cls:
            raise ValueError(f"Unknown electronic model '{model_type}'. Available: {list(self.REGISTRY.keys())}")
        self.submodel = cls(params)
    
    def __call__(self, V, T):
        return self.submodel(V, T)


# =============================================================================
# COMPOSITE EQUATION OF STATE
# =============================================================================

class EquationOfState(PressureComponent):
    """Main container combining all three pressure contributions."""
    
    def __init__(
        self,
        ambient: AmbientPressure,
        thermal: ThermalPressure,
        electronic: ElectronicPressure
    ):
        self.ambient = ambient
        self.thermal = thermal
        self.electronic = electronic

        if all(c is None for c in [ambient, thermal, electronic]):
            raise ValueError("At least one component must be provided")
    
    def __call__(self, V, T):
        return sum((c(V, T) if c else 0)
                   for c in [self.ambient, self.thermal, self.electronic])
    
    def decomposition(self, V, T):
        """Return individual contributions separately for analysis."""
        result = {
                'ambient': self.ambient(V, T) if self.ambient else None,
                'thermal': self.thermal(V, T) if self.thermal else None,
                'electronic': self.electronic(V, T) if self.electronic else None
        }
        result['total'] = sum(val for val in result.values() if val is not None)
        return result
