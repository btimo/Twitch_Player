import Tkinter as tk
import ttk
import player
import gi
from gi.repository import GObject

GObject.threads_init()


class GUI():
    def __init__(self, player):
        self.player = player
        player.parent = self
        self.root = tk.Tk()
        self.init = True
        self.buildUI()
        self.init = False
        self.root.mainloop()

    def search(self):
        # send streamer name to the livestreamer module
        name = self.streamer_entry.get()
        if not self.init:
            if self.player.initStream(name):
                self.play_button.config(state=tk.NORMAL)
                self.pause_button.config(state=tk.NORMAL)

    def create_top_frame(self):
        search_frame = tk.Frame(self.root)
        self.streamer_entry = tk.Entry(search_frame)
        streamer_button = tk.Button(search_frame, text='search streamer', command=self.search)
        self.streamer_entry.pack()
        streamer_button.pack()
        search_frame.pack()

    def create_player_frame(self):
        player_frame = tk.Frame(self.root, width=500, height=500)
        player_frame.pack()

        #send xid to player
        self.player.parent_xid = player_frame.winfo_id()

    def create_bottom_frame(self):
        bottom_frame = tk.Frame(self.root)
        self.play_button = tk.Button(bottom_frame, text='Play', state=tk.DISABLED , command=self.player.play)
        self.pause_button = tk.Button(bottom_frame, text='Pause', state=tk.DISABLED , command=self.player.stop)
        self.play_button.pack()
        self.pause_button.pack()
        bottom_frame.pack()

    def buildUI(self):
        self.create_top_frame()
        self.create_player_frame()
        self.create_bottom_frame()


def main():
    player_object = gstreamer_module.Player()
    app = GUI(player_object)

if __name__ == '__main__':
    main()