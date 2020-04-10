import asyncio
from asyncio import transports


class ServerProtocol(asyncio.Protocol):
    login: str = None
    server: 'Server'
    transport: transports.Transport

    def __init__(self, server: 'Server'):
        self.server = server

    def data_received(self, data: bytes):
        decoded = data.decode('utf-8')
        print(decoded.strip("\r\n"))

        if self.login is not None:
            self.send_message(decoded)
        else:
            if decoded.startswith("login:"):
                new_login = decoded.replace("login:", "").replace("\r\n", "").strip()
                if self.server.check_login(new_login):
                    self.transport.write(f"Login {new_login} already in use, try again...\n".encode())
                    self.transport.close()
                else:
                    self.login = new_login
                    self.transport.write(f"Hello, {self.login}!\n".encode())
                    self.send_history()

    def send_history(self):
        self.transport.write(''.join(self.server.history).encode())

    def connection_made(self, transport: transports.Transport):
        self.server.clients.append(self)
        self.transport = transport
        print("New client...")

    def connection_lost(self, exception):
        self.server.clients.remove(self)

        login = "Client" if (self.login is None) else self.login
        print(f"{login} leaved.")

    def send_message(self, content: str):
        message = f"[{self.login}]: {content}"
        self.server.message_history(message + "\n")

        for user in self.server.clients:
            user.transport.write(message.encode())


class Server:
    clients: list
    history: list

    def __init__(self):
        self.clients = []
        self.history = []

    def build_protocol(self):
        return ServerProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.build_protocol,
            "127.0.0.1",
            8000
        )

        print("Server started...")

        await coroutine.serve_forever()

    def check_login(self, new_login: str):
        for client in self.clients:
            if client.login == new_login:
                return True
        return False

    def message_history(self, message: str):
        self.history.append(message)
        self.history = self.history[-10:]


process = Server()

try:
    asyncio.run(process.start()) 
except KeyboardInterrupt:
    print("The server was stopped manually.")
