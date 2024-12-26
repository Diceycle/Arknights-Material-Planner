import os
import shutil

import PyInstaller.__main__

console = False
name = "ArknightsMaterials"
windowHandlerName = "FindArknightsWindow"

distFolder = "_dist/"
workFolder = "_build/"

# Paths in args are relative to the workFolder (except runtime hook)
mainCommand = ['src/main/ArknightsMaterials.py',
               '--name', name,
               '--icon', '../src/main/rock.ico',
               '--contents-directory', '.',
               '--distpath', distFolder,
               '--workpath', workFolder,
               '--add-data', '../src/main/img;img',
               '--add-data', '../src/build/config-defaults.json;.',
               '--add-data', '../src/main/rock.ico;.',
               '--add-data', '../README.md;.',
               '--runtime-hook', 'src/build/addLib.py',
               '--specpath', workFolder,
               '--noconfirm']

if not console:
    mainCommand.append('--noconsole')

windowHandlerCommand = ['src/main/WindowHandler.py',
                        '--name', windowHandlerName,
                        '--distpath', distFolder,
                        '--workpath', workFolder,
                        '--specpath', workFolder,
                        '--noconfirm',
                        '--onefile']

PyInstaller.__main__.run(mainCommand)
PyInstaller.__main__.run(windowHandlerCommand)

distFolderFull = distFolder + name + "/"
libFolder = distFolderFull + "lib/"
os.makedirs(libFolder, exist_ok=True)

doNotMove = [
    name + ".exe",
    "base_library.zip",
    "libopenblas64__v0.3.21-gcc_10_3_0.dll",
    "python3.dll",
    "python313.dll",

    "rock.ico",
    "config-defaults.json",
    "README.md"
]

for f in os.listdir(distFolderFull):
    if os.path.isfile(distFolderFull + f):
        if f not in doNotMove and not f.startswith("libopenblas"):
            shutil.move(distFolderFull + f, libFolder + f)

shutil.move(distFolder + windowHandlerName + ".exe", distFolderFull + windowHandlerName + ".exe")
