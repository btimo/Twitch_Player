from livestreamer import Livestreamer, NoPluginError, StreamError, PluginError



class Stream(object):
	def __init__(self):
		#open session.
		self.session = Livestreamer()

	def find_stream(self, link):
		# find stream from link
		try:
			self.streams_dict=self.session.streams(link)
		# stream exist ?
		except NoPluginError:
			print "Link error"

		if not self.streams_dict:
			print "Streams is offline"
		else:
			print self.streams_dict

		# stream online

	def select_stream_quality(self, quality):
		#choose a stream quality
		self.quality = quality

	def get_stream_quality(self):
		return self.streams_dict.keys()


	def change_stream_quality(self, quality):
		self.select_stream_quality(quality)
		self.stream_media = self.streams_dict[self.quality]

	def get_stream_file(self):
		try:
			return self.streams_dict[self.quality]
		except:
			"Shouldnt be called without a stream sets up"

def main():
	stream_object = Stream()
	stream_object.find_stream("http://twitch.tv/summit1g")


if __name__ == '__main__':
	main()
	# print "a livestreamer/Gstreamer player for twitch"
