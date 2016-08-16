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

    def change_selection(self):
        item = self.ids.list_view.adapter.get_view(self.current_item)
        item.trigger_action(duration=0)

    def on_selection_change(self, adapter):
        self.current_item = 0
        if len(self.adapter.selection) > 0:
            data = adapter.data[adapter.selection[0].index]
            if adapter.selection[0].index == 0 \
               and '../' in data['name']:
                    self.go_up()
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
                    self.main_screen.go_to_screen('Odtwarzacz')
                    Utils.speak('PLAY_URI', val=data['name'])
                else:
                    Utils.speak('ENTER_DIR', val=data['name'])

    def go_up(self):
        if len(self.current_dir) == 1:
            Utils.speak('CH')
            self.main_screen.go_to_screen('Odtwarzacz')
        else:
            Utils.speak('GO_UP_DIR')
            self.current_dir.pop()
            uri = self.current_dir[-1]
            self.browse(uri)

    def select_current_item(self):
        i = 0
        data = []
        for item in self.adapter.data:
            item['name'] = item['name'].replace("-> ", "")
            item['name'] = item['name'].replace(" <-", "")
            if i == self.current_item:
                item['name'] = "-> " + item['name'] + " <-"
            data.append(item)
            i += 1
        self.adapter.data = data
        self.adapter.data.prop.dispatch(self.adapter.data.obj())

    def next_item(self):
        if len(self.adapter.data) == self.current_item + 1:
            self.current_item = 0
        else:
            self.current_item = self.current_item + 1
        view = self.ids.list_view.adapter.get_view(self.current_item)
        view.select()
        if view.text == '../' or view.text == '-> ../ <-':
            Utils.speak('UP_DIR')
        else:
            Utils.speak_text(Utils.convert_text(view.text))
        self.select_current_item()

    def prev_item(self):
        if self.current_item == 0:
            self.current_item = len(self.adapter.data) - 1
        else:
            self.current_item = self.current_item - 1
        view = self.ids.list_view.adapter.get_view(self.current_item)
        view.select()
        if view.text == '../' or view.text == '-> ../ <-':
            Utils.speak('UP_DIR')
        else:
            Utils.speak_text(Utils.convert_text(view.text))
        self.select_current_item()

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
            self.select_current_item()
        pass
