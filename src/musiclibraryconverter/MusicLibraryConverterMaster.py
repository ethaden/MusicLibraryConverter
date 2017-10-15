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
Created on Mar 1, 2014

@author: Eike Thaden
'''

from concurrent.futures import *
import logging
from multiprocessing import Event
from multiprocessing import RLock
import os
from pathlib import Path
import platform
from random import randint
import sys
import threading
import time
import shutil

from musiclibraryconverter.MusicLibraryConverterBackend import MusicLibraryConverterBackend, MusicLibraryConverterBackendFactory
from musiclibraryconverter.MusicLibraryConverterSlave import MusicLibraryConverterSlave


supportedFileEndings = ['flac']

def createWorker (verbose, metadataonly, converter, event, srcFile, dstFile):
    worker = MusicLibraryConverterSlave(converter, event, verbose, metadataonly, srcFile, dstFile)
    worker.run()

class ConverterBackendNotFoundException(Exception):
    def __init__(self, backend):
        Exception.__init__(self, 'Converter backend '+backend+' not found')
    


class MusicLibraryConverterMaster(object):
    '''
    classdocs
    '''
    __instance = None

    def __init__(self, verbose, recursive, threads, includePattern, excludePattern, overwrite, overwriteIfSrcNewer, metadataonly, src, dst, converterType='FFMpeg', srcParams='', dstParams='', srcExt='flac', dstExt='mp3'):
        '''
        Constructor
        '''
        ':type recursive: boolean'
        ':type includePattern: String'
        ':type excludePattern: String'
        ':type threads: int'
        ':type src: String'
        ':type src: String'
        ':type dstExt: String'
        ':type dstExt: String'
        ':type overwrite: String'
        ':type overwriteIfSrcNewer: String'
        self.__verbose = verbose
        self.__recursive = recursive
        self.__includePattern = includePattern
        self.__excludePattern = excludePattern
        self.__threads = threads
#         print ("src="+src)
#         print ("dst="+dst)
        self.__src = Path(src)
        self.__dst = Path(dst)
        self.__srcExt = srcExt
        self.__dstExt = dstExt
        self.__coverExtList = ['jpg', 'jpeg', 'bmp', 'png']
        #self.__executer = ProcessPoolExecutor(max_workers=threads)
        self.__executer = ThreadPoolExecutor(max_workers=threads)
        self.__futures = []
        self.__futureEvents = {}
        self.__instance = self
        self.__mutex = RLock()
        self.__evInterrupted = Event()
        self.__overwrite = overwrite
        self.__overwriteIfSrcNewer = overwriteIfSrcNewer
        self.__metadataonly = metadataonly
        self.__converter = MusicLibraryConverterBackendFactory(converterType, srcParams, dstParams)
        if self.__converter == None or not self.__converter.backendFound():
            raise ConverterBackendNotFoundException(converterType)
        
    def handleFiles(self, srcFile, dst):
        ':type src: Path'
        ':type dst: Path'
        if not srcFile.exists():
            raise FileNotFoundError(srcFile)
        dstFile = self.deriveDstFile(srcFile, dst)
        ': :type dstFile: Path'
        skipFile = False
        if dstFile.exists():
            if dstFile.is_symlink() or not os.access(dstFile.as_posix(), os.W_OK):
                skipFile = True # Skip all symlinks and destination files which are not writable
            elif self.__overwrite:
                skipFile = False # Overwrite file as requested!
            elif self.__overwriteIfSrcNewer:
                # Check whether or not the last modification of the source file has been later than the last modification of the destination file
                # Update if newer
                if srcFile.stat().st_mtime < dstFile.lstat().st_mtime:
                    skipFile = True
                else:
                    skipFile = False
            else:
                skipFile = True # In all other cases: it's better to skip this file
        elif self.__metadataonly:
            skipFile = True
        # Do the work!
        if not skipFile:
            try:
                srcFileStr = (str(srcFile)).encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
                dstFileStr = (str(dstFile)).encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
                #print ('"'+srcFileStr+'"\n -> "'+dstFileStr+'"')
            except Exception as e:
                logging.error('An exception occured: '+str(e))
            self.__mutex.acquire()
            future = self.__executer.submit(createWorker, self.__verbose, self.__metadataonly, self.__converter, self.__evInterrupted, srcFile, dstFile)
            self.__futures.append(future)
            future.add_done_callback(self.finished)
            self.__mutex.release()
            
    def copyFile(self, srcFile, dstDir):
        ':type file: Path'
        ':type dst: Path'
        dstFile = dstDir.joinpath(srcFile.parts[-1])
        skipFile = False
        if dstFile.exists():
            if dstFile.is_symlink() or not os.access(dstFile.as_posix(), os.W_OK):
                skipFile = True # Skip all symlinks and destination files which are not writable
            elif self.__overwrite:
                skipFile = False # Overwrite file as requested!
            elif self.__overwriteIfSrcNewer:
                # Check whether or not the last modification of the source file has been later than the last modification of the destination file
                # Update if newer
                if srcFile.stat().st_mtime < dstFile.lstat().st_mtime:
                    skipFile = True
                else:
                    skipFile = False
            else:
                skipFile = True # In all other cases: it's better to skip this file
        elif self.__metadataonly:
            skipFile = True
        # Do the work!
        if not skipFile:
            try:
                srcFileStr = (str(srcFile)).encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
                dstFileStr = (str(dstFile)).encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
                shutil.copyfile(srcFileStr, dstFileStr)
            except Exception as e:
                logging.error('An exception occured: '+str(e))
    
    def handlePathRecursively(self, src, dst):
        ':type src: Path'
        ':type dst: Path'
        if not src.exists():
            raise FileNotFoundError(src)
        if src.is_file():
            self.handleFiles(src, self.deriveDstFile(src, dst))
        elif src.is_dir():
            #for file in src.glob('*.'+self.__srcExt):
            for p in src.iterdir():
                ':type p: Path'
                if (self.__evInterrupted.is_set()):
                    break
                if p.is_file():
                    if p.name.endswith('.'+self.__srcExt):
                        self.handleFiles(p, dst)
                    else:
                        for cover_ext in self.__coverExtList:
                            if p.name.endswith('.'+cover_ext):
                                self.copyFile(p, dst)
                                break;
                elif self.__recursive and p.is_dir():
                    dstSubDir = dst.joinpath(p.parts[-1])
                    ': :type dstSubDir: Path'
                    if not dstSubDir.exists():
                        dstSubDir.mkdir()
                    self.handlePathRecursively(p, dstSubDir)

    def deriveDstFile(self, src, dst):
        ':type src: Path'
        ':type dst: Path'
        if dst.is_file():
            return dst
        if dst.is_dir():
            filename = src.name
            ': :type filename: str'
            if filename.endswith('.'+self.__srcExt):
                #filename.replace(self.__srcExt, self.__dstExt, -1)
                i = filename.rfind('.'+self.__srcExt)
                if i==-1:
                    filename = filename+self.__dstExt
                else:
                    filename = filename[0:i]+"."+self.__dstExt
            return dst.joinpath(filename)
        raise Exception("Error: Destination file '"+str(dst)+"' is neither a file nor an (existing) directory")

    def run(self):
        try:
            if self.__src.exists() and not self.__dst.exists():
                self.__dst.mkdir(parents=True)
            logging.info("Analyzing specified files/directories...")
            self.handlePathRecursively(self.__src, self.__dst)
            finished=False
            while not finished:
                finished=True
                self.__mutex.acquire()
                for f in self.__futures:
                    if not (f.done() or f.cancelled()):
                        finished=False
                self.__mutex.release()
                try:
                    time.sleep(0.1)
                except InterruptedError:
                    pass
            logging.info("Conversion finished")
        except FileNotFoundError as e:
            logging.error('Source file or directory not found: "'+str(e)+'"')
        
    def runTest(self):
        try:
#             self.__mutex.acquire()
            for i in range(6):
                ev = Event()
                self.__mutex.acquire()
                future = self.__executer.submit(createWorker, i, ev)
                self.__futures.append(future)
                self.__futureEvents[future] = ev
                future.add_done_callback(self.finished)
                self.__mutex.release()
                try:
                    time.sleep(2)
                except InterruptedError:
                    pass
                if (self.__evInterrupted.is_set()):
                    break
            #wait(self.__futures, timeout=None, return_when=ALL_COMPLETED)
            finished=0
            while not finished:
                finished=1
#                 print ("waiting: Acquire lock")
                self.__mutex.acquire()
                for f in self.__futures:
                    if not (f.done() or f.cancelled()):
                        finished=0
#                 print ("waiting: Release lock")
                self.__mutex.release()
#            while not(all((f.done() or f.cancelled()) for f in self.__futures)):
#                pass
            logging.info("All tasks are finished")
        except KeyboardInterrupt:
            pass
        
    def interrupt(self):
        logging.info("Sending CTRL-C event to all threads")
        self.__executer.shutdown(wait=False)
        self.__evInterrupted.set()

    def finished(self, future):
        self.__mutex.acquire()
        self.__futures.remove(future)
        self.__mutex.release()
        try:
            future.result()
        except Exception as e:
            logging.error("Worker exited with exception: "+str(e))

