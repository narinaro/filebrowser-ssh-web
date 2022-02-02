from django.http import HttpResponse, StreamingHttpResponse
import paramiko
from login.models import login_parameters
from django.shortcuts import render, redirect
from .forms import UploadFileForm
from django.core.files.storage import FileSystemStorage
from wsgiref.util import FileWrapper
import mimetypes
import os

client = paramiko.SSHClient()
serverRequest = ""
userRequest = ""
portRequest = ""
passwordRequest = ""


def options(request):

    global client
    global serverRequest
    global userRequest
    global portRequest
    global passwordRequest

    # Get Login Credentials (Session Variable)
    serverRequest = request.session["server"]
    userRequest = request.session["user"]
    portRequest = request.session["port"]
    passwordRequest = request.session["password"]
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(
        serverRequest, username=userRequest, port=portRequest, password=passwordRequest
    )

    if request.POST.get("delete", "") == "1":
        deleteElement(request)
    elif request.POST.get("create", "") == "1":
        createElement(request)
    elif request.POST.get("upload", "") == "1":
        uploadHandling(request)
    elif request.POST.get("rename", "") == "1":
        renameElement(request)
    elif request.POST.get("exec", "") == "1":
        execCommand(request)
    elif request.POST.get("download", "") == "1":
        response = downloadHandling(request)
        if response:
            return response

    client.close()
    link = "http://sshide.de/filebrowser/?folder={}".format(
        request.POST.get("path", "")
    )

    return redirect(link)


def downloadHandling(request):

    global client
    global serverRequest
    global userRequest
    global portRequest
    global passwordRequest

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
            command = "cd {} && zip -r files.zip{}".format(
                request.POST.get("path"), elementString
            )
            stdin, stdout, stderr = client.exec_command(command)
            elements[0] = "files.zip"

        ftp_client = client.open_sftp()
        localPath = "/home/sftp_web_project/sftp_web/media/{}".format(elements[0])
        remotePath = "{}{}".format(request.POST.get("path"), elements[0])
        ftp_client.get(remotePath, localPath)
        ftp_client.close()
        if len(elements) > 1 or folderFlag == 1:
            client.exec_command(
                "cd {} && rm files.zip".format(request.POST.get("path", ""))
            )
        response = StreamingHttpResponse(
            FileWrapper(open(localPath, "rb"), 8192),
            content_type=mimetypes.guess_type(localPath)[0],
        )
        response["Content-Length"] = os.path.getsize(localPath)
        response["Content-Disposition"] = "Attachment;filename={}".format(elements[0])
        os.remove(localPath)
        return response


def uploadHandling(request):
    global client

    uploadedFiles = request.FILES.getlist("document")
    for file in uploadedFiles:
        fs = FileSystemStorage()
        file.name = file.name.replace("/", "")
        file.name = file.name.replace(" ", "")
        file.name = file.name.replace("\\", "")
        file.name = file.name.replace("(", "")
        file.name = file.name.replace(")", "")
        fs.save(file.name, file)
        ftp_client = client.open_sftp()
        localPath = "/home/sftp_web_project/sftp_web/media/{}".format(file.name)
        remotePath = "{}{}".format(request.POST.get("path", ""), file.name)
        ftp_client.put(localPath, remotePath)
        ftp_client.close()
        os.remove(localPath)


def createElement(request):
    global client

    if request.POST.get("newFile", ""):
        fileName = request.POST.get("newFile", "")
        command = "touch {}{}".format(request.POST.get("path", ""), fileName)
        stdin, stdout, stderr = client.exec_command(command)
    else:
        folderName = request.POST.get("newFolder", "")
        command = "mkdir {}{}".format(request.POST.get("path", ""), folderName)
        stdin, stdout, stderr = client.exec_command(command)


def deleteElement(request):
    global client

    for i in request.POST:
        if request.POST[i] == "1element":
            if i[-1] != "/":
                command = f"cd {request.POST.get('path', '')} && rm {i}"
                stdin, stdout, stderr = client.exec_command(command)
            else:
                command = f"cd {request.POST.get('path', '')} && rm -r {i}"
                stdin, stdout, stderr = client.exec_command(command)


def renameElement(request):
    global client

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
        stdin, stdout, stderr = client.exec_command(command)


def execCommand(request):
    global client

    if request.POST.get("command", ""):
        command = "cd {} && {}".format(
            request.POST.get("path", ""), request.POST.get("command", "")
        )
        stdin, stdout, stderr = client.exec_command(command)
