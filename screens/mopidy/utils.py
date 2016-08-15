# encoding=utf8
import json
import os
import subprocess
from threading import Thread


class Utils:
    id_tracklist_loaded = 10
    id_cover_loaded = 11
    id_current_track_loaded = 12
    id_current_time_position_loaded = 13
    id_current_status_loaded = 14
    id_search_result = 15
    id_playlists_loaded = 16
    id_browse_loaded = 17
    id_volume = 18
    speak_on = True
    lang = 'pl'

    @staticmethod
    def format_time_to_string(seconds_total):
        duration_text = str(seconds_total / 60) + ':'
        seconds = seconds_total % 60
        if seconds < 10:
            duration_text += '0' + str(seconds)
        else:
            duration_text += str(seconds)
        return duration_text

    @staticmethod
    def get_title_string(tl_track):
        name = "nazwa..."
        try:
            if 'track' in tl_track:
                name = tl_track['track']['name']
            else:
                name = tl_track['name']
        except Exception:
            pass
        return name

    @staticmethod
    def get_album_string(tl_track):
        name = "album..."
        try:
            name = tl_track['track']['album']['name']
        except Exception:
            pass
        return name

    @staticmethod
    def get_artist_string(tl_track):
        name = "artysta..."
        try:
            if len(tl_track['track']['artists']) > 0:
                name = ""
                for artist in tl_track['track']['artists']:
                    name += artist['name'] + " "
        except Exception:
            pass
        return name

    @staticmethod
    def get_message(id, method, params=None):
        message = {}
        message['jsonrpc'] = '2.0'
        message['id'] = id
        message['method'] = method
        if params is not None:
            message['params'] = params
        return json.dumps(message)

    @staticmethod
    def convert_text(text):
        try:
            t = text.encode("utf8", "ignore")
        except Exception as e:
            print(str(e))
            t = 'Error ' + e.message

        t = t.replace('_', ' ')
        t = t.replace('-', ' ')
        # remove the file extension
        t = os.path.splitext(t)[0]
        return t

    @staticmethod
    def speak_text(text, thread=True):
        if thread:
            os.system('pkill espeak')
            t = Thread(target=Utils.speak_text_thread, args=(text,))
            t.start()
        else:
            os.system(
                ' echo "' + text + '" | espeak -v ' + Utils.lang + ' > /dev/null 2>&1')

    @staticmethod
    def speak_text_thread(text):
            os.system(
                ' echo "' + text + '" | espeak -v ' + Utils.lang + ' > /dev/null 2>&1')

    @staticmethod
    def speak(code, *param, **key):

        if Utils.speak_on is False:
            return 0

        if ('val' in key):
            val = key['val']
            if not isinstance(val, str) and not isinstance(val, unicode):
                val = str(val)
            val = Utils.convert_text(val)

        if code == 'PLAY':
            if Utils.lang == 'pl':
                Utils.speak_text("Graj", False)
            elif Utils.lang == 'en':
                Utils.speak_text("Play", False)
        if code == 'PLAYING':
            if Utils.lang == 'pl':
                Utils.speak_text("Gramy " + val)
            elif Utils.lang == 'en':
                Utils.speak_text("Now playing " + val)
        if code == 'PAUSE':
            if Utils.lang == 'pl':
                Utils.speak_text("Pauza", False)
            elif Utils.lang == 'en':
                Utils.speak_text("Pause", False)
        if code == 'SPEAK_ON':
            if Utils.lang == 'pl':
                Utils.speak_text("Podpowiedzi")
            elif Utils.lang == 'en':
                Utils.speak_text("Hints on")
        if code == 'SPEAK_OFF':
            if Utils.lang == 'pl':
                Utils.speak_text("Bez podpowiedzi")
            elif Utils.lang == 'en':
                Utils.speak_text("Hints off")
        if code == 'VOL':
            if Utils.lang == 'pl':
                Utils.speak_text("głośność " + val)
            elif Utils.lang == 'en':
                Utils.speak_text("Volume " + val)
        if code == 'MUTE':
            if Utils.lang == 'pl':
                Utils.speak_text("Wycisz")
            elif Utils.lang == 'en':
                Utils.speak_text("Mute")
        if code == 'NEXT':
            if Utils.lang == 'pl':
                Utils.speak_text("Następny", False)
            elif Utils.lang == 'en':
                Utils.speak_text("Next", False)
        if code == 'PREV':
            if Utils.lang == 'pl':
                Utils.speak_text("Poprzedni", False)
            elif Utils.lang == 'en':
                Utils.speak_text("Previous", False)
        if code == 'CHP':
            if Utils.lang == 'pl':
                Utils.speak_text("Biblioteka")
            elif Utils.lang == 'en':
                Utils.speak_text("library")
        if code == 'CH':
            if Utils.lang == 'pl':
                Utils.speak_text("Odtwarzacz")
            elif Utils.lang == 'en':
                Utils.speak_text("Player")
        if code == 'CHM':
            if Utils.lang == 'pl':
                Utils.speak_text("Listy")
            elif Utils.lang == 'en':
                Utils.speak_text("Play lists")
        if code == 'NUM0':
            if Utils.lang == 'pl':
                Utils.speak_text("Numer 0")
            elif Utils.lang == 'en':
                Utils.speak_text("Number 0")
        if code == 'FLM':
            if Utils.lang == 'pl':
                Utils.speak_text("Fl minus")
            elif Utils.lang == 'en':
                Utils.speak_text("Fl minus")
        if code == 'FLP':
            if Utils.lang == 'pl':
                Utils.speak_text("Fl plus")
            elif Utils.lang == 'en':
                Utils.speak_text("Fl plus")
        if code == 'NUM9':
            if Utils.lang == 'pl':
                Utils.speak_text("Informacja")
            elif Utils.lang == 'en':
                Utils.speak_text("Information")
        if code == 'LIST_ITEM':
                Utils.speak_text(val)
        if code == 'ENTER_DIR':
            if Utils.lang == 'pl':
                Utils.speak_text("Wybierz " + val)
            elif Utils.lang == 'en':
                Utils.speak_text("Go to " + val)
        if code == 'PLAY_URI':
            if Utils.lang == 'pl':
                Utils.speak_text("Włączam " + val)
            elif Utils.lang == 'en':
                Utils.speak_text("Playing " + val)
        if code == 'GO_UP_DIR':
            if Utils.lang == 'pl':
                Utils.speak_text("Idz do góry")
            elif Utils.lang == 'en':
                Utils.speak_text("Go up")
        if code == 'UP_DIR':
            if Utils.lang == 'pl':
                Utils.speak_text("Do góry")
            elif Utils.lang == 'en':
                Utils.speak_text("Up")
        if code == 'NO_TRACK':
            if Utils.lang == 'pl':
                Utils.speak_text("Aktualnie nie jest odtwarzany żaden utwór")
            elif Utils.lang == 'en':
                Utils.speak_text("Currently we do not play any song")
        if code == 'NO_PLAYLISTS':
            if Utils.lang == 'pl':
                Utils.speak_text("Brak list odtwarzania")
            elif Utils.lang == 'en':
                Utils.speak_text("We do not have any playlist")
        if code == 'AUDIOBOOKS_DIR':
            if Utils.lang == 'pl':
                Utils.speak_text("Audiobuki")
            elif Utils.lang == 'en':
                Utils.speak_text("Audiobooks")
        if code == 'INFO_DIR':
            if Utils.lang == 'pl':
                Utils.speak_text("Informacje")
            elif Utils.lang == 'en':
                Utils.speak_text("Information")
        if code == 'MUSIC_DIR':
            if Utils.lang == 'pl':
                Utils.speak_text("Muzyka")
            elif Utils.lang == 'en':
                Utils.speak_text("Music")
        if code == 'PODCAST_DIR':
            if Utils.lang == 'pl':
                Utils.speak_text("Podkasty")
            elif Utils.lang == 'en':
                Utils.speak_text("Podcasts")
        if code == 'RADIO_DIR':
            if Utils.lang == 'pl':
                Utils.speak_text("Radio")
            elif Utils.lang == 'en':
                Utils.speak_text("Radio")
        if code == 'NO_LIBRARY':
            if Utils.lang == 'pl':
                Utils.speak_text("Brak pozycji w bibliotece")
            elif Utils.lang == 'en':
                Utils.speak_text("There is nothing in the library")
        if code == 'LIB_SCREAN_INFO':
            if Utils.lang == 'pl':
                Utils.speak_text("Jesteś w bibliotece, mamy tu " + val)
            elif Utils.lang == 'en':
                Utils.speak_text("You are in library, we have here " + val)
        if code == 'PL_SCREAN_INFO':
            if Utils.lang == 'pl':
                Utils.speak_text("Listy odtwarzania")
            elif Utils.lang == 'en':
                Utils.speak_text("Playlists")
        if code == 'TR_SCREAN_INFO':
            if Utils.lang == 'pl':
                Utils.speak_text("Lista utworów ma " + val + ' pozycji')
            elif Utils.lang == 'en':
                Utils.speak_text("Tracks list has " + val + ' entries')
        if code == 'BRIGHTNESS':
            if Utils.lang == 'pl':
                Utils.speak_text("jasność " + val)
            elif Utils.lang == 'en':
                Utils.speak_text("brightness " + val)

    @staticmethod
    def get_actual_brightness():
        ab = subprocess.check_output(
            'cat /sys/class/backlight/rpi_backlight/actual_brightness',
            shell=True)
        return ab

    @staticmethod
    def set_actual_brightness(ab):
        Utils.speak('BRIGHTNESS', val=str(ab))
        os.system(
            'echo ' + str(ab) +
            ' > /sys/class/backlight/rpi_backlight/brightness')

    @staticmethod
    def backlight_up():
        try:
            ab = Utils.get_actual_brightness()
            ab = min(255, int(ab) + 30)
            ab = max(0, ab)
            Utils.set_actual_brightness(ab)
        except Exception as e:
            print(str(e))

    @staticmethod
    def backlight_down():
        try:
            ab = Utils.get_actual_brightness()
            ab = min(255, int(ab) - 30)
            ab = max(0, ab)
            Utils.set_actual_brightness(ab)
        except Exception as e:
            print(str(e))
