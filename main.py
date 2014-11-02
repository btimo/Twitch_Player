from livestreamer import Livestreamer, StreamError, PluginError, NoPluginError

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject as gobject, Gst as gst, GstVideo, Gdk

import Tkinter, sys

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

class MainFrame(Tkinter.Frame):
    def __init__(self, parent):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.watching = False
        self.initUI()

    def initUI(self):
        search_frame = Tkinter.LabelFrame(self.parent, text=' Search streamer ')
        search_frame.grid(sticky="we")
        search_field = Tkinter.Entry(search_frame)
        search_field.grid(sticky="we")


        def start_search():
            if not self.watching:
                self.watching = True
            else:
                self.player.stop()

            if search_field:
                quality = 'best'
                url = 'http://twitch.tv/' + search_field.get()
                #create livestreamer session
                livestreamer = Livestreamer()

                #enable logging
                livestreamer.set_loglevel('info')
                livestreamer.set_logoutput(sys.stdout)

                #attempt to fetch stream
                try:
                    streams = livestreamer.streams(url)
                except NoPluginError:
                    print "Livestreamer is unable to handle the url " + url
                except PluginError as err:
                    print 'Plugin error: ' + err

                if not streams:
                    print 'No streams found on URL ' + url

                #Look for specific quality
                if quality not in streams:
                    print "unable to find '{0}' stream on URL '{1}'".format(
                                                                quality, url)

                #We found the stream
                stream = streams[quality]

                #Create the player and start playback
                self.player = LivestreamerPlayer(self.window_handle_id)

                #add player to video_field


                #Blocks until playback is done
                self.player.play(stream)


        search_button = Tkinter.Button(search_frame, text='Search streamer',
                                command=start_search)
        search_button.grid(pady=8)

        print 'search frame created'

        # creation d'une frame pour livestreamer/gstreamer
        video_lframe = Tkinter.LabelFrame(self.parent, text=' Stream ')
        video_lframe.grid(row=1, column=0, sticky="nswe")
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(1, weight=1)
        video_frame = Tkinter.Frame(video_lframe, width=768, height=564, bg='black')
        video_frame.pack(fill='both', expand=1)
        print 'video frame created ...'

        self.window_handle_id = video_frame.winfo_id()

        print 'video window handle id:', video_frame.winfo_id()

        # stream settings panel
        # quality settings

        # volume settings

        # pause

        # stop






def main():
    window_master = Tkinter.Tk()
    print 'master window created ...'
    app = MainFrame(window_master)
    # Gdk.threads_init()
    window_master.mainloop()



if __name__ == "__main__":
    main()
