import socket



def listener(port):

    print(f"{port=}")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Socket successfully created")

    s.bind(("", port))

    print(f"socket bound to {port}")

    s.listen(5)

    print("socket is listening")

    while True:
        client_connection, client_address = s.accept()
        
        print(f"Got connection from {client_address}")

        request = client_connection.recv(1024).decode()
        print(request)

        response = "HTTP/1.0 200 OK\n\nThank you for connecting!"
        client_connection.sendall(response.encode())

        client_connection.close()

        break
    
    s.close()



def main():
    listener(port = 7000)

if __name__ == "__main__":
    main()
    