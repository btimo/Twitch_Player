# -*- coding: utf-8 -*-

from livestreamer import Livestreamer, NoPluginError
# from livestreamer import PluginError, StreamError


class Stream(object):
    def __init__(self):
        # open session.
        self.session = Livestreamer()

    def find_stream(self, link):
        # find stream from link
        try:
            self.streams_dict = self.session.streams(link)
        # stream exist ?
        except NoPluginError:
            print "Link error"
            return -1

        if not self.streams_dict:
            print "Streams is offline"
            return 0

        return 1

        # stream online

    def set_quality(self, quality):
        # choose a stream quality
        self.quality = quality

    def get_stream_qualities(self):
        return self.streams_dict.keys()

    def change_stream_quality(self, quality):
        self.select_stream_quality(quality)
        self.stream_media = self.streams_dict[self.quality]

    def get_stream_file(self):
        try:
            return self.streams_dict[self.quality]
        except:
            print "Stream.get_stream_file: Shouldnt be called without a \
                    stream sets up."


if __name__ == '__main__':
    print "a livestreamer/Gstreamer player for twitch"
