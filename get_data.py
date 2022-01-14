import bs4 as bs
import requests
import tabula
import tempfile
from pathlib import Path

html = requests.get(
    url="https://www.mwra.com/biobot/biobotdata.htm", allow_redirects=True,
).text

soup = bs.BeautifulSoup(html, 'lxml')

links = soup.find_all('a', href=True)

data_link = None
for link in links:
    if link.text.strip().lower() == "click here":
        data_link = link
    else:
        continue

if data_link is None:
    raise ValueError("Could not find the link to the BioBot dataset.")

data_filename = data_link.attrs['href']

data_url = f"https://www.mwra.com/biobot/{data_filename}"

with tempfile.TemporaryDirectory() as tmp:
    tmpdir = Path(tmp)
    with open(tmpdir / data_filename, "wb") as f:
        f.write(requests.get(data_url).content)

    df = tabula.read_pdf(
        f.name,
        pages='all',
        multiple_tables=False
    )[0]
