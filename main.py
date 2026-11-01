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

def getTag(dict, tag, e):

    try:
        returnValue = dict.get(tag)[0]
    except TypeError:
        returnValue = ' '
        print(os.path.abspath(e))
        print('Is missing ' + tag + ' tag\n')

    return returnValue
    
        


Base.metadata.create_all(engine)



# gets metadata from file
def getMetadata(filename):
    f = taglib.File(filename)

    return f.tags
    
def loopDir(dirName, jout):
    

    


    for e in os.scandir(dirName):
        if e.is_file() and (e.path.endswith('.flac') or (e.path.endswith('.mp3'))) :
            # c:\Users\victo\Music\ncpjazz\ncp-jazz
            #get the metadata from the file
            data = getMetadata(e.path)
            
            # print(data)
            # print(e.path)
            # create a track object with the fields from data
            t = Track(album = getTag(data, 'ALBUM',e),
                      artist = getTag(data, 'ARTIST',e),
                      title = getTag(data, 'TITLE',e),
                      label = getTag(data, 'LABEL',e),
                      mbTrackId = getTag(data,'MUSICBRAINZ_TRACKID',e),
                      comment = getTag(data, 'COMMENT',e),
                    #   genre = getTag(data, 'GENRE'),
                      url = os.path.abspath(e))
            # #creates a session and adds t to the database
            jout.append(t.as_dict()) 
            with Session(engine) as session:
                q = session.query(Track.title).filter(Track.mbTrackId==t.title)
                
                if not session.query(q.exists()).scalar():
                    session.add(t)
                    session.commit()
        elif e.is_dir():
            # if there is a folder, run loop dir again through that
            loopDir(e.path, jout)

    




def pathUrl(file):
    return os.path.splitroot(file.path)

def main():

    jout = []

    try:
        loopDir(sys.argv[1], jout)

        file = open('out.json', 'w+')
        json.dump(jout, file)


    except IndexError:

        

        print('Enter Directory')

if __name__ == "__main__":
    main()

    
