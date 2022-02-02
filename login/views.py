from django.shortcuts import render, redirect
from django.http import HttpResponse, request
import paramiko
from .models import login_parameters
from django.db.models import Max


def login(request):
    if request.method == "GET":
        error = " "
        if request.GET.get("error", "") == "true":
            error = "Check credentials"
        return render(request, "index.html", {"Error": error})
    elif request.method == "POST":

        if (
            not request.POST.get("server", "")
            or not request.POST.get("user", "")
            or not request.POST.get("port", "")
            or not request.POST.get("password", "")
        ):
            return redirect("http://sshide.de/?error=true")

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
            return redirect("http://sshide.de/?error=true")
        except paramiko.BadHostKeyException:
            return redirect("http://sshide.de/?error=true")
        except paramiko.SSHException:
            return redirect("http://sshide.de/?error=true")
        except paramiko.ssh_exception.NoValidConnectionsError:
            return redirect("http://sshide.de/?error=true")
        finally:
            client.close()

        return redirect("filebrowser/?folder=/")
