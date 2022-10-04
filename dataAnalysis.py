from os import listdir
from os.path import isfile, join
from sortedcontainers import SortedDict


mypath = "/Users/fuyingbo/Desktop/repos/results"
projects = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith(".csv")]
res = {}

for project in projects:
    dir = join(mypath, project)
    with open(dir, "r") as f:
        for line in f.readlines():
            entry = line.strip("\n").split(", ")
            entry = [int(x) for x in entry]
            if entry[0] not in res:
                res[entry[0]] = entry[1:]
            else:
                for i in range(3):
                    res[entry[0]][i] += entry[i+1]

res = SortedDict(res)
for k, v in res.items():
    # with open("/Users/fuyingbo/Desktop/repos/ER-total.csv", "a") as f1:
    #     print(f"{k}, {v[0]/v[1]}", file=f1)
    # with open("/Users/fuyingbo/Desktop/repos/dis-total.csv", "a") as f2:
    #     print(f"{k}, {v[2]}", file=f2)
    with open("/Users/fuyingbo/Desktop/repos/total.csv", "a") as f3:
        print(f"{k}, {v[0]}, {v[1]}, {v[2]}", file=f3)
