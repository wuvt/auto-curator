from operator import itemgetter
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from tinytag import TinyTag
import os
import sys

#starts SQLite database
engine = create_engine("sqlite:///test.db")

class Base(DeclarativeBase):
    pass
#create ORM object for the track
class Track(Base):
    __tablename__ = "tracks"

    title: Mapped[str]
    album: Mapped[str]
    artist: Mapped[str]
    label: Mapped[str]
    mbTrackId: Mapped[str] = mapped_column(primary_key=True)
    path: Mapped[str]

    def __repr__(self):
        return f"{self.title}, {self.artist}, {self.album}, {self.label}, {self.mbTrackId}, {self.path}"

Base.metadata.create_all(engine)



# gets metadata from file
def getMetadata(filename):
    tag = TinyTag.get(filename)

    metadata: dict = tag.as_dict()
    return metadata
def loopDir(dirName):
    for e in os.scandir(dirName):
        if e.is_file() and TinyTag.is_supported(e.path):

            #get the metadata from the file
            data = getMetadata(e.path)
            
            # create a track object with the fileds from data
            t = Track(album = data.get('album')[0],
                      artist = data.get('artist')[0],
                      title = data.get('title')[0],
                      label = data.get('label')[0],
                      mbTrackId = data.get('musicbrainz_trackid')[0],
                      path = e.path)
            #creates a session and adds t to the database
            print(t)
            with Session(engine) as session:
                session.add(t)
                session.commit()
        elif e.is_dir():
            # if there is a folder, run loop dir again through that
            loopDir(e.path)





def main():
    loopDir(sys.argv[1])

if __name__ == "__main__":
    main()

    