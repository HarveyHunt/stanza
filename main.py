from stanza import interface, config, metadata, player
import time
from threading import Thread


class Stanza():

    def __init__(self):
        self.config = config.Config()
        self.ui = interface.stanza_ui(self.config.interface)
        self.player = player.find_player(self.config.general)
        self.status = {'artist': None, 'album': None, 'title': None,
                       'vol_left': None, 'vol_right': None, 'playing': False,
                       'duration': 0, 'position': 0, 'repeat': False,
                       'shuffle': False}
        self.lyrics = ''
        if not self.player:
            print('No supported players are running')
            exit()
        self.md = metadata.Metadata(self.config.general)

    def run(self):
        player_thread = Thread(target=self.monitor_player)
        player_thread.daemon = True
        player_thread.start()
        self.ui.run()

    def monitor_player(self):
        while True:
            if not self.player.is_running():
                exit()
            self.player.update_status()
            if self.status != self.player.status:
                self.ui.footer.set_data(self.player.status)
                self.ui.header.set_data(self.player.status)
                if self.status['artist'] != self.player.status['artist'] or \
                        self.status['album'] != self.player.status['album'] or \
                        self.status['title'] != self.player.status['title']:
                            self.status[
                                'artist'] = self.player.status['artist']
                            self.status['album'] = self.player.status['album']
                            self.status['title'] = self.player.status['title']
                            Thread(target=self.md.get, args=('lyrics',
                                                             self.status['artist'],
                                                             self.status['album'],
                                                             self.status['title'])).start()
                self.status = self.player.status
            if self.lyrics != self.md.lyrics:
                self.lyrics = self.md.lyrics
                self.ui.set_listbox_data(self.lyrics)
            if self.ui.is_dirty:
                self.ui.loop.draw_screen()
            time.sleep(0.5)

if __name__ == '__main__':
    s = Stanza()
    s.run()
