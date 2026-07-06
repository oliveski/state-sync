from pathlib import Path
from modules.equation_parser import EquationParser

class EoSLoader:
    """Lists .eq files and loads them as EquationParser objects"""

    def __init__(self, directory='equations-of-state'):
        self.directory = Path(directory)

    def list_available(self):
        """Return list of filenames (without extension)"""
        return [f.stem for f in self.directory.glob('*.eq')]

    def load(self, name):
        """Load a single .eq file by stem or filename"""
        path = self.directory / f'{name}.eq'
        if not path.exists():
            # Allow passing full filename too
            path = self.directory / name
        if not path.exists():
            raise FileNotFoundError(f'No equation file: {name}')
        return EquationParser(path)

    def load_all(self):
        """Load all .eq files, return dict of {name: EquationParser}"""
        return {f.stem: self.load(f.stem) for f in self.directory.glob('*.eq')}
