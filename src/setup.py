# Run with "python -OO setup.py py2exe"
from distutils.core import setup
import py2exe,sys,os

from distutils.sysconfig import get_python_lib

opts = {
    "py2exe": {
#        "includes": ['ctypes',
#                     'sip',
#                     ],
        "dll_excludes": [
                         "MSVCP90.dll",
                         "MSWSOCK.dll",
                         "mswsock.dll",
                         "powrprof.dll",
                         ],
        "dist_dir": "../bin",
        "optimize":2,
        'bundle_files': 1, 
        'compressed': True,
    }
}

setup(
      name="MusicLibraryConverter",
      version="1.0",
      author="Eike Thaden",
      author_email="true@assertion.eu",
      #url="https://launchpad.net/liftr",
      license="GNU General Public License (GPL)",
      windows=[{'script': 'MusicLibraryConverter.py'}], 
      options=opts, 
      zipfile = None, 
#      data_files=[('platforms', [get_python_lib()+'\\PyQt5\\plugins\\platforms\\qwindows.dll'])]
    )
