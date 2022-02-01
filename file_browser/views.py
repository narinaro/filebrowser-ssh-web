from django.http import HttpResponse
from paramiko import SSHClient, AutoAddPolicy
from login.models import login_parameters
from django.shortcuts import render, redirect

serverRequest = ""
counter = 0
itemsZip = []


def fileBrowser(request):

    global serverRequest
    global counter
    global itemsZip

    # connect to server and get folders/files
    conSshAndMap(request)

    return render(
        request,
        "fileBrowser.html",
        {
            "itemsZip": itemsZip,
            "counter": counter,
            # Current Path
            "path": request.GET.get("folder", ""),
            # IP
            "IP": serverRequest,
        },
    )


def conSshAndMap(request):

    global itemsZip
    global counter
    global serverRequest

    client = SSHClient()

    # Get login credentials (session variable)
    serverRequest = request.session["server"]
    userRequest = request.session["user"]
    portRequest = request.session["port"]
    passwordRequest = request.session["password"]
    client.set_missing_host_key_policy(AutoAddPolicy())

    client.connect(
        serverRequest, username=userRequest, port=portRequest, password=passwordRequest
    )
    path = request.GET.get("folder", "")

    command = "ls -p {}".format(path)
    stdin, stdout, stderr = client.exec_command(command)
    answer = stdout.read().decode("utf8")

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

    client.close()
