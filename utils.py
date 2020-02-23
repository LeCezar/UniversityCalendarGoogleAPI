import json

mandatoryCourses = ["Verificarea si validarea sistemelor soft", "Calcul numeric", "Elaborarea lucrarii de licenta"]

ACTION_MAKE = 1
ACTION_DELETE = 2


def readJson(filename):
    with open(filename, "rb") as file:
        return json.load(file)


def addGroupsToBasicJson(initialJson):
    group = "931"
    finalJson = {
        group: {
            group + '/1': [],
            group + '/2': [],
        }
    }

    for entry in initialJson:

        if (entry["Ziua"] == "Ziua"):

            group = str(int(group) + 1)
            finalJson[group] = {
                str(group) + '/1': [],
                str(group) + '/2': [],
            }
        else:
            if (entry['Formatia'] == group + "/1"):
                finalJson[group][group + "/1"].append(entry)
            elif (entry['Formatia'] == group + "/2"):
                finalJson[group][group + "/2"].append(entry)
            else:
                finalJson[group][group + "/1"].append(entry)
                finalJson[group][group + "/2"].append(entry)
    return finalJson


def generateListOfOptinalCourses(initialJson):
    optionalList = []
    for entry in initialJson:
        if (entry['Disciplina'] not in mandatoryCourses and entry['Disciplina'] not in optionalList and entry[
            'Disciplina'] != 'Disciplina'):
            optionalList.append(entry['Disciplina'])
    return optionalList


print(addGroupsToBasicJson(readJson("toConvert.json")))
