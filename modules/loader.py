import logging
from pathlib import Path
from modules.equation_parser import EquationParser

logger = logging.getLogger(__name__)

class EoSLoader:
    """Lists .eq files and loads them as EquationParser objects"""

    def __init__(self, directory='equations-of-state'):
        self.directory = Path(directory)

    def list_available(self):
        """Return list of filenames (without extension)"""
        try:
            files = [
                    f
                    for f in os.listdir(self.directory)
                    if os.path.isfile(os.path.join(self.directory, f))
            ]

            if not files:
                logger.warning(f"No equations found in {self.directory}")
                return files
            return [f.stem for f in self.directory.glob('*.eq')]
        except FileNotFoundError:
            logger.error(f"Directory not found: {self.directory}")

    def load(self, name):
        """Load a single .eq file by stem or filename"""
        path = self.directory / f'{name}.eq'
        if not path.exists():
            # Allow passing full filename too
            path = self.directory / name
        if not path.exists():
            logger.error(f"Failed to load equation: {name} - file not found")
            raise FileNotFoundError(f'No equation file: {name}')
        logger.debug(f"Successfully loaded equation: {name}")
        return EquationParser(path)

    def load_all(self):
        """Load all .eq files, return dict of {name: EquationParser}"""
        return {f.stem: self.load(f.stem) for f in self.directory.glob('*.eq')}
