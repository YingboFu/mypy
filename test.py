from mypy import api
from mypy import infer
from mypy import checker
from mypy import errors
from mypy import checkexpr
from mypy import fastparse
from sortedcontainers import SortedDict
from os import listdir
from os.path import isfile, join
import git
import os
import shutil

mypath = "/Users/fuyingbo/Desktop/Commit Pair Hash"
projects = [f for f in listdir(mypath) if isfile(join(mypath, f))]

for project in projects:
    print(f"Processing {project}")
    idx = project.find("---")
    owner = project[:idx]
    p = project[idx+3:-4]

    repo_dir = os.path.join("/Users/fuyingbo/Desktop/repos", p)
    if not os.path.exists(repo_dir):
        os.makedirs(repo_dir)

    github_url = f'https://github.com/{owner}/{p}'
    repo = git.Repo.clone_from(github_url, repo_dir)

    checkexpr.callExpMap = {}
    infer.typeIslands = []
    checker.related_variable_list = []
    fastparse.funcs = []
    errors.errorLoc = []

    # result = api.run(sys.argv[1:])
    # result = api.run(["/Users/fuyingbo/Desktop/testRepoForPythonTypes/main.py"])
    result = api.run(["--show-traceback", "--follow-imports", "silent", "--ignore-missing-imports",
                      "--check-untyped-defs", "--show-error-codes", f"/Users/fuyingbo/Desktop/repos/{p}"])

    # print(infer.typeIslands)
    # print(errors.errorCounter)

    print("Combining call exp")
    for (fileName, line, endLine), v in checkexpr.callExpMap.items():
        idx = []
        new_type_island = []
        for i in range(infer.typeIslands.__len__()):
            for c in infer.typeIslands[i]:
                if (c.file == fileName and c.line == line and c.end_line == endLine) or (c.fname == v):
                    if i not in idx:
                        idx.append(i)
                        break
        for i in idx:
            new_type_island.extend(infer.typeIslands[i])
        for i in reversed(idx):
            if i < infer.typeIslands.__len__():
                del infer.typeIslands[i]
        infer.typeIslands.append(new_type_island)

    print("Combining vars")
    for var_list in checker.related_variable_list:
        idx = []
        new_type_island = []
        for v in var_list:
            for i in range(infer.typeIslands.__len__()):
                for c in infer.typeIslands[i]:
                    if (v.line == c.line and v.end_line == c.end_line and v.column == c.column and v.end_column == c.end_column)\
                        or (v.line == c.line and v.name == c.var_name):
                        if i not in idx:
                            idx.append(i)
                            break
        for i in idx:
            new_type_island.extend(infer.typeIslands[i])
        for i in reversed(idx):
            if i < infer.typeIslands.__len__():
                del infer.typeIslands[i]
        infer.typeIslands.append(new_type_island)

    print("Combining funcs")
    for (fileName, line, endLine) in fastparse.funcs:
        idx = []
        new_type_island = []
        for i in range(infer.typeIslands.__len__()):
            for c in infer.typeIslands[i]:
                if c.file == fileName and line <= c.line <= endLine:
                    if i not in idx:
                        idx.append(i)
                        break
        for i in idx:
            new_type_island.extend(infer.typeIslands[i])
        for i in reversed(idx):
            if i < infer.typeIslands.__len__():
                del infer.typeIslands[i]
        infer.typeIslands.append(new_type_island)

    print("Calculating")
    errorCounter = {}
    for (file, line) in errors.errorLoc:
        for typeIsland in infer.typeIslands:
            for c in typeIsland:
                if c.file == file:
                    if c.end_line is not None:
                        if c.line <= line <= c.end_line:
                            if typeIsland.__len__() not in errorCounter:
                                errorCounter[typeIsland.__len__()] = 0
                            errorCounter[typeIsland.__len__()] = errorCounter[typeIsland.__len__()] + 1
                            break
                    else:
                        if c.line == line:
                            if typeIsland.__len__() not in errorCounter:
                                errorCounter[typeIsland.__len__()] = 0
                            errorCounter[typeIsland.__len__()] = errorCounter[typeIsland.__len__()] + 1
                            break

    lineCounter = {}
    for typeIsland in infer.typeIslands:
        test = []
        for c in typeIsland:
            if c.line != -1:
                if c.end_line is not None:
                    for i in range(c.line, c.end_line+1):
                        if [c.file, i] not in test:
                            test.append([c.file, i])
                else:
                    if [c.file, c.line] not in test:
                        test.append([c.file, c.line])
        if typeIsland.__len__() not in lineCounter:
            lineCounter[typeIsland.__len__()] = []
        if test.__len__() != 0:
            lineCounter[typeIsland.__len__()].append(test.__len__())

    typeIslandsCounter = {}
    res = {}
    for typeIsland in infer.typeIslands:
        if typeIsland.__len__() not in typeIslandsCounter:
            typeIslandsCounter[typeIsland.__len__()] = 0
        typeIslandsCounter[typeIsland.__len__()] = typeIslandsCounter[typeIsland.__len__()] + 1

    for len in SortedDict(typeIslandsCounter):
        if len in errorCounter and len in lineCounter:
            if lineCounter[len].__len__() != 0:
                # res[len] = errorCounter[len] / typeIslandsCounter[len] /
                # (sum(lineCounter[len])/lineCounter[len].__len__())
                # res[len] = errorCounter[len] / sum(lineCounter[len])
                with open(f"/Users/fuyingbo/Desktop/repos/results/{p}.csv", "a") as f:
                    print(f"{len}, {errorCounter[len]}, {sum(lineCounter[len])}, {typeIslandsCounter[len]}", file=f)
        else:
            res[len] = 0

    # with open("results/zulip/2e04cdbe5e7cdce6fa7064d946810255eccda33c-size.csv", "a") as f:
    #     for k, v in SortedDict(typeIslandsCounter).items():
    #         print(f"{k}, {v}", file=f)
    #
    # with open("results/zulip/2e04cdbe5e7cdce6fa7064d946810255eccda33c-ER.csv", "a") as f:
    #     for k, v in SortedDict(res).items():
    #         print(f"{k}, {v}", file=f)

    if result[0]:
        print('\nType checking report:\n')
        print(result[0])  # stdout

    if result[1]:
        print('\nError report:\n')
        print(result[1])  # stderr

    print('\nExit status:', result[2])
    shutil.rmtree(repo_dir)
