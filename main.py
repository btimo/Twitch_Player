import Tkinter as tk
import ttk
from PIL import Image, ImageTk
from StringIO import StringIO
import gstreamer_module, livestreamer_module, browse_module
import gi
from gi.repository import GObject

GObject.threads_init()


class GUI():
    def __init__(self):
        self.root = tk.Tk()
        self.root.minsize(300,300)
        self.root.geometry("900x600")
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



    def browse_games(self, offset=None):
        print "browse games"
        # make request for game list
        games_list, next_list = browse_module.get_games(None, offset)

        # if watching, stop and destroy play frame
        if self.watching:
            print "stop watching"
            self.stop()
            self.watching = False
            self.browsing = True
            for child in self.main_frame.winfo_children():
                child.destroy()
            self.create_browsing_panel()
            self.create_table(games_list, next_list)
        else:
            self.create_table(games_list, next_list)
        



    def browse_channels(self, elem, offset=None):
        print "browse channels"
        channel_list, next_list = elem.access_game_streams(offset)
        self.create_table(channel_list, next_list)

    def watch_stream(self, elem):
        print "watch stream"
        self.browsing = False
        self.watching = True
        #clear main_frame
        for child in self.main_frame.winfo_children():
            child.destroy()

        # create player frame
        self.create_playing_frame()
        self.stream.find_stream(elem.url)
        self.stream.set_quality('best')

        self.play()


    def browse_search(self):
        print 'browse search'
        channel_list = browse_module.search_request(self.search_entry.get())
        self.browsing = True
        self.watching = False

        if self.watching:
            print "stop watching"
            self.stop()
            self.watching = False
            self.browsing = True
            for child in self.main_frame.winfo_children():
                child.destroy()
            self.create_browsing_panel()
            self.create_table(channel_list, None)
        else:
            self.create_table(channel_list, None)

        
    # Main Window construction
    def create_left_side_panel(self):
        print "left side panel"
        # recreate the left panel of twitch:
        self.left_pane = tk.Frame(self.root, width=150)
        # - Search
        self.search_entry = tk.Entry(self.left_pane)
        self.search_entry.pack(fill=tk.X)
        search_button = tk.Button(self.left_pane, text='Search', command=self.browse_search)
        search_button.pack(fill=tk.X)
        # - Following
        # - Games
        games_button = tk.Button(self.left_pane, text='Games', command=lambda: self.browse_games())
        games_button.pack(fill=tk.X, side=tk.TOP)
        # - Channel
        channels_button = tk.Button(self.left_pane, text='Channels', command=self.browse_channels)
        channels_button.pack(fill=tk.X, side=tk.TOP)
        # - User

        # add left side panel to root
        self.left_pane.pack(fill=tk.Y, side=tk.LEFT)

    # MainFrame when browsing
    def create_table(self, object_list, next_list):
        print "create_table"
        # if browsing game
        if self.table_frame.winfo_children():
            for child in self.table_frame.winfo_children():
                child.destroy()
        height = self.table_frame.winfo_height()
        width = self.table_frame.winfo_width()
        button_width = 136
        button_height = 190
        preview_width = 320
        max_col_preview = width // preview_width
        max_col = width // button_width
        i = 0
        # make a button for all the games in the list
        for elem in object_list:
            m = max_col if isinstance(elem, browse_module.Game) else max_col_preview
            pic = elem.pic_medium if isinstance(elem, browse_module.Game) else elem.preview
            im = ImageTk.PhotoImage(Image.open(StringIO(browse_module.request_image(pic))))
            but = tk.Button(self.table_frame, text=elem.name if isinstance(elem, browse_module.Game) else elem.display_name, image=im, compound=tk.TOP, height=button_height + 50,wraplength=100, command=lambda elem=elem : self.browse_channels(elem) if isinstance(elem, browse_module.Game) else self.watch_stream(elem))
            but.image = im
            but.grid(row=(i//m), column=(i%m), sticky=tk.N+tk.S+tk.E+tk.W)
            # tk.Grid.columnconfigure(self.table_frame,i,weight=1, minsize=136)
            # tk.Grid.rowconfigure(self.table_frame,i//max_col, weight=1, minsize=190)
            i += 1
        # make button for accessing the next games 
        if next_list != None:
            tk.Button(self.table_frame, text='Next games', command=lambda: self.browse_games(next_list['offset']) if isinstance(elem, browse_module.Game) 
                else self.browse_channels(elem, next_list['offset'])).grid(row=(i//m), column=(i%m), sticky=tk.N+tk.S+tk.E+tk.W)


    def create_browsing_panel(self):
        print "browsing panel"
        # left pane with search entry, games button, channel button, follows button, user button
        self.title_bar = tk.Frame(self.main_frame)
        self.title_bar_title_label = tk.Label(self.title_bar, text="All games")
        self.title_bar_title_label.pack(side=tk.LEFT)
        self.title_bar_search_entry = tk.Entry(self.title_bar)
        self.title_bar_search_entry.pack(side=tk.RIGHT)
        self.title_bar.pack(side=tk.TOP, fill=tk.X) 
        # mid pane with result : set size for each result, dynamic row/col with window size
        # last res is offset for more.
        # call function to create the table
        self.table_frame = tk.Frame(self.main_frame)
        self.table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.root.update()


    # MainFrame when watching
    def create_playing_frame(self):
        self.play_frame = tk.Frame()
        # video frame
        # player and control
        self.create_player_frame()
        # self.create_bottom_frame()
        # chat frame


    def create_player_frame(self):
        # setting empty bg fix flickering
        player_frame = tk.Frame(self.main_frame, bg='')
        player_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.player_frame_id = player_frame.winfo_id()


    def defaultUI(self):
        print "default ui"
        self.create_left_side_panel()
        print "create main frame"
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack_propagate(0)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.create_browsing_panel()
        self.browse_games()


def main():
    app = GUI()

if __name__ == '__main__':
    main()