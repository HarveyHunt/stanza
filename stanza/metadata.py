import time
import plyr
from stanza import __version__


class Metadata():

    def __init__(self, config):
        self.db = plyr.Database(config['db_path'])
        self.timeout = config['query_timeout']
        self.useragent = 'stanza ' + __version__
        self.last_query = 0
        self.lyrics = ''

    def _query(self, get_type, artist, album, title):
        qry = plyr.Query(get_type=get_type, artist=artist, album=album,
                         title=title)
        qry.useragent = self.useragent
        qry.database = self.db
        qry.timeout = self.timeout
        qry.force_utf8 = True
        qry.normalize = ('aggressive', 'artist', 'album', 'title')
        return qry.commit()

    def get(self, get_type, artist, album, title):
        self.lyrics = 'Searching...'
        self.last_query = time.time()
        last_query_time = self.last_query
        items = self._query('lyrics', artist, album, title)
        if items and last_query_time >= self.last_query:
            self.lyrics = items[0].data.decode('utf-8')
        elif not items and last_query_time == self.last_query:
            self.lyrics = 'No lyrics found.'
