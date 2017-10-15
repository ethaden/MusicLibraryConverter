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
#
# frame.text = unicode(frame).encode("iso-8859-1").decode("koi8-r")

'''
Created on 03.04.2014

@author: Eike Thaden
'''

import logging

from pathlib import Path
from mutagenx.id3 import ID3, TIT2, TALB, TPE1, TPE2, TCOM, TCON, COMM, TRCK, TPOS, TDRC, TextFrame
from mutagenx.flac import FLAC
from mutagenx.easyid3 import EasyID3
from builtins import type
import codecs

# factory
def createMusicLibraryTagConverter(file):
    ':type file: Path'
    assert isinstance(file, Path)
    suffix = file.suffix
    if suffix=='.mp3':
        return MusicLibraryTagConverterID3(file)
    elif suffix=='.flac':
        return MusicLibraryTagConverterFlac(file)
    return None

class MusicLibraryTagConverter(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def getEncoding(self):
        return "UTF-8"
        
    @property
    def title(self):
        return None
    @title.setter
    def title(self, title):
        pass

    @property
    def artist(self):
        return None
    @artist.setter
    def artist(self, artist):
        pass
    
    @property
    def album(self):
        return None
    @album.setter
    def album(self, album):
        pass
    
    @property
    def album_artist(self):
        return None
    @album_artist.setter
    def album_artist(self, album_artist):
        pass
    
    @property
    def composer(self):
        return None
    @composer.setter
    def composer(self, composer):
        pass
    
    @property
    def performer(self):
        return None
    @performer.setter
    def performer(self, performer):
        pass
    
    @property
    def genre(self):
        return None
    @genre.setter
    def genre(self, genre):
        pass
    
    @property
    def comment(self):
        return None
    @comment.setter
    def comment(self, comment):
        pass
    
    @property
    def date(self):
        return None
    @date.setter
    def date(self, date):
        pass
    
    @property
    def tracknumber(self):
        return None
    @tracknumber.setter
    def tracknumber(self, tracknumber):
        pass
    
    @property
    def totaltracks(self):
        return None
    @totaltracks.setter
    def totaltracks(self, totaltracks):
        pass
    
    @property
    def discnumber(self):
        return None
    @discnumber.setter
    def discnumber(self, discnumber):
        pass
    
    @property
    def totaldiscs(self):
        return None
    @totaldiscs.setter
    def totaldiscs(self, totaldiscs):
        pass
    
    def delete_all(self):
        pass
    
    def pprint(self):
        return ''
    
    def save(self):
        pass

    def set_from_other(self, other):
        if not isinstance(other, MusicLibraryTagConverter):
            raise Exception('Error while copying meta tags: Source object is not of type MusicLibraryTagConverter')
        self.title = other.title
#        self.title = other.title.encode(self.getEncoding())
        self.artist = other.artist
        self.album = other.album
        self.composer = other.composer
        self.performer = other.performer
        self.genre = other.genre
        self.comment = other.comment
        self.date = other.date
        self.tracknumber = other.tracknumber
        self.totaltracks = other.totaltracks
        self.discnumber = other.discnumber
        self.totaldiscs = other.totaldiscs

class MusicLibraryTagConverterID3(MusicLibraryTagConverter):
    '''
    classdocs
    '''

    def __init__(self, file):
        '''
        Constructor
        '''
        MusicLibraryTagConverter.__init__(self)
        self.__file = file
        self.__id3 = ID3(file.as_posix())
        self.__v2_version=3
    
    def delete_all(self):
        self.__id3.delete()

    def pprint(self):
        return self.__id3.pprint()

    def save(self):
        # Save id3 v2.3 format for retaining compatibility to Windows Media Player
        self.__id3.update_to_v23()
        self.__id3.save(v2_version=3)

    def getEncoding(self):
        return "UTF-16-LE"
    
    @property
    def v2_version(self):
        return self.__v2_version
    
    @v2_version.setter
    def v2_version(self, version):
        if not (version==3 or version==4):
            logging.warning('Only id3 v2.3 or v2.4 tags are supported')
        else:
            self.__v2_version = version

    @property
    def title(self):
        tags = self.__id3.getall('TIT2')
        if tags==[]:
            return None
        return tags[0]  
    @title.setter
    def title(self, title):
        if title == None:
            self.__id3.delall('TIT2')
        else:
            self.__id3.add(TIT2(encoding=1 if self.__v2_version==3 else 3, text=title))

    @property
    def album(self):
        tags = self.__id3.getall('TALB')
        if tags==[]:
            return None
        return tags[0]  
    @album.setter
    def album(self, album):
        if album == None:
            self.__id3.delall('TALB')
        else:
            self.__id3.add(TALB(encoding=1 if self.__v2_version==3 else 3, text=album))    

    @property
    def artist(self):
        tags = self.__id3.getall('TPE1')
        if tags==[]:
            return None
        return tags[0]  
    @artist.setter
    def artist(self, artist):
        if artist == None:
            self.__id3.delall('TPE1')
        else:
            self.__id3.add(TPE1(encoding=1 if self.__v2_version==3 else 3, text=artist))    

    @property
    def album_artist(self):
        tags = self.__id3.getall('TPE2')
        if tags==[]:
            return None
        return tags[0]  
    @album_artist.setter
    def album_artist(self, album_artist):
        if album_artist == None:
            self.__id3.delall('TPE2')
        else:
            self.__id3.add(TPE2(encoding=1 if self.__v2_version==3 else 3, text=album_artist))    

    @property
    def composer(self):
        tags = self.__id3.getall('TCOM')
        if tags==[]:
            return None
        return tags[0]  
    @composer.setter
    def composer(self, composer):
        if composer == None:
            self.__id3.delall('TCOM')
        else:
            self.__id3.add(TCOM(encoding=1 if self.__v2_version==3 else 3, text=composer))    

    @property
    def performer(self):
        tags = self.__id3.getall('TPE2')
        if tags==[]:
            return None
        return tags[0]  
    @performer.setter
    def performer(self, performer):
        if performer == None:
            self.__id3.delall('TPE2')
        else:
            self.__id3.add(TPE2(encoding=1 if self.__v2_version==3 else 3, text=performer))    
    
    @property
    def genre(self):
        tags = self.__id3.getall('TCON')
        if tags==[]:
            return None
        return tags[0]  
    @genre.setter
    def genre(self, genre):
        if genre == None:
            self.__id3.delall('TCON')
        else:
            self.__id3.add(TCON(encoding=1 if self.__v2_version==3 else 3, text=genre))    
    
    @property
    def comment(self):
        tags = self.__id3.getall('COMM')
        if tags==[]:
            return None
        return tags[0]  
    @comment.setter
    def comment(self, comment):
        if comment == None:
            self.__id3.delall('COMM')
        else:
            self.__id3.add(COMM(encoding=1 if self.__v2_version==3 else 3, text=comment))    

    @property
    def date(self):
        tags = self.__id3.getall('TDRC')
        if tags==[]:
            return None
        return tags[0]  
    @date.setter
    def date(self, date):
        if date == None:
            self.__id3.delall('TDRC')
        else:
            self.__id3.add(TDRC(encoding=1 if self.__v2_version==3 else 3, text=date))    

    @property
    def tracknumber(self):
        tags = self.__id3.getall('TRCK')
        if tags==[]:
            return None
        splitted = str(tags[0]).split(sep='/', maxsplit=1)
        if len(splitted) >=1:
            track = splitted[0]
        else:
            return None
        if (track==''):
            return None
        return track  
    @tracknumber.setter
    def tracknumber(self, tracknumber):
        current_totaltracks = self.totaltracks
        if tracknumber == None:
            self.__id3.delall('TRCK')
        else:
            if (current_totaltracks==None):
                self.__id3.add(TRCK(encoding=1 if self.__v2_version==3 else 3, text=tracknumber))
            else:
                self.__id3.add(TRCK(encoding=1 if self.__v2_version==3 else 3, text=str(tracknumber)+'/'+str(current_totaltracks)))
    
    @property
    def totaltracks(self):
        tags = self.__id3.getall('TRCK')
        if tags==[]:
            return None
        splitted = str(tags[0]).split(sep='/', maxsplit=1)
        if len(splitted) <=1:
            return None
        totaltracks = splitted[1]
        if (totaltracks==None or totaltracks==''):
            return None
        return totaltracks  
    @totaltracks.setter
    def totaltracks(self, totaltracks):
        current_track = self.tracknumber
        if current_track==None and totaltracks == None:
            self.__id3.delall('TRCK')
        else:
            if (totaltracks==None):
                self.__id3.add(TRCK(encoding=1 if self.__v2_version==3 else 3, text=current_track))
            else:
                self.__id3.add(TRCK(encoding=1 if self.__v2_version==3 else 3, text=str(current_track)+'/'+str(totaltracks)))
    
    @property
    def discnumber(self):
        tags = self.__id3.getall('TPOS')
        if tags==[]:
            return None
        splitted = str(tags[0]).split(sep='/', maxsplit=1)
        if len(splitted)==0:
            return None
        return splitted[0]
    @discnumber.setter
    def discnumber(self, discnumber):
        current_totaldiscs = self.totaldiscs
        if discnumber == None:
            self.__id3.delall('TPOS')
        else:
            if current_totaldiscs == None:
                self.__id3.add(TPOS(encoding=1 if self.__v2_version==3 else 3, text=str(discnumber)))
            else:
                self.__id3.add(TPOS(encoding=1 if self.__v2_version==3 else 3, text=str(discnumber))+'/'+str(current_totaldiscs))

    @property
    def totaldiscs(self):
        tags = self.__id3.getall('TPOS')
        if tags==[]:
            return None
        splitted = str(tags).split(sep='/', maxsplit=1)
        if len(splitted)<=1:
            return None
        return splitted[1] 
    @totaldiscs.setter
    def totaldiscs(self, totaldiscs):
        current_disc = self.discnumber
        if current_disc==None and totaldiscs == None:
            self.__id3.delall('TPOS')
        else:
            if (totaldiscs==None):
                self.__id3.add(TPOS(encoding=1 if self.__v2_version==3 else 3, text=str(current_disc)))
            else:
                self.__id3.add(TPOS(encoding=1 if self.__v2_version==3 else 3, text=str(current_disc)+'/'+str(totaldiscs)))
  

class MusicLibraryTagConverterFlac(MusicLibraryTagConverter):
    def __init__(self, file):
        '''
        Constructor
        '''
        ':type file: Path'
        MusicLibraryTagConverter.__init__(self)
        self.__file = file
        self.__flac = FLAC(file.as_posix())

    def save(self):
        self.__flac.save()

    def pprint(self):
        return self.__flac.pprint()

    def getEncoding(self):
        return "UTF-8"

    @property
    def title(self):
        tags = []
        if 'title' in self.__flac:
            tags = self.__flac['title']
        if tags == []:
            return None
        return tags[0]

    @title.setter
    def title(self, title):
        pass

    @property
    def album(self):
        tags = []
        if 'album' in self.__flac:
            tags = self.__flac['album']
        if tags == []:
            return None
        return tags[0]
    @album.setter
    def album(self, album):
        self.__flac['album'] = [album]

    @property
    def artist(self):
        tags = []
        if 'artist' in self.__flac:
            tags = self.__flac['artist']
        if tags == []:
            return None
        return tags[0]
    @artist.setter
    def artist(self, artist):
        self.__flac['artist'] = [artist]
    
    @property
    def album_artist(self):
        tags = []
        if 'albumartist' in self.__flac:
            tags = self.__flac['albumartist']
        if tags == []:
            return None
        return tags[0]
    @album_artist.setter
    def album_artist(self, album_artist):
        self.__flac['albumartist'] = [album_artist]
    
    @property
    def composer(self):
        tags = []
        if 'composer' in self.__flac:
            tags = self.__flac['composer']
        if tags == []:
            return None
        return tags[0]
    @composer.setter
    def composer(self, composer):
        self.__flac['composer'] = [composer]
    
    @property
    def performer(self):
        tags = []
        if 'performer' in self.__flac:
            tags = self.__flac['performer']
        if tags == []:
            return None
        return tags[0]
    @performer.setter
    def performer(self, performer):
        self.__flac['performer'] = [performer]
    
    @property
    def genre(self):
        tags = []
        if 'genre' in self.__flac:
            tags = self.__flac['genre']
        if tags == []:
            return None
        return tags[0]
    @genre.setter
    def genre(self, genre):
        self.__flac['genre'] = [genre]
    
    @property
    def comment(self):
        tags = []
        if 'description' in self.__flac:
            tags = self.__flac['description']
        if tags == []:
            return None
        return tags[0]
    @comment.setter
    def comment(self, comment):
        self.__flac['description'] = [comment]
    
    @property
    def date(self):
        tags = []
        if 'date' in self.__flac:
            tags = self.__flac['date']
        if tags == []:
            return None
        return tags[0]
    @date.setter
    def date(self, date):
        self.__flac['date'] = [date]

    @property
    def tracknumber(self):
        tags = []
        if 'tracknumber' in self.__flac:
            tags = self.__flac['tracknumber']
        if tags == []:
            return None
        return tags[0]
    @tracknumber.setter
    def tracknumber(self, tracknumber):
        self.__flac['tracknumber'] = [tracknumber]
    
    @property
    def totaltracks(self):
        tags = []
        if 'tracktotal' in self.__flac:
            tags = self.__flac['tracktotal']
        if tags == []:
            return None
        return tags[0]
    @totaltracks.setter
    def totaltracks(self, totaltracks):
        self.__flac['tracktotal'] = [totaltracks]
    
    @property
    def discnumber(self):
        tags = []
        if 'discnumber' in self.__flac:
            tags = self.__flac['discnumber']
        if tags == []:
            return None
        return tags[0]
    @discnumber.setter
    def discnumber(self, discnumber):
        self.__flac['discnumber'] = [discnumber]
    
    @property
    def totaldiscs(self):
        tags = []
        if 'disctotal' in self.__flac:
            tags = self.__flac['disctotal']
        if tags == []:
            return None
        return tags[0]
    @totaldiscs.setter
    def totaldiscs(self, totaldiscs):
        self.__flac['disctotal'] = [totaldiscs]
    
