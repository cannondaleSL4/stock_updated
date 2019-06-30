from bs4 import BeautifulSoup


def rewrite():
    quotes_file = open("./quotes.txt", 'r')
    quotes = quotes_file.read()
    parsed_html = BeautifulSoup(quotes)

    for tag in parsed_html.find_all("li", recursive=True):
        print("'{}':{}".format(tag.text, tag.contents[0].get("value")))


if __name__ == "__main__":
    rewrite()