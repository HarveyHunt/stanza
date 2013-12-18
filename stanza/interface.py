import datetime
import urwid


class TextLine(urwid.WidgetWrap):

    def __init__(self, line_number, max_line_length, text, alt_line,
                 line_num_sep_char, line_num_sep_width):
        if alt_line and line_number % 2:
            alt = True
        else:
            alt = False
        content = []
        # Add in the line numbers.
        content.append(('fixed', max_line_length, urwid.AttrWrap(
            urwid.Text(str(line_number), align='right'),
            'list_num_alt' if alt else 'list_num')))
        # Add in the seperator between the line numbers and the text.
        content.append(('fixed', line_num_sep_width,
                             urwid.AttrWrap(urwid.Text(line_num_sep_char), 'line_num_sep')))
        # Add the line of text.
        content.append(urwid.AttrWrap(urwid.Text(text),
                                    'list_text_alt' if alt else 'list_text'))

        widg = urwid.Columns(content)
        super().__init__(widg)

    def selectable(self):
        return False


class Bar(urwid.WidgetWrap):

    def __init__(self, formatting, attr_name):
        contents = []
        if '<progress>' in formatting:
            self._start_formatting = formatting.split('<progress>')[0].rstrip()
            self._end_formatting = formatting.split('<progress>')[1].lstrip()
            self._prog = urwid.ProgressBar(attr_name + '_prog_normal',
                                        attr_name + '_prog_complete')
            self._start_text = urwid.Text('') if self._start_formatting != '' else None
            self._end_text = urwid.Text('') if self._end_formatting != '' else None

            if self._start_text:
                contents.append(urwid.AttrWrap(self._start_text, attr_name))
            contents.append(self._prog)
            if self._end_text:
                contents.append(urwid.AttrWrap(self._end_text, attr_name))
        else:
            self._formatting = formatting
            self._text = urwid.Text('')

            contents.append(urwid.AttrWrap(self._text, attr_name))
        widg = urwid.Columns(contents)
        widg.options(width_type='pack')
        super().__init__(widg)

    def set_data(self, data):
        if hasattr(self, '_text') and self._text is not None:
            self._set_text_only(self._text, self._formatting, data)
            return
        if hasattr(self, '_start_text') and self._start_text is not None:
            self._set_text_only(self._start_text, self._start_formatting, data)
        if hasattr(self, '_end_text') and self._end_text is not None:
            self._set_text_only(self._end_text, self._end_formatting, data)
        
        self._prog.set_completion((int(data['position']) / int(data['duration'])) * 100)

    def _set_text_only(self, text_obj, formatting, data):
        for k, v in data.items():
            if k in ['duration', 'position']:
                formatting = formatting.replace('<' + k + '>',
                        self._convert_time(v))
            else:
                formatting = formatting.replace('<' + k + '>', str(v))
        text_obj.set_text(formatting)

    def _convert_time(self, time):
        """
        A helper function to convert seconds into hh:mm:ss for better
        readability.

        time: A string representing time in seconds.
        """
        time_string = str(datetime.timedelta(seconds=int(time)))
        if time_string.split(':')[0] == '0':
            time_string = time_string.partition(':')[2]
        return time_string


class LyricListBox(urwid.ListBox):

    def __init__(self, body):
        super().__init__(body)

    def keypress(self, size, key):
        if key is 'j':
            self.keypress(size, 'down')
        elif key is 'k':
            self.keypress(size, 'up')
        return super().keypress(size, key)


class StanzaUI():

    def __init__(self, config):
        self.is_dirty = False
        self.conf = config

        self.header = Bar(self.conf['header_format'], 'header')
        self.footer = Bar(self.conf['footer_format'], 'footer')
        self.simple_list = urwid.SimpleListWalker([])
        self.listbox = LyricListBox(self.simple_list)

        frame_header = urwid.Pile([self.header,
                                   urwid.Divider(div_char=self.conf['header_div_char'])])
        frame_footer = urwid.Pile([urwid.Divider(div_char=
                                                 self.conf['footer_div_char']),
                                   self.footer])

        self.view = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'),
                                header=frame_header, footer=frame_footer)
        palette = self._generate_palette()
        self.loop = urwid.MainLoop(self.view, palette=palette,
                                   unhandled_input=self._keystroke)
        self.loop.screen.set_terminal_properties(colors=
                                                 self.conf['terminal_colours'])

    def _keystroke(self, key):
        if key is 'q':
            raise urwid.ExitMainLoop()

    def run(self):
        self.loop.run()

    def _generate_palette(self):
        pal = []
        for setting, value in self.conf.items():
            if setting.endswith('_col') and value is not '':
                pal.append(tuple([setting.split('_col')[0]] + value))
        return pal

    def set_listbox_data(self, data, refresh=True):
        data = data.split('\n')
        max_lines = len(str(len(data)))
        self.simple_list.contents[:] = [TextLine(i, max_lines, text,
                                                 self.conf['alt_list'],
                                                 self.conf['line_num_sep_char'],
                                                 self.conf['line_num_sep_width'])
                                                 for i, text in enumerate(data)]
        if refresh:
            self.is_dirty = True
