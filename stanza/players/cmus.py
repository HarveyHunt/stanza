import subprocess
import datetime


class Player:
    '''
    Handles all of the actions relating to the cmus player, such as playing
    tracks as well as getting the current status of the player.
    '''

    def is_running(self):
        '''
        It is important for the rest of the application to be aware as to
        whether or not a player is running.
        '''
        if subprocess.call(['cmus-remote', '-C']) == 0:
            return True
        else:
            return False

    def update_status(self):
        '''
        Updates the contents of the status dictionary with the most recent
        output from cmus.
        '''
        self.status = {'artist': None, 'album': None, 'title': None,
                       'vol_left': None, 'vol_right': None, 'playing': False,
                       'duration': 0, 'position': 0, 'repeat': False,
                       'shuffle': False}
        # Setting stderr to subprocess.STDOUT seems to stop the error
        # message returned by the process from being output to STDOUT.
        cmus_output = subprocess.check_output(['cmus-remote', '-Q'],
                                    stderr=subprocess.STDOUT).decode('utf-8')

        cmus_status = self.convert_cmus_output(cmus_output)
        for key in self.status:
            self.status[key] = cmus_status[key]

    def send_cmd(self, cmd):
        '''
        Provides a uniform way for the application to send commands to cmus
        and other players.
        '''
        command = {
            'play': '-p',
            'pause': '-u',
            'vol_up': '-v +5',
            'vol_down': '-v -5',
            'next': '-n',
            'prev': '-r',
            'stop': '-s'
        }.get(cmd)
        if command:
            subprocess.call(['cmus-remote'] + command.split())

    def convert_cmus_output(self, cmus_output):
        """
        Change the newline separated string of output data into
        a dictionary.

        cmus_output: A string with information about cmus that is newline
        seperated. Running cmus-remote -Q in a terminal will show you what
        you're dealing with.
        """
        cmus_output = cmus_output.split('\n')
        cmus_output = [x.replace('tag ', '')
                       for x in cmus_output if not x in '']
        cmus_output = [x.replace('set ', '') for x in cmus_output]
        status = {}
        partitioned = (item.partition(' ') for item in cmus_output)
        status = {item[0]: item[2] for item in partitioned}
        status['playing'] = cmus_output[0].split()[-1]
        return status
