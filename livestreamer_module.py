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

        # stream online ?
        if not self.streams_dict:
            print "Streams is offline"
            return 0

        return 1

        # stream online

    def set_quality(self, quality):
        # set a stream quality
        self.quality = quality

    def get_stream_qualities(self):
        # return dict() of available stream quality
        return self.streams_dict.keys()

    def change_stream_quality(self, quality):
        # switch stream quality
        self.select_stream_quality(quality)
        self.stream_media = self.streams_dict[self.quality]

    def get_stream_file(self):
        # get the specific media file for selected quality
        try:
            return self.streams_dict[self.quality]
        except:
            print "Stream.get_stream_file: Shouldnt be called without a stream sets up."


if __name__ == '__main__':
    print "a livestreamer player for twitch"
