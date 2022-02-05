from django.shortcuts import render, redirect
from django.http import HttpResponse, request
import paramiko
from django.db.models import Max

client = paramiko.SSHClient()

content = ""
itemZip = []
baseZip = []
pathBase = []
quantity = 0


def ide(request):

    global client
    global itemZip
    global quantity

    connectSSH(request)

    return render(
        request,
        "ide.html",
        {
            # Items with path and openFlag
            "itemZip": itemZip,
            "quantity": quantity,
        },
    )


def connectSSH(request):

    global itemZip
    global baseZip
    global pathBase
    global quantity

    # Get login credentials (session variable)
    serverRequest = request.session["server"]
    userRequest = request.session["user"]
    portRequest = request.session["port"]
    passwordRequest = request.session["password"]
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(
        serverRequest, username=userRequest, port=portRequest, password=passwordRequest
    )

    # Get list of subfiles and subfolders
    getParameter = request.GET.get("folder", "")
    if getParameter[-1] == "/":
        getParameter = getParameter[:-1]
    lastOcc = getParameter.rfind("/")
    getPath = getParameter[: lastOcc + 1]
    getFolder = getParameter[lastOcc + 1 :]
    curlyBrackets = "{}"
    insert = '"%s/\n" "$0"'

    command = f"cd {getPath} && find {getFolder} -type d -exec sh -c 'printf {insert}' {curlyBrackets} \; -or -print"
    stdin, stdout, stderr = client.exec_command(command)
    answer = stdout.read().decode("utf8")

    items = answer.splitlines()
    idCounter = []
    baseDir = []
    counter = 0
    itemNames = []
    folderFlag = []
    itemPaths = []

    items.pop(0)

    for i in items:
        if (i.count("/") == 2 and i[-1] == "/") or i.count("/") == 1:
            lastOcc = i[:-1].rfind("/")
            itemNames.append(i[lastOcc + 1 :])
            itemPaths.append(i[: lastOcc + 1])

            # This is used in JS to map paths to ID's
            idCounter.append(counter)
            counter += 1

            # This is a base item
            baseDir.append("1")

            # folder or not
            if i[-1] == "/":
                folderFlag.append("1")
            else:
                folderFlag.append("0")

        else:
            lastOcc = i[:-1].rfind("/")
            itemNames.append(i[lastOcc + 1 :])
            itemPaths.append(i[: lastOcc + 1])

            # This is used in JS to map paths to ID's
            idCounter.append(counter)
            counter += 1

            # This is a base item
            baseDir.append("0")

            # folder or not
            if i[-1] == "/":
                folderFlag.append("1")
            else:
                folderFlag.append("0")

    quantity = counter
    itemZip = list(zip(itemPaths, itemNames, folderFlag, idCounter, baseDir))
    client.close()
