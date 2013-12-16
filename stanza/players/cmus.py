import subprocess
import datetime

class Player():

    def __init__(self):
        pass

    def is_running(self):
        if subprocess.call(['cmus-remote', '-C']) == 0:
            return True
        else:
            return False

    def update_status(self):
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
        cmus_output = [x.replace('tag ', '') for x in cmus_output if not x in '']
        cmus_output = [x.replace('set ', '') for x in cmus_output]
        status = {}
        partitioned = (item.partition(' ') for item in cmus_output)
        status = {item[0]: item[2] for item in partitioned}
        status['duration'] = self.convert_time(status['duration'])
        status['position'] = self.convert_time(status['position'])
        status['playing'] = cmus_output[0].split()[-1]
        return status

    def convert_time(self, time):
        """
        A helper function to convert seconds into hh:mm:ss for better
        readability.

        time: A string representing time in seconds.
        """
        time_string = str(datetime.timedelta(seconds=int(time)))
        if time_string.split(':')[0] == '0':
            time_string = time_string.partition(':')[2]
        return time_string

