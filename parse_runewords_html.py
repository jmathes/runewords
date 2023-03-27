from pprint import pprint
import json
from html.parser import HTMLParser

class RuneWordParser(HTMLParser):
    def __init__(self):
        self.words = []
        self.current_word = None
        super().__init__()
        self.tagstack = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "tr":
            self.current_word = {}
        if tag not in ("br",):
            self.tagstack.append(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "tr":
            pprint(self.current_word)
            self.words.append(self.current_word)
            self.current_word = None
        last_tag = self.tagstack.pop()
        assert last_tag == tag, (f"Closing {tag} doesn't match last tag, {last_tag}, during {self.current_word}")

    def handle_data(self, data):
        if not data.strip():
            return
        if self.current_word is not None:
            if "name" not in self.current_word:
                self.current_word["name"] = data
            elif "equipment" not in self.current_word:
                print(data)
                self.current_word["equipment"] = data.strip().split("Socket")[1].strip()
            elif "recipe" not in self.current_word:
                self.current_word["recipe"] = data.strip().split(" + ")
            else:
                self.current_word["effects"] = data.strip().split(";")

parser = RuneWordParser()

with open("runewords-original.html", "r") as wordfile:
    parser.feed("".join(wordfile.readlines()))

with open("runewords-110.html", "r") as wordfile:
    parser.feed("".join(wordfile.readlines()))

with open("runewords-111.html", "r") as wordfile:
    parser.feed("".join(wordfile.readlines()))

pprint(parser.words)


with open("runewords.json", "w") as runewords_json:
    json.dump(parser.words, runewords_json)    