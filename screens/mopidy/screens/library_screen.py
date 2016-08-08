from screens.mopidy.screens.base_list_screen import BaseListScreen
from screens.mopidy.utils import Utils


class LibraryScreen(BaseListScreen):
    def __init__(self, ws,  **kwargs):
        super(LibraryScreen, self).__init__(ws, **kwargs)
        self.current_dir = [None]
        self.current_item = 0
        self.current_uri = ''
        for name, value in kwargs.items():
            if name == 'main_screen':
                self.main_screen = value

    def browse(self, uri):
        self.current_uri = uri
        self.ws.send(
            Utils.get_message(
                Utils.id_browse_loaded, "core.library.browse", {'uri': uri}))

    def on_selection_change(self, adapter):
        if len(self.adapter.selection) > 0:
            data = adapter.data[adapter.selection[0].index]
            if adapter.selection[0].index == 0 \
               and '../' in data['name']:
                    self.go_up()
                    print("GO UP")
            else:
                self.current_dir.append(data['uri'])
                self.browse(data['uri'])
                self.adapter.selection = []
                if data['type'] == 'track':
                    self.ws.send(
                        Utils.get_message(0, "core.tracklist.clear"))
                    # if not data['uri'].endswith(('.m3u', '.m3u8')):
                    self.ws.send(
                        Utils.get_message(
                            0, "core.tracklist.add", {"uri": data['uri']}))
                    self.ws.send(
                        Utils.get_message(0, "core.playback.play"))
                    self.main_screen.go_to_screen('Now Playing')

    def go_up(self):
        self.current_dir.pop()
        uri = self.current_dir[-1]
        self.browse(uri)

    def next_item(self):
        self.current_item = min(
            self.current_item + 1, len(self.adapter.data) - 1)
        self.browse(self.current_uri)

    def prev_item(self):
        self.current_item = max(0, self.current_item - 1)
        self.browse(self.current_uri)

    def result_loaded(self, result, id):
        self.current_result = result
        i = 0
        if id == Utils.id_browse_loaded:
            if len(result) > 0:
                data = []
                if len(self.current_dir) > 1:
                    if self.current_item == 0:
                        data = [{'name': '-> ../ <-'}]
                    else:
                        data = [{'name': '../'}]
                for item in result:
                    if i + 1 == self.current_item:
                        for key in item.keys():
                            if key == 'name':
                                item[key] = "-> " + item[key] + " <-"
                    data.append(item)
                    i += 1
                self.adapter.data = data
            else:
                if len(self.current_dir) > 1:
                    if self.current_item == 0:
                        data = [{'name': '-> ../ <-'}]
                    else:
                        data = [{'name': '../'}]
                else:
                    data = []
                self.adapter.data = data
