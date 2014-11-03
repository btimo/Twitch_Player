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
        self.pipeline = gst.ElementFactory.make("playbin", None)
        self.pipeline.set_property('video-sink', None)
        self.pipeline.set_property("uri", "appsrc://")

        # When the playbin creates the appsrc source it will call
        # this callback and allow us to configure it
        self.pipeline.connect("source-setup", self.on_source_setup)

        # Creates a bus and set callbacks to receive errors
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.enable_sync_message_emission()
        self.bus.connect("message::eos", self.on_eos)
        self.bus.connect("message::error", self.on_error)
        self.bus.connect("sync-message::element", self.on_sync_message)
        print 'bus connected ...'

    def exit(self, msg):
        self.stop()
        exit(msg)

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
        print 'got sync'

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



class MainFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.watching = False
        self.fullscreen_bool = False
        self.initUI()
        self.update_geo()


    def initUI(self):

        def undo_fullscreen(key):
            self.parent.overrideredirect(False)
            self.parent.geometry('{0}x{1}+0+0'.format(self.current_width, self.current_height))
            self.fullscreen_bool = False

        def fullscreen_video():
            if self.fullscreen_bool:
                undo_fullscreen('')
            else:
                self.fullscreen_bool = True
                self.parent.overrideredirect(True)
                self.update_geo()
                self.parent.geometry('{0}x{1}+0+0'.format(self.parent.winfo_screenwidth(), self.parent.winfo_screenheight()))




        def set_vol(vol):
            if self.watching:
                self.player.set_volume(float(vol) / 100)


        def update_options():
            opts = self.streams.keys()
            opts.sort()
            #set default quality to best
            self.quality_o.set('best')
            self.quality_combobox.config(values=opts)
            self.quality_combobox.state(["!disabled"])

        def stop_stream():
            if self.watching:
                self.player.stop()
                self.watching = False


        def start_stream():
            if not self.watching:
                self.watching = True
                self.stream_status.config(text='Watching ' + search_field.get())

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
                stop_stream()
            


        search_frame = ttk.LabelFrame(self.parent, text=' Search streamer ')
        search_frame.grid(sticky="we")
        search_field = ttk.Entry(search_frame)
        search_field.grid(row=0, column = 0, sticky="we")
        self.stream_status = ttk.Label(search_frame, text='Waiting for streamer nickname ...', width=100)
        self.stream_status.grid(row=0, column=1)
        self.quality_o = ttk.Tkinter.StringVar(search_frame)
        self.quality_combobox = ttk.Combobox(search_frame, textvariable = self.quality_o)
        self.quality_combobox.state(["disabled"])
        self.quality_combobox.grid(row=0, column=3, columnspan = 2)
        self.start_button = ttk.Button(search_frame, text='Start Stream', command=start_stream )
        self.start_button.state(["disabled"])
        self.start_button.grid(row=1, column = 3)
        self.stop_button = ttk.Button(search_frame, text='Stop', command=stop_stream)
        self.stop_button.state(["disabled"])
        self.stop_button.grid(row=1, column = 4)
        volume_label = ttk.Label(search_frame, text=' Volume ')
        volume_label.grid(row=0, column=5)
        self.volume_scale = ttk.Scale(search_frame, from_=0, to=100, command=set_vol)
        self.volume_scale.state(["disabled"])
        self.volume_scale.grid(row=1, column = 5)
        fullscreen_button = ttk.Button(search_frame, text='fullscreen', command=fullscreen_video)
        fullscreen_button.grid(row=0, column=6)

        def start_search():
            if search_field:
                url = 'http://twitch.tv/' + str(search_field.get())
                self.stream_status.config(text='Searching streamer '+ search_field.get() +' ...')
               
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
                    self.stream_status.config(text='Streamer '+ search_field.get() + ' is offline ...')

                #Look for specific quality
                # if quality not in streams:
                #     print "unable to find '{0}' stream on URL '{1}'".format(
                #                                                 quality, url)

                #We found the stream
                #search for all the quality options
                else:
                    update_options()
                    self.stream_status.config(text='Select stream quality ...')
                    self.start_button.state(["!disabled"])
                    self.stop_button.state(["!disabled"])




        search_button = ttk.Button(search_frame, text='Search streamer',
                                command=start_search)
        search_button.grid(row=1, column=0)

        print 'search frame created'

        # creation d'une frame pour livestreamer/gstreamer
        video_lframe = ttk.LabelFrame(self.parent, text=' Stream ')
        video_lframe.grid(row=1, column=0, sticky="nswe")
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(1, weight=1)
        self.video_frame = ttk.Frame(video_lframe, width=768, height=564)
        self.video_frame.pack(fill='both', expand=1)
        print 'video frame created ...'

        self.window_handle_id = self.video_frame.winfo_id()

        print 'video window handle id:', self.video_frame.winfo_id()

        self.parent.bind('<Escape>', undo_fullscreen)


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
    print 'master window created ...'
    app = MainFrame(window_master)
    # Gdk.threads_init()
    window_master.mainloop()





if __name__ == "__main__":
    main()
