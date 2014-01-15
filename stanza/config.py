import configparser
import os.path
import errno


class Config:
    '''
    Manages configuration of the application.
    '''

    def __init__(self):
        self.folder_paths = [os.path.join(os.path.expanduser('~'),
                                         '.config/stanza'), '/etc/stanza']
        for path in self.folder_paths:
            if os.path.isdir(path):
                self._folder_path = path
                break
        else:
            self._folder_path = self.folder_paths[0]
            self._touchdir(self._folder_path)

        self._conf = configparser.SafeConfigParser()
        # A weird trick to retain the case of sections and keys.
        self._conf.optionxform = str
        self._conf_file_path = os.path.join(self._folder_path, 'config')
        self.reload()

    def _touchdir(self, path):
        '''
        Create a directory if it doesn't exist.
        '''
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                    raise

    def reload(self):
        '''
        Reload the categories of configuration.
        '''
        self._conf.read(self._conf_file_path)
        self.general = self._replace_data_types(
            dict(self._conf.items('general')))
        self.interface = self._replace_data_types(
            dict(self._conf.items('interface')))

    def _replace_data_types(self, dictionary):
        """
        Replaces strings with appropriate data types (int, boolean).
        Also replaces the human readable logging levels with the integer form.

        dictionary: A dictionary returned from the config file.
        """
        logging_levels = {
            'NONE': 0, 'NULL': 0, 'DEBUG': 10, 'INFO': 20, 'WARNING': 30,
            'ERROR': 40, 'CRITICAL': 50}
        for k, v in dictionary.items():
            if v in ['true', 'True', 'on']:
                dictionary[k] = True
            elif v in ['false', 'False', 'off']:
                dictionary[k] = False
            elif k == 'log_file' and '~' in v:
                dictionary[k] = v.replace('~', os.path.expanduser('~'))
            elif v in logging_levels:
                dictionary[k] = logging_levels[v]
            elif isinstance(v, str) and v.isnumeric():
                dictionary[k] = int(v)
            elif ',' in v:
                dictionary[k] = [x.lstrip() for x in v.split(',')]
        return dictionary
