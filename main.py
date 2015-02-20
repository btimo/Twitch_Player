# -*- coding: utf-8 -*-

import Tkinter as tk
# import ttk
from PIL import Image, ImageTk
from StringIO import StringIO
import gstreamer_module
import livestreamer_module
import browse_module

from gi.repository import GObject

GObject.threads_init()


class GUI():
    def __init__(self):
        self.root = tk.Tk()
        self.root.minsize(300, 300)
        self.root.geometry("900x600")
        self.player = gstreamer_module.Player()
        self.stream = livestreamer_module.Stream()
        self.browsing = True
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
        # make request for game list
        games_list, next_list = browse_module.get_games(None, offset)

        # if watching, stop and destroy play frame
        if self.watching:
            self.from_watch_to_browse()
        # call create_table to make a table with the game list
        self.create_table(games_list, next_list)

    def browse_channels(self, elem, offset=None):
        # request the channel list for a specific game
        channel_list, next_list = elem.access_game_streams(offset)
        self.create_table(channel_list, next_list)

    def watch_stream(self, elem):
        self.browsing = False
        self.watching = True
        # clear main_frame
        for child in self.main_frame.winfo_children():
            child.destroy()

        # create irc frame
        # self.create_irc_frame()

        # create player frame
        self.create_playing_frame()
        
        self.stream.find_stream(elem.url)
        self.stream.set_quality('best')

        self.play()

    def from_watch_to_browse(self):
        self.stop()
        self.watching = False
        self.browsing = True
        # remove all the childs from main_frame
        for child in self.main_frame.winfo_children():
            child.destroy()
        # recreate the title bar and the table frame
        self.create_browsing_panel()

    def browse_search(self):
        # make request with entry string
        channel_list = browse_module.search_request(self.search_entry.get())

        # if watching
        if self.watching:
            self.from_watch_to_browse

        self.create_table(channel_list, None)

    # Main Window construction
    def create_left_side_panel(self):
        # recreate the left panel of twitch:
        self.left_pane = tk.Frame(self.root, width=150)
        # - Search
        self.search_entry = tk.Entry(self.left_pane)
        self.search_entry.pack(fill=tk.X)
        search_button = tk.Button(self.left_pane,
                                  text='Search',
                                  command=self.browse_search)
        search_button.pack(fill=tk.X)
        # - Following
        # - Games
        games_button = tk.Button(self.left_pane,
                                 text='Games',
                                 command=lambda: self.browse_games())
        games_button.pack(fill=tk.X, side=tk.TOP)
        # - Channel
        channels_button = tk.Button(self.left_pane,
                                    text='Channels',
                                    command=self.browse_channels)
        channels_button.pack(fill=tk.X, side=tk.TOP)
        # - User

        # add left side panel to root
        self.left_pane.pack(fill=tk.Y, side=tk.LEFT)

    # MainFrame when browsing
    def create_table(self, object_list, next_list):
        # called to draw a 2D table with games/channel/search result

        # clear the table frame to draw others element
        if self.table_canvas_frame.winfo_children():
            for child in self.table_canvas_frame.winfo_children():
                child.destroy()

        # get dimension of window to put element in the right place
        # height = self.table_frame.winfo_height()
        width = self.table_frame.winfo_width()

        # constant size of button for
        # - game list
        game_img_width = 136
        game_img_height = 190
        # - channel list
        channel_preview_width = 320

        # calc for element by column and row
        max_col_preview = width // channel_preview_width
        max_col = width // game_img_width

        # iterator for element position
        i = 0

        # make a button for all the games in the list
        for elem in object_list:
            # get number of element by row (depend of elem type)
            m = max_col if isinstance(elem, browse_module.Game)\
                else max_col_preview
            # get picture of elem
            pic = elem.pic_medium if isinstance(elem, browse_module.Game)\
                else elem.preview
            im = ImageTk.PhotoImage(Image.open(
                StringIO(browse_module.request_image(pic))))
            # create button for elem
            but = tk.Button(
                self.table_canvas_frame,
                text=elem.name if isinstance(elem, browse_module.Game)
                else elem.display_name,
                image=im,
                compound=tk.TOP,
                height=game_img_height + 50,
                wraplength=100,
                command=lambda elem=elem: self.browse_channels(elem)
                if isinstance(elem, browse_module.Game)
                else self.watch_stream(elem))
            # re set the image parameter to force it to show
            but.image = im
            but.grid_propagate(0)
            but.grid(row=(i // m),
                     column=(i % m),
                     sticky=tk.N+tk.S+tk.E+tk.W)
            # tk.Grid.columnconfigure(self.table_frame,i,weight=1,
            # minsize=136)
            # tk.Grid.rowconfigure(self.table_frame,i//max_col, weight=1,
            # minsize=190)
            i += 1

        # make button for accessing the next part of the list if there is any
        if next_list is not None:
            tk.Button(
                self.table_canvas_frame,
                text='Next Games' if isinstance(elem, browse_module.Game)
                else 'Next Channels',
                height=10,
                command=lambda:
                self.browse_games(next_list['offset'])
                if isinstance(elem, browse_module.Game)
                else self.browse_channels(elem, next_list['offset'])
                ).grid(row=(i // m),
                       column=(i % m),
                       sticky=tk.N+tk.S+tk.E+tk.W)

        # draw object inside canvas to update its dimension.
        self.table_canvas_frame.update_idletasks()
        self.table_canvas.config(scrollregion=self.table_canvas.bbox("all"))

    def create_browsing_panel(self):
        # title bar for section title (All games/Game name) and search entry
        # for specific element in the table
        self.title_bar = tk.Frame(self.main_frame)
        # title
        self.title_bar_title_label = tk.Label(self.title_bar,
                                              text="All games")
        self.title_bar_title_label.pack(side=tk.LEFT)
        # entry
        self.title_bar_search_entry = tk.Entry(self.title_bar)
        self.title_bar_search_entry.pack(side=tk.RIGHT)

        self.title_bar.pack(side=tk.TOP, fill=tk.X)

        # table to contain the elements
        self.table_frame = tk.Frame(self.main_frame)
        # give importance to the canvas
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        # create the scrollbar
        yscrollbar = tk.Scrollbar(self.table_frame)
        yscrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)

        self.table_canvas = tk.Canvas(self.table_frame,
                                      yscrollcommand=yscrollbar.set,
                                      bg='black')
        self.table_canvas.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

        self.table_canvas_frame = tk.Frame(self.table_canvas)

        self.table_canvas.create_window(0,
                                        0,
                                        anchor=tk.N + tk.W,
                                        window=self.table_canvas_frame)

        yscrollbar.config(command=self.table_canvas.yview)

        self.table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.root.update()

    # MainFrame when watching
    def create_playing_frame(self):
        # create player_frame
        self.create_player_frame()
        # create overlay

    def create_irc_frame(self):
        # self.irc_frame = tk.Frame(self.main_frame, width=200, bg='red')

        # self.irc_text_area = tk.

        # self.irc_frame.pack(side=tk.RIGHT, fill=tk.Y)

        pass
        # # init irc


    def create_player_frame(self):
        # create frame for the player
        # set bg to "" fix flickering
        player_frame = tk.Frame(self.main_frame, bg='')
        player_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # get frame id for gstreamer sync-message
        self.player_frame_id = player_frame.winfo_id()

    def defaultUI(self):
        # create left side panel
        self.create_left_side_panel()
        # create main_frame (title, table, player)
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # size not controlled by child
        self.main_frame.pack_propagate(0)
        # create browsing panel (title, table)
        self.create_browsing_panel()
        # browse game once to initialize the table
        self.browse_games()


def main():
    GUI()

if __name__ == '__main__':
    main()
