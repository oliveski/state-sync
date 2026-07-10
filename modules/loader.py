import os
import logging
from pathlib import Path
from modules.equation_parser import EquationParser

logger = logging.getLogger(__name__)

class EoSLoader:
    """Lists .eq files and loads them as EquationParser objects"""

    def __init__(self, directory='equations-of-state'):
        self.directory = Path(directory)

    def list_available(self):
        """Return dict of files (keys without extension)"""
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

    def available_equations(self):
        """Return dict of {name_without_extension: filename} for .eq files"""
        try:
            if not self.directory.exists():
                logger.error(f"Directory not found: {self.directory}")
                return {}
            
            eq_files = list(self.directory.glob('*.eq'))
            
            if not eq_files:
                logger.warning(f"No .eq files found in {self.directory}")
                return {}
            
            return {
                f.stem: f.name 
                for f in eq_files
            }
        
        except PermissionError:
            logger.error(f"Permission denied accessing: {self.directory}")
            return {}
        except Exception as e:
            logger.exception(f"Unexpected error reading directory: {e}")
            return {}



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
