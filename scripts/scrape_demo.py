import requests
from bs4 import BeautifulSoup

URL = "https://fr.wikipedia.org/wiki/Le_Mans"
USER_AGENT = "ENSIM-BI-course-TD (educational, contact your-email@univ-lemans.fr)"

def robots_allows(url, user_agent="*"):
    # Minimal, real check -- confirmed by hand against fr.wikipedia.org/robots.txt
    # before writing this: /wiki/<Article> is allowed for User-agent: *, only
    # /wiki/Special:... and a few other prefixes are disallowed.
    #
    # rp.read() uses urllib under the hood, which respects HTTP_PROXY/HTTPS_PROXY --
    # on a network with an institutional proxy (this one included), that silently
    # intercepts the request and robotparser then defaults to "disallow everything"
    # with no visible error. Confirmed by real testing: rp.read() returned False for
    # a URL manually verified as allowed. Fetching the text with requests (already
    # proxy-bypassed everywhere else in this course) and handing it to rp.parse()
    # instead avoids the same silent-failure trap.
    import urllib.robotparser
    resp = requests.get("https://fr.wikipedia.org/robots.txt",
                         proxies={"http": None, "https": None},
                         headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(resp.text.splitlines())
    return rp.can_fetch(user_agent, url)

def main():
    allowed = robots_allows(URL)
    print(f"robots.txt allows fetching {URL}: {allowed}")
    if not allowed:
        raise SystemExit("robots.txt disallows this -- stopping, not scraping anyway.")

    resp = requests.get(URL, proxies={"http": None, "https": None},
                         headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title = soup.find("h1").get_text(strip=True)

    first_para = None
    for p in soup.find_all("p"):
        # A first, naive version of this loop (just "length > 40") grabbed a
        # disambiguation notice ("Pour les articles homonymes...") instead of real
        # article text -- confirmed on a live fetch. Wikipedia marks these notices
        # with a "hatnote" class on an ancestor, a well-known real convention;
        # skipping any <p> nested inside one is the actual fix, not a longer length
        # threshold (a short real sentence exists too, and a long hatnote could too).
        if p.find_parent(class_="hatnote"):
            continue
        text = p.get_text(strip=True)
        if len(text) > 40:
            first_para = text
            break

    print(f"\nPage title: {title}")
    print(f"First real paragraph ({len(first_para)} chars): {first_para[:200]}...")

    # One measurable variable extracted from unstructured HTML: population from the
    # infobox, found by label text rather than a fragile fixed CSS position.
    population = None
    for row in soup.select("table.infobox_v2 tr, table.infobox tr"):
        header = row.find("th")
        if header and "population" in header.get_text(strip=True).lower():
            cell = row.find("td")
            if cell:
                population = cell.get_text(" ", strip=True)
                break
    print(f"Extracted population field (unstructured -> one variable): {population!r}")

if __name__ == "__main__":
    main()
