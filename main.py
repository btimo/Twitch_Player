from livestreamer import Livestreamer, StreamError, PluginError, NoPluginError

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject as gobject, Gst as gst, GstVideo, Gdk, GstAudio

import Tkinter, sys, ttk

gst.init(None)





class LivestreamerPlayer(object):
    def __init__(self, window_id):
        self.fd = None
        self.win_id = window_id

        # This creates a playbin pipeline and using the appsrc source
        # we can feed it our stream data
        self.pipeline = gst.Pipeline()
       

        #create Bus to get event from Gstreamer Pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message::eos", self.on_eos)
        self.bus.connect("message::error", self.on_error)

        # Needed for video output
        self.bus.enable_sync_message_emission()
        self.bus.connect("sync-message::element", self.on_sync_message)


        # Create Gstreamer elements
        self.playbin = gst.ElementFactory.make("playbin", None)

        #add element to the pipeline
        self.pipeline.add(self.playbin)
        
        #Set uri properties
        self.playbin.set_property("uri", "appsrc://")

        # When the playbin creates the appsrc source it will call
        # this callback and allow us to configure it
        self.playbin.connect("source-setup", self.on_source_setup)

       

    def exit(self, msg):
        self.stop()

    def stop(self):
        # Stop playback and exit mainloop
        self.pipeline.set_state(gst.State.NULL)

        # Close the stream
        if self.fd:
            self.fd.close()

    def play(self, stream):
        # Attempt to open the stream
        try:
            self.fd = stream.open()
        except StreamError as err:
            self.exit("Failed to open stream: {0}".format(err))

        # Start playback
        self.pipeline.set_state(gst.State.PLAYING)

    def on_sync_message(self, bus, message):
        if message.get_structure() is None:
            return

        message_name = message.get_structure().get_name()
        if message_name == "prepare-window-handle":
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_window_handle(self.win_id)


    def on_source_setup(self, element, source):
        # When this callback is called the appsrc expects
        # us to feed it more data
        source.connect("need-data", self.on_source_need_data)

    def on_source_need_data(self, source, length):
        # Attempt to read data from the stream
        try:
            data = self.fd.read(length)
        except IOError as err:
            self.exit("Failed to read data from stream: {0}".format(err))

        # If data is empty it's the end of stream
        if not data:
            source.emit("end-of-stream")
            return

        # Convert the Python bytes into a GStreamer Buffer
        # and then push it to the appsrc
        buf = gst.Buffer.new_wrapped(data)
        source.emit("push-buffer", buf)

    def on_eos(self, bus, msg):
        # Stop playback on end of stream
        self.stop()

    def on_error(self, bus, msg):
        # Print error message and exit on error
        error = msg.parse_error()[1]
        self.exit(error)

    def set_volume(self, vol):
        self.pipeline.set_property('volume', vol)

class toolbarFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.quality_options = None
        self.volume_scale_value = 50
        self.initUI()

    def start_player(self):
        self.parent.start_stream()

    def stop_player(self):
        self.parent.stop_stream()

    def go_fullscreen(self):
        self.parent.fullscreen_video()

    def set_volume(vol):
        self.parent.player.set_volume(float (vol) / 100)


    def set_quality_options(self, list_):
        self.quality_options = list_
        self.quality_combobox.config(values=self.quality_options)
        self.quality_combobox.set('best')

    def initUI(self):

        # Play button
        self.play_button = ttk.Button(self, text='P', command=self.start_player)
        self.play_button.grid(row=0, column=0)
        # Stop Button
        self.stop_button = ttk.Button(self, text='S', command=self.stop_player)
        self.stop_button.grid(row=0, column = 1)

        # fullscreen button
        self.fullscreen_button = ttk.Button(self, text='F', command=self.go_fullscreen)
        self.fullscreen_button.grid(row=0, column=2)
        # Quality combobox
        self.quality_combobox = ttk.Combobox(self, values=self.quality_options)
        self.quality_combobox.grid(row=0, column=4)

        # volume scale
        self.volume_scale = ttk.Scale(self, from_=0, to=100, command=self.set_volume)
        self.volume_scale.grid(row=0, column=5)
        self.volume_label = ttk.Label(self, text=self.volume_scale.get())
        self.volume_label.grid(row=0, column=6)

    





class MainFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.watching = False
        self.fullscreen_bool = False
        self.video_focused = False
        self.initUI()
        self.update_geo()
        self.video_frame.focus_set()
        # print 'here'
        self.video_winfo_id = self.parent.focus_get()
        # print 'there'
        # print self.parent.focus_get()
        self.search_field.focus_set()


    def start_stream():
        if not self.watching:
            self.watching = True
            self.stream_status.config(text='Watching ' + self.search_field.get())

            #fixer probleme de double stream.
            #faire varialbe classe pour empecher ca.
            
            stream = self.streams[self.quality_o.get()]

            #Create the player and start playback
            self.player = LivestreamerPlayer(self.window_handle_id)

            #add player to video_field

            self.volume_scale.state(['!disabled'])
            self.volume_scale.set(50)
            #Blocks until playback is done
            self.player.play(stream)

        else:
            self.stop_stream()

    def stop_stream():
        if self.watching:
            self.player.stop()
            self.watching = False


    def initUI(self):
        def clicked(event):
            if self.parent.focus_get() != self.video_winfo_id:
                # print 'video not focused'
                self.video_focused = False

        def focus_video_frame(event):
            self.video_frame.focus_set()
            self.video_focused = True
            # print 'video frame focused'

        def undo_fullscreen(key):
            if self.fullscreen_bool:
                self.search_frame.grid(row=0)
                self.parent.overrideredirect(False)
                self.parent.geometry('{0}x{1}+0+0'.format(self.current_width, self.current_height))
                self.fullscreen_bool = False

        def fullscreen_video(*key):
            if self.fullscreen_bool and self.player:
                undo_fullscreen('')
            elif self.player:
                self.search_frame.grid_forget()
                self.fullscreen_bool = True
                self.parent.overrideredirect(True)
                self.update_geo()
                self.parent.geometry('{0}x{1}+0+0'.format(self.parent.winfo_screenwidth(), self.parent.winfo_screenheight()))


        def set_vol_mouse(event):
            if self.watching and self.video_focused:
                current_vol = self.player.pipeline.get_property('volume') * 100
                #wheel vers le bas -> baisse le son
                if event.delta == -120 and current_vol > 0:
                    set_vol(current_vol - 5)
                    self.volume_scale.set(current_vol - 5)
                #wheel vers le haut -> monte le son
                elif event.delta == 120 and current_vol < 100 :
                    set_vol(current_vol + 5)
                    self.volume_scale.set(current_vol + 5)

        def set_vol(vol):
            if self.watching:
                self.player.set_volume(float(vol) / 100)


        def update_options():
            opts = self.streams.keys()
            opts.sort()
            #set default quality to best
            self.toolbar_frame.set_quality_options(opts)

        


        


        def start_search():
            if self.search_field:
                url = 'http://twitch.tv/' + str(self.search_field.get())
                self.stream_status.config(text='Searching streamer '+ self.search_field.get() +' ...')
               
                #create livestreamer session
                livestreamer = Livestreamer()

                #enable logging
                livestreamer.set_loglevel('info')
                livestreamer.set_logoutput(sys.stdout)

                #attempt to fetch stream
                try:
                    self.streams = livestreamer.streams(url)
                except NoPluginError:
                    print "Livestreamer is unable to handle the url " + url
                except PluginError as err:
                    print 'Plugin error: ' + str(err)

                if not self.streams:
                    print 'No streams found on URL ' + url
                    self.stream_status.config(text='Streamer '+ self.search_field.get() + ' is offline ...')

                #Look for specific quality
                # if quality not in streams:
                #     print "unable to find '{0}' stream on URL '{1}'".format(
                #                                                 quality, url)

                #We found the stream
                #search for all the quality options
                else:
                    update_options()
                    self.stream_status.config(text='Select stream quality ...')
            


        self.search_frame = ttk.LabelFrame(self.parent, text=' Search streamer ')
        self.search_frame.grid(sticky="we")
        self.search_field = ttk.Entry(self.search_frame)
        self.search_field.grid(row=0, column = 0, sticky="we")
        self.stream_status = ttk.Label(self.search_frame, text='Waiting for streamer nickname ...', width=100)
        self.stream_status.grid(row=0, column=1)

        self.toolbar_frame = toolbarFrame(self.parent)
        self.toolbar_frame.grid(row=2)
        

        




        search_button = ttk.Button(self.search_frame, text='Search streamer',
                                command=start_search)
        search_button.grid(row=1, column=0)

        # print 'search frame created'

        # creation d'une frame pour livestreamer/gstreamer
        self.video_frame = ttk.Frame(self.parent, width=768, height=564)
        self.video_frame.grid(row=1, sticky='nswe')

        #search frame should grow columnwise
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(1, weight=1)
        # self.columnconfigure(0, weight=1)
        #video frame should grow columnwise and rowwise


        # print 'video frame created ...'

        self.window_handle_id = self.video_frame.winfo_id()

        # print 'video window handle id:', self.video_frame.winfo_id()


        #Key binding
        #Escape -> undo fullscreen
        self.parent.bind('<Escape>', undo_fullscreen)
        self.video_frame.bind('<Double-Button-1>', fullscreen_video)
        self.parent.bind_all('<MouseWheel>', set_vol_mouse)
        self.parent.bind_all('<Button-1>', clicked)
        self.video_frame.bind('<Button-1>', focus_video_frame)


        # stream settings panel
        # quality settings

        # volume settings

        # pause

        # stop

    def update_geo(self):
        self.parent.update()
        self.current_height = self.parent.winfo_height()
        self.current_width = self.parent.winfo_width()



def main():
    window_master = ttk.Tkinter.Tk()
    # print 'master window created ...'
    app = MainFrame(window_master)
    # Gdk.threads_init()
    window_master.mainloop()





if __name__ == "__main__":
    main()
