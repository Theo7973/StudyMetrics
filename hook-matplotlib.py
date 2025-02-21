# hook-matplotlib.py (simplified)
from pathlib import Path
import matplotlib

# Get matplotlib's installation path
mpl_data_path = Path(matplotlib.__file__).parent / 'mpl-data'

# Specify data files to include
datas = [
    (str(mpl_data_path / '*.*'), 'matplotlib/mpl-data'),
    (str(mpl_data_path / 'fonts'), 'matplotlib/mpl-data/fonts'),
    (str(mpl_data_path / 'images'), 'matplotlib/mpl-data/images')
]