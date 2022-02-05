from django.http import HttpResponse
from paramiko import SSHClient, AutoAddPolicy
from django.shortcuts import render, redirect

# Create your views here.


def openFile(request):
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

    if request.GET.get("file", ""):

        # Get File content
        folder = request.GET.get("folder", "")
        file = folder + request.GET.get("file", "")
        command = "sudo cat {}".format(file)
        stdin, stdout, stderr = client.exec_command(command)
        stdin.write(passwordRequest)
        response_text = stdout.read().decode("utf8")
        client.close()
        return render(
            request,
            "openFile.html",
            {
                "content": response_text,
                "path": file,
                "folder": request.GET.get("folder", ""),
            },
        )

    # No File specified
    elif request.method == "POST":

        # Save file
        if request.POST.get("content", ""):
            command = 'echo "{}" > {}'.format(
                request.POST.get("content", ""), request.POST.get("path", "")
            )
            stdin, stdout, stderr = client.exec_command(command)
            stdin.write(passwordRequest)
            client.close()
            link = "http://sshide.de/filebrowser/?folder={}".format(
                request.POST.get("folder", "")
            )
            return redirect(link)
    else:
        return HttpResponse("error")
