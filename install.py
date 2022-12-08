import os

print("First you have to create a virtual enviroment for your python version to not mess up the system one.")
venv = input("You've already done that? (Y/n)")

if venv == "Y" or venv == "y":
    os.system("pip install django")
    os.system("pip install paramiko")
elif venv == "N" or venv == "n":
    print("If not already done install 'pythonvirtualenv' via pip install ... and then create a venv with 'virtualenv <name>'. Afterwards execute install.py again.")
else:
    print("Error")