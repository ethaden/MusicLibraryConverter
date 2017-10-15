#!/usr/bin/python3
# encoding: utf-8
#
# (c) 2014 Eike Thaden
#
# This file is part of MusicLibraryConverter.
#
# MusicLibraryConverter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MusicLibraryConverter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MusicLibraryConverter.  If not, see <http://www.gnu.org/licenses/>.
'''
MusicLibraryConverter -- Batch convert your music library from flac to mp3.

MusicLibraryConverter is a software written in Python 3 for batch converting of a music library containing flac files to mp3. It retains all meta tags and can be used iteratively.
It uses multi-threading and is based on ffmpeg (Windows) or avconv (Linux) as conversion backend and mutagenx as tagging library. Note that ffmpeg.exe/avconv must be available and it
must be possible to find them via the PATH environment. The Python 3 library mutagenx (https://pypi.python.org/pypi/mutagenx/1.22.1) must be installed.  

@author:     Eike Thaden

@copyright:  2014 Eike Thaden. All rights reserved.

@license:    GPL v3

@contact:    true@assertion.eu
@deffield    updated: Updated
'''

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import os
import platform
import signal
import sys
import logging

import psutil

from musiclibraryconverter import MusicLibraryConverterMaster


__all__ = []
__version__ = 0.1
__date__ = '2014-02-20'
__updated__ = '2014-02-20'
mediaLibraryConverterMaster = None

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def signal_handler(signal, frame):
    global mediaLibraryConverterMaster
    if (mediaLibraryConverterMaster != None):
        mediaLibraryConverterMaster.interrupt()
    #sys.exit(0)

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    try:
        if argv is None:
            argv = sys.argv
        else:
            sys.argv.extend(argv)
            
        myPath = os.path.dirname(argv[0])
        sys.path.append(myPath)
    
        program_name = os.path.basename(sys.argv[0])
        program_version = "v%s" % __version__
        program_build_date = str(__updated__)
        program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
        program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
        program_license = '''%s
    
      Created by Eike Thaden on %s.
      Copyright 2014 Eike Thaden. All rights reserved.
    
      Licensed under the Apache License 2.0
      http://www.apache.org/licenses/LICENSE-2.0
    
      Distributed on an "AS IS" basis without warranties
      or conditions of any kind, either express or implied.
    
    USAGE
    ''' % (program_shortdesc, str(__date__))

        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-r", "--recursive", dest="recurse", action="store_true", help="recurse into subfolders [default: %(default)s]")
        parser.add_argument('-O', '--overwrite', dest='overwrite', action="store_true", help="overwrite existing files [default: %(default)s]", default=False)
        parser.add_argument('-o', '--overwriteIfNewer', dest='overwriteIfSrcNewer', action="store_true", help="overwrite existing files [default: %(default)s]", default=False)
        parser.add_argument('-m', '--metadataonly', dest='metadataonly', action="store_true", help="Convert meta data only, do not convert files. Implies overwriteIfSrcNewer.", default=False)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]", default=False)
        parser.add_argument("-n", "--nice", dest="nice",  help="set nice level [default: system default]")
        parser.add_argument("-i", "--include", dest="include", help="only include paths matching this regex pattern. Note: exclude is given preference over include. [default: %(default)s]", metavar="RE" )
        parser.add_argument("-e", "--exclude", dest="exclude", help="exclude paths matching this regex pattern. [default: %(default)s]", metavar="RE" )
        parser.add_argument('-t', '--threads', dest='threads', help="number of threads to use [default: %(default)s]", default=1)
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest="src", help="paths to source file / source folder")
        parser.add_argument(dest="dst", help="paths to destination file / destination folder  [default: %(default)s]")

        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose
        recursive = args.recurse
        overwrite = args.overwrite
        metadataonly = args.metadataonly
        if metadataonly:
            overwriteIfSrcNewer = True
        else:
            overwriteIfSrcNewer = args.overwriteIfSrcNewer
        includePattern = args.include
        excludePattern = args.exclude
        threads = args.threads
        src = args.src
        dst = args.dst
        dict = vars(args)
        if 'nice' in dict:
            nice = args.nice
            p = psutil.Process(os.getpid())
            if platform.system()=='Windows':
                p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            else:
                p.nice(nice)

        logging.basicConfig(level=logging.INFO, format='%(asctime)-15s -- %(levelname)s -- %(message)s')
        logging.info("MusicLibraryConverter started...")
        if verbose > 0:
            logging.getLogger().setLevel(logging.DEBUG)
            logging.info("Verbose mode on")
            if recursive:
                logging.info("Recursive mode on")
            else:
                logging.info("Recursive mode off")

        if includePattern and excludePattern and includePattern == excludePattern:
            raise CLIError("include and exclude pattern are equal! Nothing will be processed.")

        global mediaLibraryConverterMaster
        mediaLibraryConverterMaster = MusicLibraryConverterMaster(verbose, recursive, int(threads), includePattern, excludePattern, overwrite, overwriteIfSrcNewer, metadataonly, src, dst)
        mediaLibraryConverterMaster.run()
#         time.sleep(20)
#        for inpath in paths:
            ### do something with inpath ###
            #print(inpath)
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    from os.path import dirname
    sys.path.append(dirname(dirname(__file__)))
    signal.signal(signal.SIGINT, signal_handler)
#     if DEBUG:
#         sys.argv.append("-h")
#         sys.argv.append("-v")
#         sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'medialibraryconverter_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
    
