from screens.mopidy.screens.base_list_screen import BaseListScreen
from screens.mopidy.utils import Utils


class LibraryScreen(BaseListScreen):
    def __init__(self, ws,  **kwargs):
        super(LibraryScreen, self).__init__(ws, **kwargs)
        self.current_dir = [None]
        for name, value in kwargs.items():
            if name == 'main_screen':
                self.main_scrren = value

    def browse(self, uri):
        self.ws.send(
            Utils.get_message(
                Utils.id_browse_loaded, "core.library.browse", {'uri': uri}))

    def on_selection_change(self, adapter):
        if len(self.adapter.selection) > 0:
            data = adapter.data[adapter.selection[0].index]
            if adapter.selection[0].index == 0 and data['name'] == '../':
                self.go_up()
                print("GO UP")
            else:
                self.current_dir.append(data['uri'])
                self.browse(data['uri'])
                self.adapter.selection = []
                print('TODO ----- TODO')
                print(data['name'])
                print(data['type'])
                print(data)
                if data['type'] == 'track':
                    self.ws.send(
                        Utils.get_message(0, "core.tracklist.clear"))
                    # if not data['uri'].endswith(('.m3u', '.m3u8')):
                    self.ws.send(
                        Utils.get_message(
                            0, "core.tracklist.add", {"uri": data['uri']}))
                    self.ws.send(
                        Utils.get_message(0, "core.playback.play"))
                    # go to now_playing_screen
                    self.main_scrren.change_screen(-1)
                    self.main_scrren.change_screen(-1)
                    print('TODO END ----- TODO END')

    def go_up(self):
        self.current_dir.pop()
        uri = self.current_dir[-1]
        self.browse(uri)

    def result_loaded(self, result, id):
        if id == Utils.id_browse_loaded:
            if len(result) > 0:
                data = []
                if len(self.current_dir) > 1:
                    data = [{'name': '../'}]
                for item in result:
                    data.append(item)
                print(data)
                self.adapter.data = data
            else:
                if len(self.current_dir) > 1:
                    data = [{'name': '../'}]
                else:
                    data = []
                self.adapter.data = data
