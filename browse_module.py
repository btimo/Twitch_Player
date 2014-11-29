#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
# import json

client_id = "81gaw82lvaj8sbbkrmkxfer26pfczcz"

headers = {
    'Accept': 'application/vnd.twitchtv.v2+json',
    'Client-ID': client_id
    }

api_root = "https://api.twitch.tv/kraken"


# channel object

class Channel(object):
    def __init__(self, game, preview, mature, status, logo, url,
                 display_name, viewers, link):
        self.game = game
        # preview img
        self.preview = preview
        # mature content ?
        self.mature = mature
        # Steam description
        self.status = status
        self.logo = logo
        # for livestreamer ;)
        self.url = url
        self.display_name = display_name
        self.viewers = viewers
        # link in API to update viewers count, stream description and others.
        self.link = link


# game object
class Game(object):
    def __init__(self, name, pic_large, pic_small, pic_medium,
                 channels, viewers):
        self.name = name
        self.pic_large = pic_large
        self.pic_small = pic_small
        self.pic_medium = pic_medium
        self.channels = channels
        self.viewers = viewers

    def access_game_streams(self, offset=None):
        res = make_request(
            api_root + '/streams',
            {'game': self.name, 'limit': 25, 'offset': 0})

        channel_list = [Channel(elem['game'],
                                elem['preview'],
                                elem['channel']['mature'],
                                elem['channel']['status'],
                                elem['channel']['logo'],
                                elem['channel']['url'],
                                elem['channel']['display_name'],
                                elem['viewers'],
                                elem['_links']['self'])
                        for elem in res.json()['streams']]

        return channel_list, {'link': res.json()['_links']['next'],
                              'offset': 25 if offset is None else offset + 25}


def request_image(url):
    return requests.get(url).content


def search_request(string):
    res = make_request(api_root + '/search/streams', {'q': string})
    channel_list = [Channel(elem['game'],
                            elem['preview'],
                            elem['channel']['mature'],
                            elem['channel']['status'],
                            elem['channel']['logo'],
                            elem['channel']['url'],
                            elem['channel']['display_name'],
                            elem['viewers'],
                            elem['_links']['self'])
                    for elem in res.json()['streams']]

    return channel_list


def get_games(limit=25, offset=None):
    res = make_request(
        api_root+'/games/top',
        {'limit': limit, 'offset': offset})

    game_list = [Game(elem['game']['name'],
                      elem['game']['box']['large'],
                      elem['game']['box']['small'],
                      elem['game']['box']['medium'],
                      elem['channels'],
                      elem['viewers'])
                 for elem in res.json()['top']]

    next_url = {'link': res.json()['_links']['next'],
                'offset': 25 if offset is None else offset + 25}

    return game_list, next_url


def get_channels():
    pass


def search():
    pass


def following():
    pass


def make_request(link, params=None):
    return requests.get(link, headers=headers, params=params)

# to get Oauth from user
# redirect to localhost and listen on localhost:port to get the key for
# the user ...

# passer le header Client-id : client_id
# et le header pour le MIME type : application/vnd.twitchtv[.version]+json


# headers = {'Accept': 'application/vnd.twitchtv[.version]+json',
# 'Client-id': 'hash' }

def main():
    print search_request('summit1g').content

if __name__ == '__main__':
    main()
