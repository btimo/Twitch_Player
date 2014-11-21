class Player():
	def __init__(self):
		pass

	def initGstreamer(self):
		# create pipeline
		self.pipeline = Gst.pipeline()

		# create bus and connect event
		self.bus = self.pipeline.get_bus()
		self.bus.add_signal_watch()
		self.bus.connect('message::eos', self.on_end_of_stream)
		self.bus.connect('message::error', self.on_error)

		# link pipeline output and gui frame
		self.bus.enable_sync_message_emission()
		self.bus.connect('sync-message::element', self.on_sync_message)

		# create playbin element
		
		# add playbin to pipeline

		# set property of pipeline for app source

		# set callback for playbin and source setup

	def on_sync_message(self, bus, msg):
		pass

	def on_source_setup(self, element, source):
		pass

	def on_source_need_data(self, source, length):
		pass

	def on_end_of_stream(self, bus, msg):
		pass

	def on_error(self, bus, msg):
		pass

	def on_stop(self):
		# set element state to null then
		# unref element
		pass

	def on_start(self):
		pass




if __name__ == '__main__':
	print "videoStream is a class implementing Gstreamer package to accomodate a Tkinter GUI and Livestreamer appsrc"