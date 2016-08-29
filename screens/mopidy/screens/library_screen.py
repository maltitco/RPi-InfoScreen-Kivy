from screens.mopidy.screens.base_list_screen import BaseListScreen
from screens.mopidy.utils import Utils


class LibraryScreen(BaseListScreen):
    def __init__(self, ws,  **kwargs):
        super(LibraryScreen, self).__init__(ws, **kwargs)
        self.do_init(True)
        for name, value in kwargs.items():
            print('LibraryScreen name: ' + str(name))
            if name == 'main_screen':
                self.main_screen = value

    def do_init(self, full=False):
        if full:
            self.current_dir = [None]
            self.browse(None)
        self.current_item = 0
        self.clear_list_item_selection()
        self.ids.list_view.scroll_to(0)
        # view = self.adapter.get_view(self.current_item)
        # if view is not None:
        #     self.adapter.select_item_view(view)

    def browse(self, uri):
        self.ws.send(
            Utils.get_message(
                Utils.id_browse_loaded, "core.library.browse", {'uri': uri}))

    def change_selection(self):
        # item = self.ids.list_view.adapter.get_view(self.current_item)
        # item.trigger_action(duration=0)
        self.on_selection_change(self.ids.list_view.adapter)

    def on_selection_change(self, adapter):
        if len(adapter.selection) > 0:
            idx = adapter.selection[0].index
            data = adapter.data[idx]
            if idx == 0 and '../' in data['name']:
                    self.go_up()
            else:
                self.go_uri(data)
        # clear
        self.clear_list_item_selection()

    def go_up(self):
        if len(self.current_dir) == 1:
            Utils.speak('CH')
            self.main_screen.go_to_screen('Odtwarzacz')
        else:
            Utils.speak('GO_UP_DIR')
            self.current_dir.pop()
            uri = self.current_dir[-1]
            self.browse(uri)

    def go_uri(self, data):
        self.current_dir.append(data['uri'])
        self.browse(data['uri'])
        if data['type'] == 'track':
            self.ws.send(
                Utils.get_message(0, "core.tracklist.clear"))
            self.ws.send(
                Utils.get_message(
                    0, "core.tracklist.add", {"uri": data['uri']}))
            self.ws.send(
                Utils.get_message(0, "core.playback.play"))
            self.main_screen.go_to_screen('Odtwarzacz')
            Utils.speak('PLAY_URI', val=data['name'])
        else:
            Utils.speak('ENTER_DIR', val=data['name'])

    def next_item(self):
        self.clear_list_item_selection()
        if len(self.adapter.data) == self.current_item + 1:
            self.current_item = 0
        else:
            self.current_item = self.current_item + 1
        view = self.ids.list_view.adapter.get_view(self.current_item)
        self.ids.list_view.adapter.select_item_view(view)
        # scrolling
        selected_index = self.adapter.selection[0].index
        if selected_index > 4:
            self.ids.list_view.scroll_to(selected_index - 4)
        else:
            self.ids.list_view.scroll_to(0)

        if view.text == '../':
            Utils.speak('UP_DIR')
        else:
            Utils.speak_text(Utils.convert_text(view.text))

    def prev_item(self):
        self.clear_list_item_selection()
        if self.current_item == 0:
            self.current_item = len(self.adapter.data) - 1
        else:
            self.current_item = self.current_item - 1
        view = self.ids.list_view.adapter.get_view(self.current_item)
        self.ids.list_view.adapter.select_item_view(view)
        # scrolling
        selected_index = self.adapter.selection[0].index
        if selected_index > 4:
            self.ids.list_view.scroll_to(selected_index - 4)
        else:
            self.ids.list_view.scroll_to(0)

        if view.text == '../':
            Utils.speak('UP_DIR')
        else:
            Utils.speak_text(Utils.convert_text(view.text))

    def result_loaded(self, result, id):
        if id == Utils.id_browse_loaded:
            if len(result) > 0:
                data = []
                if len(self.current_dir) > 1:
                    data = [{'name': '../'}]
                for item in result:
                    data.append(item)
            else:
                if len(self.current_dir) > 1:
                    data = [{'name': '../'}]
                else:
                    data = []
            self.adapter.data = data
            self.do_init(False)
        pass
