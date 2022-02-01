from django.http import HttpResponse
from paramiko import SSHClient, AutoAddPolicy
from login.models import login_parameters
from django.shortcuts import render, redirect

responseFolderPathsArray = []
responseFilesArray = []
responseFoldersArray = []
responseFoldersAndPaths = []
responseFilesWithCounter = []
responseFile = []
fileQuantity = []
folderQuantity = []
serverRequest = ""


def fileBrowser(request):

    global responseFoldersAndPaths
    global responseFilesWithCounter
    global responseFile
    global fileQuantity
    global folderQuantity

    # Connect to SSH and save response
    connectSSH(request)

    # Map response to arrays -> will be passed to template
    mapFilesFolders()

    return render(
        request,
        "fileBrowser.html",
        {
            # Folder names + paths + counter
            "responseFoldersAndPaths": responseFoldersAndPaths,
            # If more than on file -> file names and counter
            "responseFilesWithCounter": responseFilesWithCounter,
            # Only one file -> file name
            "responseFile": responseFilesArray,
            # Quantities
            "fileQuantity": fileQuantity,
            "folderQuantity": folderQuantity,
            # Current Path
            "path": request.GET.get("folder", ""),
            # IP
            "IP": serverRequest,
        },
    )


def mapFilesFolders():

    global responseFolderPathsArray
    global responseFilesArray
    global responseFoldersArray
    global responseFoldersAndPaths
    global responseFilesWithCounter
    global responseFile
    global fileQuantity
    global folderQuantity
    global path

    # Remove "/" from folder name
    j = 0

    for i in responseFoldersArray:
        responseFoldersArray[j] = i[:-1]
        j += 1

    # Get length of Array and pass it to template
    fileQuantity = len(responseFilesArray)
    fileIndex = len(responseFilesArray) + 3000

    # If only more than one file was found -> zip together file names with a counter (Used as ID in HTML)
    if fileIndex > 1:
        fileQuantityArray = list(range(3001, fileIndex + 1))
        # Zip together so that we can iterate through two Arrays at the same time
        responseFilesWithCounter = list(zip(fileQuantityArray, responseFilesArray))

    # Get length of Array and pass it to template
    folderQuantity = len(responseFoldersArray)

    if folderQuantity < 2:
        responseFoldersAndPaths = list(
            zip(responseFolderPathsArray, responseFoldersArray)
        )
    else:
        folderQuantityArray = list(range(1, folderQuantity + 1))
        # Zip together so that we can iterate through three Arrays at the same time
        responseFoldersAndPaths = list(
            zip(folderQuantityArray, responseFolderPathsArray, responseFoldersArray)
        )


def connectSSH(request):
    global responseFolderPathsArray
    global responseFilesArray
    global responseFoldersArray
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

    # Folder specified
    if request.GET.get("folder", ""):

        # Get path of folders
        command = 'cd {} && ls -d -1 "$PWD/"**/'.format(request.GET.get("folder", ""))
        stdin, stdout, stderr = client.exec_command(command)
        stdin.write(passwordRequest)
        responseFolderPaths = stdout.read().decode("utf8")

        # Get folders
        command = "cd {} && ls -d */".format(request.GET.get("folder", ""))
        stdin, stdout, stderr = client.exec_command(command)
        stdin.write(passwordRequest)
        responseFolders = stdout.read().decode("utf8")

        # Get files
        command = "cd {} && (ls -p | grep -v /)".format(request.GET.get("folder", ""))
        stdin, stdout, stderr = client.exec_command(command)
        stdin.write(passwordRequest)
        responseFiles = stdout.read().decode("utf8")
    # No Folder specified -> Show /
    else:

        # Get paths of folders
        stdin, stdout, stderr = client.exec_command('cd / && ls -d -1 "$PWD"**/')
        stdin.write(passwordRequest)
        responseFolderPaths = stdout.read().decode("utf8")

        # Get folders
        stdin, stdout, stderr = client.exec_command("cd / && ls -d */")
        stdin.write(passwordRequest)
        responseFolders = stdout.read().decode("utf8")

        # Get files
        stdin, stdout, stderr = client.exec_command("cd / && (ls -p | grep -v /)")
        stdin.write(passwordRequest)
        responseFiles = stdout.read().decode("utf8")

    # Split response strings into Arrays
    responseFolderPathsArray = responseFolderPaths.split()
    responseFilesArray = responseFiles.split()
    responseFoldersArray = responseFolders.split()

    for i in range(len(responseFolderPathsArray)):
        if len(responseFolderPathsArray) > 1:
            while responseFolderPathsArray[i][1] == "/":
                responseFolderPathsArray[i] = responseFolderPathsArray[i][1:]

    for i in range(len(responseFoldersArray)):
        if len(responseFoldersArray) > 1:
            while responseFoldersArray[i][1] == "/":
                responseFoldersArray[i] = responseFoldersArray[i][1:]

    client.close()


def conSshAndMap(request):

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
