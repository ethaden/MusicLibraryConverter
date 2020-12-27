Introduction:
MusicLibraryConverter is a software written in Python 3 for batch converting of a music library containing flac files to mp3. It retains all meta tags and can be used iteratively.
It uses multi-threading and is based on ffmpeg (Windows) or avconv (Linux) as conversion backend, mutagenx as tagging library and psutil for renicing processes.

Installation:

Either use pipenv by running (in main project folder):
pipenv install

then enter virtual environment with
pipenv shell

or run directly with
pipenv run

Please install mutagenx:
https://pypi.python.org/pypi/mutagenx/
and psutil
https://pypi.python.org/pypi?:action=display&name=psutil#downloads

Then install ffmpeg (on Windows from http://www.ffmpeg.org/download.html, on Linux via package manager).
