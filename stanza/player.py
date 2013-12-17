import os.path
import imp
import glob


def find_player(conf):
    player_folder = os.path.join(os.getcwd(), 'players')
    conf = {}
    if 'default_player' in conf:
        player = _load_player(conf['default_player'], player_folder)
        return player if player.is_running() else None
    else:
        for player_file in glob.glob(player_folder + '/[!_]*.py'):
            player_name = player_file.split('/')[-1]
            player_name = player_name.split('.py')[0]
            player = _load_player(player_name, player_folder)
            if player.is_running():
                return player
        else:
            return None


def _load_player(player_name, player_folder):
    player_path = os.path.join(player_folder, player_name + '.py')
    player_module = imp.load_source(player_name, player_path)
    return player_module.Player()
