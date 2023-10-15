import os
import subprocess
from pathlib import Path
import nicegui

cmd = [
    'python',
    '-m', 'PyInstaller',
    'main.py', # your main file with ui.run()
    '--name', 'OpenLLM', # name of your app
    '--onefile',
    #'--windowed', # prevent console appearing, only use with ui.run(native=True, ...)
    '--add-data', f'{Path(nicegui.__file__).parent.parent}{os.pathsep}site-packages',
    
]
subprocess.call(cmd)
print(f'{Path(nicegui.__file__).parent.parent}{os.pathsep}nicegui')