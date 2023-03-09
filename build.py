import os
import shutil

import PyInstaller.__main__

console = False
name = "ArknightsMaterials"

distFolder = "_dist/"
workFolder = "_build/"

command = ['ArknightsMaterials.py',
           '--name', name,
           '--icon', '../rock.ico',
           '--distpath', distFolder,
           '--workpath', workFolder,
           '--add-data', '../img;img',
           '--add-data', '../config.json;.',
           '--add-data', '../rock.ico;.',
           '--runtime-hook', 'addLib.py',
           '--specpath', workFolder,
           '--noconfirm']

if not console:
    command.append('--noconsole')

PyInstaller.__main__.run(command)

distFolderFull = distFolder + name + "/"
libFolder = distFolderFull + "lib/"
os.makedirs(libFolder, exist_ok=True)

doNotMove = [
    name + ".exe",
    "base_library.zip",
    "libopenblas64__v0.3.21-gcc_10_3_0.dll",
    "python3.dll",
    "python310.dll",

    "rock.ico",
    "config.json"
]

for f in os.listdir(distFolderFull):
    if os.path.isfile(distFolderFull + f):
        if f not in doNotMove and not f.startswith("libopenblas"):
            shutil.move(distFolderFull + f, libFolder + f)
