from django.http import HttpResponse
from django.shortcuts import render, redirect
from file_browser.con_ssh import ConSSH as ssh


def openFile(request):

    if request.method != "POST" and request.method != "GET":
        return HttpResponse("Error")

    # set connection credentials
    connection = ssh(
        request.session["server"],
        request.session["user"],
        request.session["port"],
        request.session["password"],
    )

    # set up ssh connection
    connection.connect()

    if request.GET.get("file", ""):

        # Get File content
        folder = request.GET.get("folder", "")
        file = folder + request.GET.get("file", "")
        command = f"cat {file}"
        response_text = connection.commandExec(command)
        # close connection
        connection.closeConn()

        return render(
            request,
            "openFile.html",
            {
                "content": response_text,
                "path": file,
                "folder": request.GET.get("folder", ""),
                "URL": request._current_scheme_host,
            },
        )

    # No File specified
    elif request.method == "POST":

        # Save file
        command = 'echo -n "{}" > {}'.format(
            request.POST.get("content", ""), request.POST.get("path", "")
        )
        connection.commandExec(command)
        connection.client.close()
        link = f"http://{request._current_scheme_host}/filebrowser/?folder={request.POST.get('folder', '')}"
        # close connection
        connection.closeConn()

        return redirect(link)
    else:
        # close connection
        connection.closeConn()

        return HttpResponse("error")
