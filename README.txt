Introduction:
MusicLibraryConverter is a software written in Python 3 for batch converting of a music library containing flac files to mp3. It retains all meta tags and can be used iteratively.
It uses multi-threading and is based on ffmpeg (Windows) or avconv (Linux) as conversion backend and mutagenx as tagging library.

Installation:

Please install mutagenx:
https://pypi.python.org/pypi/mutagenx/

Then install ffmpeg (Windows, from http://www.ffmpeg.org/download.html) or avconv (Linux, via package system).
