import Tkinter as tk
import ttk
import gstreamer_module, livestreamer_module, browse_module
import gi
from gi.repository import GObject

GObject.threads_init()


class GUI():
    def __init__(self):
        self.root = tk.Tk()
        self.player = gstreamer_module.Player()
        self.stream = livestreamer_module.Stream()
        self.browsing= True
        self.watching = False
        self.playing = False
        self.defaultUI()
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


    def browse_games(self):
        #get games list and link for next list
        games_list, next_list = browse_module.get_games()
        # create a table




    def browse_channels(self):
        pass

    def browse_search(self):
        # # send streamer name to the livestreamer module
        # name = self.search_entry.get()
        pass
        # # find stream
        # try:
        #     self.stream_online = self.stream.find_stream('twitch.tv/'+name)

        # finally:
        #     self.stream.set_quality('best')
        #     if self.stream_online == 0:
        #         # offline
        #         pass
        #     elif self.stream_online == 1:
        #         if not self.playing:
        #             self.play()
        #         else:
        #             self.stop()
        #             self.play()
        #         # online
        #     else:
        #         # not a valid link
        #         pass

        # #activate play and pause button
        # self.play_button.config(state=tk.NORMAL)
        # self.pause_button.config(state=tk.NORMAL)

    # Main Window construction

    # MainFrame when browsing
    def create_browsing_frame(self):
        # left pane with search entry, games button, channel button, follows button, user button
        pass
        # mid pane with result : set size for each result, dynamic row/col with window size
        # last res is offset for more.

    # MainFrame when watching
    def create_watching_frame(self):
        # left side pane
        # create video frame
        pass
        # create controller frame
        # create irc frame

    # def create_top_frame(self):
    #     search_frame = tk.Frame(self.root)
    #     self.streamer_entry = tk.Entry(search_frame)
    #     streamer_button = tk.Button(search_frame, text='search streamer', command=self.search)
    #     self.streamer_entry.pack()
    #     streamer_button.pack()
    #     search_frame.pack()

    def create_left_side_panel(self):
        # recreate the left panel of twitch:
        self.left_pane = tk.Frame(self.root, width=150)
        # - Search
        self.search_entry = tk.Entry(self.left_pane)
        self.search_entry.pack(fill=tk.X)
        search_button = tk.Button(self.left_pane, text='Search', command=self.browse_search)
        search_button.pack(fill=tk.X)
        # - Following
        # - Games
        games_button = tk.Button(self.left_pane, text='Games', command=self.browse_games)
        games_button.pack(fill=tk.X, side=tk.TOP)
        # - Channel
        channels_button = tk.Button(self.left_pane, text='Channels', command=self.browse_channels)
        channels_button.pack(fill=tk.X, side=tk.TOP)
        # - User

        # add left side panel to root
        self.left_pane.pack(fill=tk.Y, expand=1, side=tk.LEFT)
        
       


    def create_playing_frame(self):
        self.play_frame = tk.Frame()
        # video frame
        # player and control
        self.create_player_frame()
        self.create_bottom_frame()
        # chat frame


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

    def defaultUI(self):
        # self.create_top_frame()
        # self.create_player_frame()
        # self.create_bottom_frame()
        self.create_left_side_panel()


def main():
    app = GUI()

if __name__ == '__main__':
    main()