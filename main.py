from operator import itemgetter

from tinytag import TinyTag
import os
import sys


def getMetadata(filename):
    tag = TinyTag.get(filename)

    metadata: dict = tag.as_dict()
    return metadata
def loopDir(dirName):
    for e in os.scandir(dirName):
        if e.is_file() and TinyTag.is_supported(e.path):

            #get the metadata from the file
            data = getMetadata(e.path)

            # gets the fields from the dictionay provide by get metadata and makes it into a list
            g = list(itemgetter('artist', 'album', 'title', 'label', 'musicbrainz_trackid')(data))
            # Adds the file path to the output list
            g.append(e.path)
            #temporary, will send to sql database instead
            print(g)
        elif e.is_dir():
            loopDir(e.path)





def main():
    loopDir(sys.argv[1])

if __name__ == "__main__":
    main()

    