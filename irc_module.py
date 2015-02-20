import sys

class IRC():
	def __init__(self, channel):
		pass

def main():
	pass

if __name__ == '__main__':
	if len(sys.argv) == 2:
		main()
	else:
		print "a irc class to handle irc chat from twitch"

# 1 - Client CONNECT : authenticate with server and pick channel
# 2 - Client JOIN : join the channel targeted (MODE may be available)
# chop/chanop : owner of the channel ('@') (KICK: eject client,
									# MODE: change channel mode,
									# INVITE: invite client in invite-only channel,
									# TOPIC : change channel topic)

# 510 characters for command and parameters allowed



