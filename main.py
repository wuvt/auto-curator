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

    title: Mapped[str]
    album: Mapped[str]
    artist: Mapped[str]
    label: Mapped[str]
    mbTrackId: Mapped[str] = mapped_column(primary_key=True)
    url: Mapped[str]

# makes Track objects printable
    def __repr__(self):
        return f"{self.title}, {self.artist}, {self.album}, {self.label}, {self.mbTrackId}, {self.url}"

#turns Track object to a dictionary to export as json
    def as_dict(self):
            return {c.name: getattr(self, c.name) for c in self.__table__.columns}

 
    


Base.metadata.create_all(engine)



# gets metadata from file
def getMetadata(filename):
    f = taglib.File(filename)

    return f.tags
    
def loopDir(dirName):
    for e in os.scandir(dirName):
        if e.is_file() and e.path.endswith('.flac'):

            #get the metadata from the file
            data = getMetadata(e.path)
            
            # print(data)
            # create a track object with the fields from data
            t = Track(album = data.get('ALBUM')[0],
                      artist = data.get('ARTIST')[0],
                      title = data.get('TITLE')[0],
                      label = data.get('LABEL')[0],
                      mbTrackId = data.get('MUSICBRAINZ_TRACKID')[0],
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
    loopDir(sys.argv[1])

if __name__ == "__main__":
    main()

    
