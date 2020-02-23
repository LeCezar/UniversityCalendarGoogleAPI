from quickstart import makeCalendarEntries
from utils import *

SEMINARY_COLOR = '2'
LABORATORY_COLOR = '5'
COURSE_COLOR = '4'


def main():
    while (True):
        choice = int(
            input("1. Add university schedule. \n 2. Delete all entries added by this app. \n 0. Exit").strip())
        if (choice == 1):
            initialJson = readJson("toConvert.json")
            schedule = addGroupsToBasicJson(initialJson)
            optionalCoursesList = generateListOfOptinalCourses(initialJson)

            userGroup = inputGroup()
            userSubgroup = inputSubGroup()
            chosenOptionals = inputOptinals(optionalCoursesList)

            userCourses = chosenOptionals + mandatoryCourses
            print(userCourses)

            eventsRaw = []
            for entry in schedule[str(userGroup)][str(userGroup) + "/" + str(userSubgroup)]:
                if (entry['Disciplina'] in userCourses):
                    eventsRaw.append(entry)
            makeCalendarEntries(eventsRaw, ACTION_MAKE)

        elif (choice == 2):
            makeCalendarEntries([], ACTION_DELETE)
            print("Events deleted... Check Google Calendar to be sure")
        elif (choice == 0):
            break


def inputSubGroup():
    try:
        userSubGroup = int(input("What is your subgroup (1 or 2)").strip())
        while (userSubGroup > 2 or userSubGroup < 1):
            userSubGroup = input("Try again ... (1 or 2)").strip()
        return userSubGroup
    except:
        print("Your input was wrong ... ")
        inputSubGroup()


def inputGroup():
    try:

        userGroup = int(input("What is your group (number from 931 - 937)").strip())
        while (userGroup > 937 or userGroup < 931):
            userGroup = int(input("Try again ... (number from 931 - 937)").strip())
        return userGroup
    except:
        print("Your input was wrong ... ")
        inputSubGroup()


def inputOptinals(optionalCoursesList):
    optionalCoursesListSorted = list(sorted(optionalCoursesList))
    for i in range(0, len(optionalCoursesListSorted)):
        print(str(i) + " " + optionalCoursesListSorted[i])

    chosenOptionals = input("Chose what optionals you have (with \",\" in between like 1,3,4 etc.): ").strip().split(
        ",")
    chosenOptionals = [int(x.strip()) for x in chosenOptionals]
    optionalsList = []
    optinalsNotOK = True
    while (optinalsNotOK):
        try:
            for number in chosenOptionals:
                optionalsList.append(optionalCoursesListSorted[number])
            optinalsNotOK = False
        except:
            chosenOptionals = input(
                "You entered the optionals wrong... Should look like \"1,2,5\" etc: ").strip().split(",")

    return optionalsList


if __name__ == '__main__':
    main()
