import requests

client_id = "81gaw82lvaj8sbbkrmkxfer26pfczcz"

		
headers = {'Accept' : 'application/vnd.twitchtv.v2+json', 'Client-ID': client_id}

api_root = "https://api.twitch.tv/kraken"

def get_games():
	res = make_request('https://api.twitch.tv/kraken/games/top')
	return res

def get_channels():
	pass

def search():
	pass

def following():
	pass


def make_request(link):
	print headers
	return requests.get(link, headers=headers)

#to get Oauth from user
# redirect to localhost and listen on localhost:port to get the key for the user ...

# passer le header Client-id : client_id
# et le header pour le MIME type : application/vnd.twitchtv[.version]+json


# headers = {'Accept': 'application/vnd.twitchtv[.version]+json', 'Client-id': 'hash' }

def main():
	print get_games().json()

if __name__=='__main__':
	main()