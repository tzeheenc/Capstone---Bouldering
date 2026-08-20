
import os
import io
import zipfile
import requests
import pandas as pd
import reverse_geocoder
import sys

url = "https://github.com/OpenBeta/climbing-data/raw/main/curated_datasets/Curated_OpenBetaAug2020_RytherAnderson.pkl.zip"
output_file = "boulders_2020_regions.csv"
needed_columns = ["climb", "sector", "region", "country",
                  "vgrade", "description", "desc_words"]

if len(sys.argv) > 1:
    data_file_name = sys.argv[1]
else:
    data_file_name = output_file

if os.path.exists(data_file_name):
    print("Using existing file:", data_file_name)
    df = pd.read_csv(data_file_name)

    missing = []
    for col in needed_columns:
        if col not in df.columns:
            missing.append(col)

    if len(missing) > 0:
        print("Problem: this file is missing these columns:", missing)
        print("It doesn't look like the boulder dataset - stopping.")
        raise SystemExit

    print("Loaded", len(df), "boulder problems")
    raise SystemExit

if len(sys.argv) > 1:
    print("Could not find a file called:", data_file_name)
    print("Check the name and try again.")
    raise SystemExit

print("No existing data file found - building it from scratch.")
response = requests.get(url)
zip_file = zipfile.ZipFile(io.BytesIO(response.content))
file_name = zip_file.namelist()[0]
data_file = zip_file.read(file_name)
df = pd.read_pickle(io.BytesIO(data_file))
print("Loaded", len(df), "climbs in total")

df = df[df["type_string"] == "boulder"]
print("Boulder problems:", len(df))

new_descriptions = []
for d in df["description"]:
    text = " ".join(d)
    new_descriptions.append(text.strip())
df["description"] = new_descriptions

word_counts = []
for text in df["description"]:
    words = text.split()
    word_counts.append(len(words))
df["desc_words"] = word_counts

coordinates = []
for location in df["parent_loc"]:
    longitude = location[0]
    latitude = location[1]
    coordinates.append((latitude, longitude))

print("Looking up states and countries...")
results = reverse_geocoder.search(coordinates)

country_codes = []
states = []
for r in results:
    country_codes.append(r["cc"])
    states.append(r["admin1"])
df["country"] = country_codes
df["state"] = states

region_list = []
for i in range(len(df)):
    if country_codes[i] == "US":
        region_list.append(states[i])
    elif country_codes[i] == "CA":
        region_list.append("Canada")
    elif country_codes[i] == "MX":
        region_list.append("Mexico")
    else:
        region_list.append(country_codes[i])
df["region"] = region_list

df = df[["route_name", "parent_sector", "region", "country",
         "Vermin", "description", "desc_words"]]
df.columns = ["climb", "sector", "region", "country",
              "vgrade", "description", "desc_words"]

df.to_csv(output_file, index=False)
print("Saved to", output_file)

has_description = df[df["desc_words"] > 0]
percent = 100 * len(has_description) / len(df)
print("Problems with a description:", round(percent), "%")
print("Median description length:", has_description["desc_words"].median(), "words")
print()
print("Problems per region (top 10):")
print(df["region"].value_counts().head(10))