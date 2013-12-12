import plyr
from stanza import __version__

class MetaData():

    def __init__(self, config):
        self.db = plyr.Database(config['db_path'])
        self.useragent = 'stanza ' + __version__
        self.lyrics = ''

    def _query(self, get_type, artist, album, title):
        qry = plyr.Query(get_type=get_type, artist=artist, album=album,
                            title=title)
        qry.useragent = self.useragent
        qry.database = self.db
        qry.force_utf8 = True
        qry.normalize = ('none', 'artist', 'album', 'title')
        return qry.commit()

    def get(self, get_type, artist, album, title):
        items = self._query(get_type, artist, album, title)
        if items:
            self.lyrics = items[0].data
