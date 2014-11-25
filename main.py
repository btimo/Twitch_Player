import Tkinter as tk
import ttk
import gstreamer_module, livestreamer_module
import gi
from gi.repository import GObject

GObject.threads_init()


class GUI():
    def __init__(self):
        self.root = tk.Tk()
        self.player = gstreamer_module.Player()
        self.stream = livestreamer_module.Stream()
        self.playable = False
        self.playing = False
        self.buildUI()
        self.root.mainloop()

    # callbacks

    def play(self):
        if not self.playing:
            self.player.initGstreamer()
            self.player.set_frame(self.player_frame_id)
            self.player.on_start(self.stream.get_stream_file())
            self.playing = True

    def stop(self):
        self.player.on_stop()
        self.playing = False

    def set_volume(self):
        pass



    def search(self):
        # send streamer name to the livestreamer module
        name = self.streamer_entry.get()

        # find stream
        try:
            self.stream_online = self.stream.find_stream('twitch.tv/'+name)

        finally:
            self.stream.set_quality('best')
            if self.stream_online == 0:
                # offline
                pass
            elif self.stream_online == 1:
                if not self.playing:
                    self.play()
                else:
                    self.stop()
                    self.play()
                # online
            else:
                # not a valid link
                pass

        #activate play and pause button
        self.play_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)

    # Main Window construction

    def create_top_frame(self):
        search_frame = tk.Frame(self.root)
        self.streamer_entry = tk.Entry(search_frame)
        streamer_button = tk.Button(search_frame, text='search streamer', command=self.search)
        self.streamer_entry.pack()
        streamer_button.pack()
        search_frame.pack()

    def create_player_frame(self):
        player_frame = tk.Frame(self.root, width=500, height=500)
        player_frame.pack(fill=tk.BOTH, expand=1)
        self.player_frame_id = player_frame.winfo_id()

    def create_bottom_frame(self):
        bottom_frame = tk.Frame(self.root)
        self.play_button = tk.Button(bottom_frame, text='Play', state=tk.DISABLED , command=self.play)
        self.pause_button = tk.Button(bottom_frame, text='Pause', state=tk.DISABLED , command=self.stop)
        self.play_button.pack()
        self.pause_button.pack()
        bottom_frame.pack()

    def buildUI(self):
        self.create_top_frame()
        self.create_player_frame()
        self.create_bottom_frame()


def main():
    app = GUI()

if __name__ == '__main__':
    main()