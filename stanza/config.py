import configparser
import os.path
import errno


class Config():

    def __init__(self):
        self.folderPaths = [os.path.join(os.path.expanduser('~'),
                        '.config/stanza'), '/etc/stanza']
        for path in self.folderPaths:
            if os.path.isdir(path):
                self._folderPath = path
                break
        else:
            self._folderPath = self.folderPaths[0]
            self._touchdir(self._folderPath)

        self._conf = configparser.SafeConfigParser()
        # A weird trick to retain the case of sections and keys.
        self._conf.optionxform = str
        self._confFilePath = os.path.join(self._folderPath, 'config')
        self.reload()

    def _touchdir(self, path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                    raise

    def reload(self):
        self._conf.read(self._confFilePath)
        self.general = self._replaceDataTypes(dict(self._conf.items('general')))
        self.interface = self._replaceDataTypes(dict(self._conf.items('interface')))

    def _replaceDataTypes(self, dictionary):
        """
        Replaces strings with appropriate data types (int, boolean).
        Also replaces the human readable logging levels with the integer form.

        dictionary: A dictionary returned from the config file.
        """
        loggingLevels = {'NONE': 0, 'NULL': 0, 'DEBUG': 10, 'INFO': 20, 'WARNING': 30,
                         'ERROR': 40, 'CRITICAL': 50}
        for k, v in dictionary.items():
            if v in ['true', 'True', 'on']:
                dictionary[k] = True
            elif v in ['false', 'False', 'off']:
                dictionary[k] = False
            elif k == 'logFile' and '~' in v:
                dictionary[k] = v.replace('~', os.path.expanduser('~'))
            elif v in loggingLevels:
                dictionary[k] = loggingLevels[v]
            elif isinstance(v, str) and v.isnumeric():
                dictionary[k] = int(v)
            elif ',' in v:
                dictionary[k] = [x.lstrip() for x in v.split(',')]
        return dictionary
