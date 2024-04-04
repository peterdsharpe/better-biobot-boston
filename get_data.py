import bs4 as bs
import requests
import tabula
import tempfile
from pathlib import Path
import numpy as np

### Get the right link to the data
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

### Download the data and convert it to a DataFrame
with tempfile.TemporaryDirectory() as tmp:
    tmpdir = Path(tmp)
    with open(tmpdir / data_filename, "wb") as f:
        f.write(requests.get(data_url).content)

    df = tabula.read_pdf(
        f.name,
        pages='all',
        multiple_tables=False
    )[0]

# Clean data
import datetime

df["Sample Date"] = df["Sample Date"].apply(lambda s: datetime.datetime.strptime(s, '%m/%d/%Y'))

for col in df.columns:
    if col == "Sample Date":
        continue

    try:
        numeric = np.array(df[col].replace('ND', 'NaN'), dtype=float)
        df[col] = numeric
    except ValueError:
        pass

# Remove NaN rows at the end
df = df.loc[
     df.iloc[:, 1:].first_valid_index():
     df.iloc[:, 1:].last_valid_index()
     ]

# Partition the data
dates = df["Sample Date"].values.astype('datetime64[D]')
north = df["Northern\r(copies/mL)"].values
south = df["Southern\r(copies/mL)"].values
north_ci = (
    df["Northern\rLow Confidence\rInterval"].values,
    df["Northern\rHigh Confidence\rInterval"].values
)
south_ci = (
    df["Southern\rLow Confidence\rInterval"].values,
    df["Southern\rHigh Confidence\rInterval"].values
)

# Group the data
data = {
    "North": {
        "dates" : dates,
        "values": north,
        "ci"    : north_ci
    },
    "South": {
        "dates" : dates,
        "values": south,
        "ci"    : south_ci
    }
}
