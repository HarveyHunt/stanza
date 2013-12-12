import urwid

class TextLine(urwid.WidgetWrap):
    
    def __init__(self, line_number, max_line_length, text, alt_line):
        if alt_line and line_number % 2:
            self.content = [('fixed', max_line_length, urwid.AttrWrap(
                urwid.Text(str(line_number), align='right'), 'list_num')),
                urwid.AttrWrap(urwid.Text(text), 'list_text')]
        else:
            self.content = [('fixed', max_line_length, urwid.AttrWrap(
                urwid.Text(str(line_number), align='right'), 'list_num_alt')),
                urwid.AttrWrap(urwid.Text(text), 'list_text_alt')]

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
        self.conf = config

        self.header = urwid.Text('')
        self.footer = urwid.Text('')
        self.header_format = self.conf['header_format']
        self.footer_format = self.conf['footer_format']
        self.simple_list = urwid.SimpleListWalker([])
        self.listbox = LyricListBox(self.simple_list)
        self.view = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'), 
                header=urwid.AttrWrap(self.header, 'header'),
                footer=urwid.AttrWrap(self.footer, 'footer'))
        palette = self._generate_palette()
        self.loop = urwid.MainLoop(self.view, palette,
                                    unhandled_input=self._keystroke)

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
            formatting = self.header_format
        else:
            formatting = self.footer_format
        markup = ''.join({formatting.replace('<' + k + '>', str(v))
                        for k, v in data.items()})
        if bar is 'header':
            self.header.set_text(markup)
        else:
            self.footer.set_text(markup)

        if refresh:
            self.loop.draw_screen()
        
    def set_listbox_data(self, data, refresh=True):
        data = data.split('\n')
        max_lines = len(str(len(data)))
        self.simple_list.contents[:] = [TextLine(i, max_lines, text,
                                    self.conf['alt_list']) for i,
                                    text in enumerate(data)]
        if refresh:
            self.loop.draw_screen()

    def set_footer_data(self, data, refresh=True):
        self._set_bar_data('footer', data, refresh)

    def set_header_data(self, data, refresh=True):
        self._set_bar_data('header', data, refresh)