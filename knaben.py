# VERSION: 1.2
# AUTHORS: HorizonCode

import json
from sys import stderr
from http.client import HTTPSConnection
from urllib.parse import unquote, urlparse, urlencode
from novaprinter import prettyPrinter


class knaben(object):
    url = "https://knaben.eu"
    name = "Knaben Database"
    supported_categories = {
        "all": "",
        "anime": [6000000, 6001000, 6002000, 6003000, 6004000, 6005000, 6006000, 6007000, 6008000],
        "books": [9000000, 9001000, 9002000, 9003000, 9004000, 9005000],
        "games": [4000000, 4001000],
        "movies": [3000000, 3001000, 3002000, 3003000, 3004000, 3005000, 3006000, 3007000, 3008000],
        "music": [1000000, 1001000, 1002000, 1003000, 1004000, 1005000, 1006000],
        "software": [4002000, 4003000, 4004000],
        "tv": [2000000, 2001000, 2002000, 2003000, 2004000, 2005000, 2006000, 2007000, 2008000]
        }

    def search(self, what, cat):
        what = unquote(what)

        search_url = "https://api.knaben.eu/v1"
        body = {
            "search_field": "title",
            "query": what,
            "order_by": "seeders",
            "order_direction": "desc",
            "from": 0,
            "size": 300,
            "hide_unsafe": True,
            "hide_xxx": False,
        }

        if cat and cat != "all":
            body["categories"] = self.supported_categories[cat]

        status, reason, response = self.request(search_url, body)

        if status < 200 or status > 299:
            print(reason, file=stderr)

        response_json = json.loads(response)

        for torrent in response_json["hits"]:
            result = {
                "link": torrent["link"] if "link" in torrent else torrent["magnetUrl"],
                "name": torrent["title"],
                "size": self.bytes_to_human_readable(torrent["bytes"]),
                "seeds": torrent["seeders"],
                "leech": torrent["peers"],
                "engine_url": "{engine}({origin})".format(engine = self.name, origin = torrent["cachedOrigin"]),
                "desc_link": torrent["details"] if "details" in torrent else "",
            }
            prettyPrinter(result)

    def request(self, url, data, headers=None):
        try:
            # Parse the URL
            parsed_url = urlparse(url)
            conn = HTTPSConnection(parsed_url.netloc)
            # Set default headers if none are provided
            if headers is None:
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "knaben-searchplugin"
                }
            # Make the POST request
            conn.request("POST", parsed_url.path, json.dumps(data), headers)
            # Get the response
            response = conn.getresponse()
            response_data = response.read()

            conn.close()
            return response.status, response.reason, response_data
        except Exception as e: print(e)

    def bytes_to_human_readable(self, byte_value):
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        size = byte_value
        unit_index = 0

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        return f"{size:.1f} {units[unit_index]}"
