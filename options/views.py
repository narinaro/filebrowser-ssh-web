from django.http import StreamingHttpResponse
import paramiko
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
from wsgiref.util import FileWrapper
import mimetypes
import os
from file_browser.con_ssh import ConSSH as ssh


def options(request):

    # set connection credentials
    connection = ssh(
        request.session["server"],
        request.session["user"],
        request.session["port"],
        request.session["password"],
    )

    # set up ssh connection
    connection.connect()

    if request.POST.get("delete", "") == "1":
        deleteElement(request, connection)
    elif request.POST.get("create", "") == "1":
        createElement(request, connection)
    elif request.POST.get("upload", "") == "1":
        uploadHandling(request, connection)
    elif request.POST.get("rename", "") == "1":
        renameElement(request, connection)
    elif request.POST.get("exec", "") == "1":
        execCommand(request, connection)
    elif request.POST.get("download", "") == "1":
        response = downloadHandling(request, connection)
        if response:
            return response

    # close connection
    connection.closeConn()

    link = "http://sshide.de/filebrowser/?folder={}".format(
        request.POST.get("path", "")
    )

    return redirect(link)


def downloadHandling(request, connection):

    elements = []
    elementString = ""
    folderFlag = 0

    for i in request.POST:
        if request.POST[i] == "1element":
            elements.append(i)
            if i[-1] == "/":
                folderFlag = 1

    if len(elements) > 0:
        if len(elements) > 1 or folderFlag == 1:
            for element in elements:
                if element[0] == "/":
                    elementString = elementString + " " + element[1:]
                else:
                    elementString = elementString + " " + element
            command = (
                f"cd {request.POST.get('path', '')} && zip -r files.zip{elementString}"
            )

            connection.commandExec(command)
            elements[0] = "files.zip"

        ftp_client = connection.client.open_sftp()
        localPath = "/home/sftp_web_project/sftp_web/media/{}".format(elements[0])
        remotePath = "{}{}".format(request.POST.get("path"), elements[0])
        ftp_client.get(remotePath, localPath)
        ftp_client.close()

        if len(elements) > 1 or folderFlag == 1:
            connection.commandExec(f"cd {request.POST.get('path', '')} && rm files.zip")

        response = StreamingHttpResponse(
            FileWrapper(open(localPath, "rb"), 8192),
            content_type=mimetypes.guess_type(localPath)[0],
        )

        response["Content-Length"] = os.path.getsize(localPath)
        response["Content-Disposition"] = f"Attachment;filename={elements[0]}"
        os.remove(localPath)

        return response


def uploadHandling(request, connection):

    uploadedFiles = request.FILES.getlist("document")
    for file in uploadedFiles:
        fs = FileSystemStorage()
        file.name = file.name.replace("/", "")
        file.name = file.name.replace(" ", "")
        file.name = file.name.replace("\\", "")
        file.name = file.name.replace("(", "")
        file.name = file.name.replace(")", "")
        fs.save(file.name, file)
        ftp_client = connection.client.open_sftp()
        localPath = f"/home/sftp_web_project/sftp_web/media/{file.name}"
        remotePath = "{request.POST.get('path', '')}{file.name}"
        ftp_client.put(localPath, remotePath)
        ftp_client.close()
        os.remove(localPath)


def createElement(request, connection):

    if request.POST.get("newFile", ""):
        fileName = request.POST.get("newFile", "")
        command = f"touch {request.POST.get('path', '')}{fileName}"
        connection.commandExec(command)
    else:
        folderName = request.POST.get("newFolder", "")
        command = f"mkdir {request.POST.get('path', '')}{folderName}"
        connection.commandExec(command)


def deleteElement(request, connection):

    for i in request.POST:
        if request.POST[i] == "1element":
            if i[-1] != "/":
                command = f"cd {request.POST.get('path', '')} && rm {i}"
                connection.commandExec(command)
            else:
                command = f"cd {request.POST.get('path', '')} && rm -r {i}"
                connection.commandExec(command)


def renameElement(request, connection):

    renameElement = []

    for i in request.POST:
        if request.POST[i] == "1element":
            renameElement.append(i)

    if len(renameElement) == 1:
        command = "mv {}{} {}{}".format(
            request.POST.get("path", ""),
            renameElement[0],
            request.POST.get("path", ""),
            request.POST.get("newName", ""),
        )
        connection.commandExec(command)


def execCommand(request, connection):

    if request.POST.get("command", ""):
        command = "cd {} && {}".format(
            request.POST.get("path", ""), request.POST.get("command", "")
        )
        connection.commandExec(command)
