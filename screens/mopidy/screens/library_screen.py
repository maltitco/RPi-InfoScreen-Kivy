from screens.mopidy.screens.base_list_screen import BaseListScreen
from screens.mopidy.screens.base_screen import BaseScreen
from screens.mopidy.utils import Utils


class LibraryScreen(BaseListScreen):

    def __init__(self, ws,  **kwargs):
        super(LibraryScreen, self).__init__(ws, **kwargs)
        self.current_dir = [None]

    def browse(self, uri):
        self.ws.send(Utils.get_message(Utils.id_browse_loaded, "core.library.browse", {'uri': uri}))

    def on_selection_change(self, adapter):
        if len(self.adapter.selection) > 0:
            data = adapter.data[adapter.selection[0].index]
            if adapter.selection[0].index == 0 and data['name'] == '../':
                self.go_up()
            else:
                self.current_dir.append(data['uri'])
                self.browse(data['uri'])
                self.adapter.selection = []

    def go_up(self):
        self.current_dir.pop()
        uri = self.current_dir[-1]
        self.browse(uri)

    def result_loaded(self, result, id):
        if id == Utils.id_browse_loaded:
            if len(result) > 1:
                data = []
                if len(self.current_dir) > 1:
                    data = [{'name':'../'}]
                for item in result:
                    data.append(item)
                print data
                self.adapter.data = data
            else:
                if len(self.current_dir) > 1:
                    data = [{'name':'../'}]
                else:
                    data = []
                self.adapter.data = data