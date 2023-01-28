from tabula import read_pdf
import pandas as pd
import re
import os

path = "./chen_approvals"

pattern = re.compile("^(\*[0-9]+ published peer\-)|(\**[0-9]+ peer\-)|(\*[0-9]+ book)|(\*[0-9]+ conference)|(\*[0-9]+ (publications|scientific|journal))|(\* [0-9]+ peer\-)")
def ifStartCell(s):
    return pattern.match(s) is not None

def getCredentials(s, credential_pattern):
    m = credential_pattern.search(s)
    if not m:
        return ""
    return m[0].strip().strip('*')

paper_pattern = re.compile("(\*[0-9,]+ (publications|scientific|journal))|(\*[0-9,]+ published peer\-)|(\**[0-9]+ peer\-)[a-zA-Z0-9 ]+( |\*)")
def getPaper(s):
    return getCredentials(s, paper_pattern)
citation_pattern = re.compile("(\*[0-9,]+ citations)[a-zA-Z0-9 ]+( \*)")
def getCitation(s):
    return getCredentials(s, citation_pattern)
peer_pattern = re.compile("(\*[0-9,]+ (review|peer review))[a-zA-Z0-9 ]+( \*)")
def getPeer(s):
    return getCredentials(s, peer_pattern)
grant_pattern = re.compile("(\*[0-9,]+ grant)[a-zA-Z0-9 ]+( \*)")
def getGrant(s):
    return getCredentials(s, grant_pattern)
year_pattern = re.compile("(\*(y|Y)ear of)([a-zA-Z0-9]| |\:|\-)+")
def getYear(s):
    return getCredentials(s, year_pattern)


all_header = [
    'Category',
    'Service Center',
    'Premium Processing',
    'Filling Date',
    'Approval Date',
    'Position at the time of filing',
    'Credentials',
    'Time',
    'Papers',
    'Citations',
    'Reviews',
    'Funding',
    'Last Paper',
]
all_df = pd.DataFrame.from_dict({})

def getDate(s):
    if "DS_Store" in s:
        return ()
    s = s.split()[2].split('.')
    return (int(s[0]), int(s[1]), int(s[2]))

for f in sorted(os.listdir(path), key=lambda x: getDate(x)):
    if "DS_Store" in f:
        continue
    filepath = path + '/' + f
    print(filepath)
    dfs = read_pdf(filepath, pages="all")
    for df in dfs:
        df = pd.concat([df.columns.to_frame().T, df], ignore_index=True).fillna('')
        df = df.iloc[:, 0:7]
        df.columns = range(len(df.columns))
        indices = [0] + df.index[df[6].apply(ifStartCell)].tolist() + [len(df)]
        all_samples = {col: [] for col in df.columns}
        for i in range(len(indices)-1):
            start = indices[i]
            end = indices[i+1]
            sub_df = df.iloc[start:end]
            for col in sub_df.columns:
                all_samples[col].append(' '.join(sub_df[col].tolist()).strip())
        df = pd.DataFrame.from_dict(all_samples)
        df = df[1:]
        df[2] = df[2].apply(lambda x: 'Y' if x == 'Y' else 'N')
        df[3] = df[3].str.split(' ').str[0]
        df[3] = pd.to_datetime(df[3],errors='coerce')
        df[4] = pd.to_datetime(df[4],errors='coerce')
        print(df)
        df[7] = (df[4] - df[3]).dt.days
        df[8] = df[6].apply(getPaper)
        df[9] = df[6].apply(getCitation)
        df[10] = df[6].apply(getPeer)
        df[11] = df[6].apply(getGrant)
        df[12] = df[6].apply(getYear)
        df.columns = all_header
        all_df = pd.concat([all_df, df])
# print(all_df)
all_df[[
    'Category',
    'Service Center',
    'Premium Processing',
    'Filling Date',
    'Approval Date',
    'Position at the time of filing',
    'Time',
    'Papers',
    'Citations',
    'Reviews',
    'Funding',
    'Last Paper',
]].to_csv("chen_approvals.csv", index=False)