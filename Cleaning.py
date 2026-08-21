import pandas as pd
 
df = pd.read_csv("boulders_2020_regions.csv")
grade_numbers = []
for grade in df["vgrade"]:
    if pd.isna(grade):
        grade_numbers.append(None)
        continue
    text = grade.strip() 
    text = text.replace("V", "")
    text = text.replace("+", "")
    parts = text.split("-")
    first = parts[0]
    if first.isdigit():
        grade_numbers.append(int(first))
    else:
        grade_numbers.append(None)

df["grade_num"] = grade_numbers
grade_numbers

before = len(df)
 
df = df[df["grade_num"].notna()]

before = len(df)
df = df[df["desc_words"] > 0]

df["grade_num"] = df["grade_num"].astype(int)

df.to_csv("boulders_clean.csv", index=False)
print("Saved", len(df), "rows to boulders_clean.csv")
print()
print("Problems per grade:")
print(df["grade_num"].value_counts().sort_index().to_string())