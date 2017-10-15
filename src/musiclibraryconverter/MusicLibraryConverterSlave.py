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
Created on Mar 2, 2014

@author: Eike Thaden
'''

import os
import time
import threading
import subprocess
from random import randint
from pathlib import Path
from musiclibraryconverter.MusicLibraryConverterBackend import MusicLibraryConverterBackend
from musiclibraryconverter.MusicLibraryTagConverter import MusicLibraryTagConverter, createMusicLibraryTagConverter

class MusicLibraryConverterSlave(object):
    '''
    classdocs
    '''
    ':type __srcFile: Path'
    ':type __dstFile: Path'
    ':type __event: Event'

    def __init__(self, converter, evInterrupted, verbose, metadataonly, srcFile, dstFile):
        '''
        Constructor
        '''
        ':type srcFile: Path'
        ':type dstFile: Path'
        ':type event: Event'

        self.__evInterrupted = evInterrupted
        self.__verbose = verbose
        self.__metadataonly = metadataonly
        assert isinstance(srcFile, Path)
        self.__srcFile = srcFile
        assert isinstance(dstFile, Path)
        self.__dstFile = dstFile
        self.__converter = converter
    
    def run(self):
        if not self.__metadataonly:
            if not self.convertFile():
                return
        if (not self.__dstFile.exists()):
            return
        try:
            self.convertTags()
        except Exception as e:
            print ('An exception of type'+str(type(e))+' occured: '+str(e))
        # For testing:
#         print ('Only for testing: Delete output file')
#         self.__dstFile.unlink()
        
    def convertFile(self):
        if (self.__converter == None):
            return
        args = self.__converter.createCommandline(self.__verbose, self.__srcFile, self.__dstFile)     
        if args == None:
            return
        if self.__verbose:
            print (*args, sep=' ', end='')
            print ('\n')
        #return
        process = subprocess.Popen(args)
        
        while process.poll() is None and not self.__evInterrupted.is_set():
            time.sleep(0.1)

        if self.__evInterrupted.is_set() and process.poll() == None:
            process.terminate()
            process.wait(timeout=5)
            if process.poll() == None:
                process.kill()
            self.__dstFile.unlink()
            return False
        elif process.poll() != 0:
            self.__dstFile.unlink()
            return False
        
#        print ('Finished converting file '+str(self.__srcFile)+' (status: '+str(process.poll())+')')
        return True
    
    def convertTags(self):
        src_tag = createMusicLibraryTagConverter(self.__srcFile)
#         print ('\nMetadata (source file):')
#         print (src_tag.pprint())
        dst_tag = createMusicLibraryTagConverter(self.__dstFile)
        dst_tag.delete_all()
        dst_tag.set_from_other(src_tag)
#         print ('\nAfter updating from source tags:')
#         print (dst_tag.pprint())
        dst_tag.save()

    def runOld(self):
        self.__event.wait(randint(2,6))
        if (self.__event.is_set()):
            pass

    def interrupt(self):
        print ("Trying to interrupt worker "+str(self.__id))

