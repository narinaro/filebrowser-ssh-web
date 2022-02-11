import paramiko


class ConSSH:
    def __init__(self, server, user, port, password):
        self.client = paramiko.SSHClient()
        self.server = server
        self.user = user
        self.port = port
        self.password = password
        self.answer = ""

    def connect(self):
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            self.server, username=self.user, port=self.port, password=self.password
        )

    def commandExec(self, command):
        command = f"{command}"
        stdin, stdout, stderr = self.client.exec_command(command)
        self.answer = stdout.read().decode("utf8")

        return self.answer

    def closeConn(self):
        self.client.close()
