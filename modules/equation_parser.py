from pathlib import Path
from typing import Dict, Any


class EquationParser:
    """Parses EOS parameter files without model-aware validation."""

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        self.params: Dict[str, Any] = {}
        self.metadata: Dict[str, str] = {}

        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        self._parse_file(self.filepath)

    def _parse_file(self, filepath: Path) -> None:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or ':' not in line:
                    continue

                key, value = line.split(':', 1)
                key = key.strip().upper()
                value = value.strip()

                # Metadata keys
                if key == 'COMMENT':
                    self.metadata['comment'] = value
                elif key == 'MODEL_AMBIENT':
                    self.metadata['model_ambient'] = value.lower()
                elif key == 'MODEL_THERMAL':
                    self.metadata['model_thermal'] = value.lower()
                elif key == 'MODEL_ELECTRONIC':
                    self.metadata['model_electronic'] = value.lower()
                else:
                    # Try numeric conversion
                    try:
                        self.params[key] = float(value)
                    except ValueError:
                        self.params[key] = value

    @property
    def comment(self) -> str:
        return self.metadata.get('comment', '')

    @property
    def model_ambient(self) -> str:
        return self.metadata.get('model_ambient', '')

    @property
    def model_thermal(self) -> str:
        return self.metadata.get('model_thermal', '')

    @property
    def model_electronic(self) -> str:
        return self.metadata.get('model_electronic', 'none')

    def to_dict(self) -> Dict[str, Any]:
        """Return params + model info for factory consumption."""
        d = dict(self.params)
        d['_MODEL_AMBIENT_'] = self.model_ambient
        d['_MODEL_THERMAL_'] = self.model_thermal
        d['_MODEL_ELECTRONIC_'] = self.model_electronic
        return d
