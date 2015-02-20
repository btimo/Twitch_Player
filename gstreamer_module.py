# -*- coding: utf-8 -*-

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GstVideo
# from gi.repository import GstVideo, GstAudio

from livestreamer import StreamError

Gst.init(None)


class Player():
    def __init__(self):
        # fd will contain
        self.fd = None
        self.initGstreamer()

    def initGstreamer(self):
        # create pipeline
        self.pipeline = Gst.Pipeline()

        # create bus and connect event
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::eos', self.on_end_of_stream)
        self.bus.connect('message::error', self.on_error)

        # listen to sync message to link pipeline output and gui frame
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message::element', self.on_sync_message)

        # create playbin element
        self.playbin = Gst.ElementFactory.make("playbin", )
        # add playbin to pipeline
        self.pipeline.add(self.playbin)
        # set property of playbin for app source
        self.playbin.set_property("uri", 'appsrc://')
        # set callback for playbin and source setup
        self.playbin.connect('source-setup', self.on_source_setup)

    def set_frame(self, frame):
        # Gui frame id
        self.frame = frame

    def on_sync_message(self, bus, msg):
        # sync message for window handle (work on windows only)
        # need to listen for different msg on osx and linux
        if msg.get_structure().get_name() == 'prepare-window-handle':
            msg.src.set_window_handle(self.frame)

    def on_source_setup(self, element, source):
        # setup appsrc
        source.connect('need-data', self.on_source_need_data)

    def on_source_need_data(self, source, length):
        try:
            data = self.fd.read(length)
        except IOError:
            print "Player.on_source_need_data : failed to read data"

        if not data:
            source.emit("end-of-stream")
            return

        # stock the media data in the buffer (will be displayed by the sink)
        buf = Gst.Buffer.new_wrapped(data)
        source.emit('push-buffer', buf)

    def on_end_of_stream(self, bus, msg):
        self.pipeline.set_state(Gst.State.NULL)
        print 'end of stream'

    def on_error(self, bus, msg):
        self.pipeline.set_state(Gst.State.NULL)
        print msg.parse_error()[1]

    def on_stop(self):
        # set element state to null then
        # unref element
        self.pipeline.set_state(Gst.State.NULL)
        if self.fd:
            self.fd.close()

    def on_start(self, stream):
        try:
            self.fd = stream.open()
        except StreamError:
            print "Player.on_start : Failed to open stream"

        self.pipeline.set_state(Gst.State.PLAYING)


if __name__ == '__main__':
    print "videoStream is a class implementing Gstreamer package to\
             accomodate a Tkinter GUI and Livestreamer appsrc"
