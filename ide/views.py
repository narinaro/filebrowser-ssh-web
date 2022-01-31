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

    return render(request, 'ide.html',
                      {
                      # Items with path and openFlag 
                       'itemZip':                  itemZip,
                       'quantity':                 quantity

                       })

def connectSSH(request):

    global itemZip
    global baseZip
    global pathBase
    global quantity

# Get login credentials (session variable)
    serverRequest   = request.session['server']
    userRequest     = request.session['user']
    portRequest     = request.session['port']
    passwordRequest = request.session['password']
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(
            serverRequest,
            username = userRequest,
            port     = portRequest,
            password = passwordRequest
        )
    
# Get list of subfiles and subfolders
    getParameter = request.GET.get('folder','')
    if getParameter[-1] == "/":
        getParameter = getParameter[:-1]
    lastOcc = getParameter.rfind("/") 
    getPath = getParameter[:lastOcc + 1]
    getFolder = getParameter[lastOcc + 1:]

    command = "cd {} && ls -pR {} | awk '{}' ".format(getPath, getFolder, '!NF{$0=";"}1')
    stdin, stdout, stderr = client.exec_command(command)
    answer = stdout.read().decode("utf8")
    array = answer.split(';')
    
    response = []

    for i in array:
        response.append(i.splitlines())

    items = []
    itemNames = []
    itemsWithPath = []
    folderFlag = []
    baseDir = []
    skip = 0
    idCounter = []
    counter = 0
    lastOcc = 0

    # Map items to list 
    for element in response:

        # Check if this is the first item -> Base Dir or not
        if skip == 1:

            # First item of element is empty, second is folder/path
            path = element[1]

            # Iterate through items of response element
            # Begin at 2 to skip folder/path
            for j in range(2, len(element)):

                # String together item and its path
                curr = path + element[j] 
                items.append(curr)

                # This is used in JS to map paths to ID's
                idCounter.append(counter)
                counter += 1    

                # This is not a base item
                baseDir.append("0")
        else:

            # These are the base items, there is no path, first is empty
            for j in range(1, len(element)):

                # Add items 
                curr = getFolder + ":" + element[j] 
                items.append(curr)

                # This is used in JS to map paths to ID's
                idCounter.append(counter)
                counter += 1    

                # This is a base item
                baseDir.append("1")
            skip = 1

    for i in items:
        if i[-1] == "/":
            folderFlag.append("1")
        else:
            folderFlag.append("0")
        lastOcc = i.rfind(":")
        itemsWithPath.append(i[:lastOcc] + "/")
        itemNames.append(i[lastOcc + 1:])
    

    quantity = len(itemNames)
    itemZip = list(zip(itemsWithPath, itemNames, folderFlag, idCounter, baseDir))

    #for i in range(len(responseFolderPathsArray)):
    #    while responseFolderPathsArray[i][1] == "/":
    #        responseFolderPathsArray[i] = responseFolderPathsArray[i][1:]
#
#    for i in range(len(responseFoldersArray)):
#        while responseFoldersArray[i][1] == "/":
#            responseFoldersArray[i] = responseFoldersArray[i][1:]

    client.close()

