import os

os.system("pip install django")
os.system("pip install paramiko")
os.system("python manage.py migrate")
os.system("python manage.py runserver 0:8080")