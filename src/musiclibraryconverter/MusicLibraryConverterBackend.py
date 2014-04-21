# encoding: utf-8
#
# (c) 2014 Eike Thaden, http://www.eike-thaden.de/
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
Created on 30.03.2014

@author: Eike Thaden
'''

import platform
import os
from pathlib import Path

class MusicLibraryConverterBackend(object):
    '''
    classdocs
    '''


    def __init__(self, srcParams, dstParams, srcCodec='', dstCodec=''):
        '''
        Constructor
        '''
        self.__srcParams = srcParams
        self.__dstParams = dstParams
        self.__isBackendFound = False
        self.locateConverter()
        self.__srcCodec = srcCodec
        self.__dstCodec = dstCodec
        
    def setBackendFound(self, backendFound):
        self.__isBackendFound = backendFound

    def backendFound(self):
        return self.__isBackendFound

    def getConverterName(self):
        return None
    
    def getCommand(self):
        return self.__command
    
    def getSrcParams(self):
        return self.__srcParams

    def getDstParams(self):
        return self.__dstParams
    
    def getSrcCodec(self):
        return self.__srcCodec
    
    def getDstCodec(self):
        return self.__dstCodec
    
    def locateConverter(self):
        converterName = self.getConverterName()
        pathlist = os.getenv('PATH').split(os.pathsep)
        for pathStr in pathlist:
            ': :type path: str'
            path = Path(pathStr)
            ': :type tmp: Path'
            tmp = Path(path.joinpath(converterName))
            ': :type tmp: Path'
            if tmp.exists() and tmp.is_file():
                self.__command = tmp
                self.__isBackendFound = True
                return
        self.__command = None
    def createCommandline(self, verbose, srcFile, dstFile):
        return None

class MusicLibraryConverterExternalFFMpeg(MusicLibraryConverterBackend):
    '''
    classdocs
    '''


    def __init__(self, srcParams, dstParams, srcCodec='', dstCodec=''):
        '''
        Constructor
        '''
        MusicLibraryConverterBackend.__init__(self, srcParams, dstParams, srcCodec, dstCodec)

    def createCommandline(self, verbose, srcFile, dstFile):
        result = [os.path.normpath(self.getCommand().as_posix())]
        result.append('-loglevel')
        if (verbose):
            result.append('verbose')
        else:
            result.append('quiet')
        srcParams = self.getSrcParams()
        srcCodec = self.getSrcCodec()
        # source file options
        if srcCodec!='':
            pass
        # source file name
        result.extend(['-i', os.path.normpath(srcFile.as_posix())])
        if srcParams != None and srcParams != '':
            if  isinstance(srcParams, (list, tuple)):
                result.extend(srcParams)
            else:
                result.append(srcParams)
#        result.extend(['-i', r'\"'+os.path.normpath(srcFile.as_posix())+r'\"', r'\"'+os.path.normpath(dstFile.as_posix())+r'\"']) # Falsch!
        # destination file options
        result.append('-y') # Overwrite existing files
        dstCodec = self.getDstCodec()
        if dstCodec!='':
            result.extend(['-format', dstCodec])
        dstParams = self.getDstParams()
        if dstParams != None and dstParams != '':
            if  isinstance(dstParams, (list, tuple)):
                result.extend(dstParams)
            else:
                result.append(dstParams)
        else:
            result.extend(['-aq', '2']) # variable bitrate
        # destination file name
        result.append(os.path.normpath(dstFile.as_posix()))
        return result

    def getConverterName(self):
        if platform.system() == 'Windows':
            return 'ffmpeg.exe'
        else:
            return 'avconv' # ffmpeg is deprecated and will be replaced by avconv
        
def MusicLibraryConverterBackendFactory(converterType, srcParams, dstParams, srcCodec='', dstCodec=''):
    if (converterType == 'FFMpeg'):
        return MusicLibraryConverterExternalFFMpeg(srcParams, dstParams, srcCodec, dstCodec)

