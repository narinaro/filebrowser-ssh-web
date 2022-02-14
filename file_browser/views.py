from paramiko import SSHClient, AutoAddPolicy
from django.shortcuts import render
from .con_ssh import ConSSH as ssh

counter = 0
itemsZip = []
path = ""


def fileBrowser(request):

    global counter
    global itemsZip
    global path

    # when path is empty open root dir
    if request.GET.get("folder", "") == "":
        path = "/"
    else:
        path = request.GET.get("folder", "")

    # set connection credentials
    connection = ssh(
        request.session["server"],
        request.session["user"],
        request.session["port"],
        request.session["password"],
    )

    # set up ssh connection
    connection.connect()

    # get items an fill lists
    getItems(request, connection)

    # close connection
    connection.closeConn()

    return render(
        request,
        "fileBrowser.html",
        {
            "itemsZip": itemsZip,
            "counter": counter,
            # Current Path
            "path": path,
            # IP
            "IP": connection.server,
        },
    )


def getItems(request, connection):

    global itemsZip
    global counter
    global path

    # get files and folders of path
    command = f"ls -p {path}"
    answer = connection.commandExec(command)

    items = []
    items = answer.splitlines()

    folderFlag = []
    idCounter = []
    counter = 0

    for i in items:
        if i[-1] == "/":
            folderFlag.append("1")
        else:
            folderFlag.append("0")
        # This is used in JS to map paths to ID's
        idCounter.append(counter)
        counter += 1

    itemsZip = list(zip(items, folderFlag, idCounter))
