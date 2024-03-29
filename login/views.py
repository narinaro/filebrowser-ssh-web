from django.shortcuts import render, redirect
import paramiko
from django.http import HttpResponse
import os


def login(request):

    if request.method != "POST" and request.method != "GET":
        return HttpResponse("Error")

    if request.method == "GET":
        error = " "
        if request.GET.get("error", "") == "true":
            error = "Check credentials"
        return render(request, "index.html", {"Error": error, "URL": request._current_scheme_host,})
    elif request.method == "POST":

        if (
            not request.POST.get("server", "")
            or not request.POST.get("user", "")
            or not request.POST.get("port", "")
            or not request.POST.get("password", "")
        ):
            return redirect(f"http://{request._current_scheme_host}/?error=true")

        try:

            serverRequest = request.POST.get("server", "")
            userRequest = request.POST.get("user", "")
            portRequest = request.POST.get("port", "")
            passwordRequest = request.POST.get("password", "")

            client = paramiko.SSHClient()

            request.session["server"] = request.POST.get("server", "")
            request.session["user"] = request.POST.get("user", "")
            request.session["password"] = request.POST.get("password", "")
            request.session["port"] = request.POST.get("port", "")

            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            client.connect(
                serverRequest,
                username=userRequest,
                port=portRequest,
                password=passwordRequest,
            )

        except paramiko.AuthenticationException:
            return redirect(f"http://{request._current_scheme_host}/?error=true")
        except paramiko.BadHostKeyException:
            return redirect(f"http://{request._current_scheme_host}/?error=true")
        except paramiko.SSHException:
            return redirect(f"http://{request._current_scheme_host}/?error=true")
        except paramiko.ssh_exception.NoValidConnectionsError:
            return redirect(f"http://{request._current_scheme_host}/?error=true")
        finally:
            client.close()

        return redirect("filebrowser/?folder=/")
