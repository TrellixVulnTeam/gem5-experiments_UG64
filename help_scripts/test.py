import re


def inputGetter():
    with open("handler_inputs.txt") as file:
        lines = []
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]

        firstOfList = next(i for i, element in enumerate(lines[1:]) if re.match("--", element))
        print(firstOfList)
        for i in range(len(lines) - firstOfList - 1):
            lines.pop()
        return lines

a = inputGetter()
print(a)
