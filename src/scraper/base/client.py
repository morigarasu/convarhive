import requests


def fetch_html(url: str) -> str:
    if url == "test":
        with open("index.html", "r") as file:
            return file.read()
    else:
        res = requests.get(url)
        if res.status_code == 200:
            return res.text


if __name__ == "__main__":
    print(fetch_html("test"))
