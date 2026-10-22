#! /usr/bin/env python3
import json
from operator import itemgetter
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import taglib
import os
import sys

# starts SQLite database
engine = create_engine("sqlite:///test.db")

class Base(DeclarativeBase):
    pass
# create ORM object for the track
class Track(Base):
    __tablename__ = "tracks"

    title: Mapped[str] = mapped_column(primary_key=True)
    album: Mapped[str]
    artist: Mapped[str]
    label: Mapped[str]
    mbTrackId: Mapped[str] 
    url: Mapped[str]
    comment: Mapped[str]
    # genre: Mapped[str]

# makes Track objects printable
    def __repr__(self):
        return f"{self.title}, {self.artist}, {self.album}, {self.label}, {self.mbTrackId}, {self.url}"

#turns Track object to a dictionary to export as json
    def as_dict(self):
            return {c.name: getattr(self, c.name) for c in self.__table__.columns}

def getTag(dict, tag):

    try:
        returnValue = dict.get(tag)[0]
    except TypeError:
        returnValue = 'Tag does not exist, Please update metadata'

    return returnValue
    
        


Base.metadata.create_all(engine)



# gets metadata from file
def getMetadata(filename):
    f = taglib.File(filename)

    return f.tags
    
def loopDir(dirName):
    for e in os.scandir(dirName):
        if e.is_file() and (e.path.endswith('.flac') or (e.path.endswith('.mp3'))) :
            # c:\Users\victo\Music\ncpjazz\ncp-jazz
            #get the metadata from the file
            data = getMetadata(e.path)
            
            # print(data)
            # print(e.path)
            # create a track object with the fields from data
            t = Track(album = getTag(data, 'ALBUM'),
                      artist = getTag(data, 'ARTIST'),
                      title = getTag(data, 'TITLE'),
                      label = getTag(data, 'LABEL'),
                      mbTrackId = getTag(data,'MUSICBRAINZ_TRACKID'),
                      comment = getTag(data, 'COMMENT'),
                    #   genre = getTag(data, 'GENRE'),
                      url = os.path.abspath(e))
            # #creates a session and adds t to the database
            print(json.dumps(t.as_dict()))
            with Session(engine) as session:
                q = session.query(Track.mbTrackId).filter(Track.mbTrackId==t.mbTrackId)
                
                if not session.query(q.exists()).scalar():
                    session.add(t)
                    session.commit()
        elif e.is_dir():
            # if there is a folder, run loop dir again through that
            loopDir(e.path)



def pathUrl(file):
    return os.path.splitroot(file.path)

def main():
    try:
        loopDir(sys.argv[1])
    except IndexError:
        print('Enter Directory')

if __name__ == "__main__":
    main()

    
