import urwid


class TextLine(urwid.WidgetWrap):

    def __init__(self, line_number, max_line_length, text, alt_line,
                 line_num_sep_char, line_num_sep_width):
        if alt_line and line_number % 2:
            alt = True
        else:
            alt = False
        self.content = []
        # Add in the line numbers.
        self.content.append(('fixed', max_line_length, urwid.AttrWrap(
            urwid.Text(str(line_number), align='right'),
            'list_num_alt' if alt else 'list_num')))
        # Add in the seperator between the line numbers and the text.
        self.content.append(('fixed', line_num_sep_width,
                             urwid.AttrWrap(urwid.Text(line_num_sep_char), 'line_num_sep')))
        # Add the line of text.
        self.content.append(urwid.AttrWrap(urwid.Text(text),
                                           'list_text_alt' if alt else 'list_text'))

        widg = urwid.Columns(self.content)
        super().__init__(widg)

    def selectable(self):
        return False


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

        self.header = urwid.Text('')
        self.footer = urwid.Text('')
        self.header_format = self.conf['header_format']
        self.footer_format = self.conf['footer_format']
        self.simple_list = urwid.SimpleListWalker([])
        self.listbox = LyricListBox(self.simple_list)

        frame_header = urwid.Pile([urwid.AttrWrap(self.header, 'header'),
                                   urwid.Divider(div_char=self.conf['header_div_char'])])
        frame_footer = urwid.Pile([urwid.Divider(div_char=
                                                 self.conf['footer_div_char']),
                                   urwid.AttrWrap(self.footer, 'footer')])

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

    def _set_bar_data(self, bar, data, refresh=True):
        if bar is 'header':
            markup = self.header_format
        else:
            markup = self.footer_format
        for k, v in data.items():
            markup = markup.replace('<' + k + '>', str(v))
        if bar is 'header':
            self.header.set_text(markup)
        else:
            self.footer.set_text(markup)

        if refresh:
            self.is_dirty = True

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

    def set_footer_data(self, data, refresh=True):
        self._set_bar_data('footer', data, refresh)

    def set_header_data(self, data, refresh=True):
        self._set_bar_data('header', data, refresh)
