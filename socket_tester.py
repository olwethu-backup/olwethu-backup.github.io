import socket

import json



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
        print(f"{request=}")

        request_split = request.split('\r\n\r\n')

        print(f"{request_split=}")

        print("\n\n")

        for i in request_split:
            print(i)
            print("-----------------------------------------")

        block_string = request_split[1]

        print(f"{block_string=}")
        print("===========================")


        block_dict = json.loads(block_string)    


        print(f"{block_dict=}")
        print("===========================")



        response = f"HTTP/1.0 200 OK\n\nThank you for connecting!"
        client_connection.sendall(response.encode())

        client_connection.close()

        # break
    
    s.close()



def main():
    listener(port = 7000)

if __name__ == "__main__":
    main()
    