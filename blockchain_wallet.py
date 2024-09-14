# from blockchain import BlockChain
from uuid import uuid4
from flask import Flask, jsonify, request
import requests
import json
from hashlib import sha256


class Wallet:

    def __init__(self):

        # Generate a globally unique address for this node
        self.username = ""
        self.address = str(uuid4()).replace('-', '')
        
        self.available = 0  #immediately available balance
        self.pending = 0    # (can be positive or negative) an amount that is still wating to be confirmed in the form of a block on the blockchain (transaction that generated this balance still needs to be added to the chain)
        self.total = self.available + self.pending  #total balance
        self.nodes = set() #Set of nodes that can validate transactions
        self.port = -1
    
    def send(self, amount, address):
        #Creates a transaction that sends currency to a specific address.
        #The transaction will only be valid once it is on the chain as a block

        if amount >= self.available:
            transaction = {
                "sender": self.address,
                "recipient": address,
                "amount": amount 
            }

            self.pending = amount
            self.total = self.available - self.pending
            return jsonify(transaction)
        
        else:
            return f"Requested amount ({amount}) exceeds available balance ({address})."


#Instantiating a wallet with an API endpoint

app = Flask(__name__)

wallet = Wallet()

wallet_identifier = wallet.address


@app.route("/wallets/register", methods = ["POST"])
def register():
    """
        Receives a username and password (in JSON), will automatically generate an address for this account.
    """

    values = request.get_json()
    username = values.get("username")
    if ("password_encrypted" not in values) or values.get("password_encrypted") == "False":
        print(f"{values=}")
        password = sha256(values.get("password").encode()).hexdigest() #TODO: Encrypt this password
    else:
        password = values.get("password")
    


    
    port_file = open("port_counter.txt", "r")
    port_data = int(port_file.read())
    
   
    new_port = port_data + 2
    port_file = open("port_counter.txt", "w")
    port_file.write(str(new_port))
    port_file.close()





    wallet_info = {
        "username": username,
        "port": port_data,
        "password": password,
        "address": str(uuid4()).replace('-', ''),
        "available balance": 0,
        "pending balance": 0,
        "total balance": 0,
        "nodes": []



    }
    
    

    wallet_dict = json.load(open("wallets.json", "r"))

    if wallet_info['username'] in wallet_dict:
        return "Error: A wallet with this username already exists", 400
    
    wallet_dict[wallet_info['username']] = {"address": wallet_info['address'], "password": wallet_info['password'], "available balance": wallet_info["pending balance"], "pending balance": wallet_info["total balance"], "total balance": wallet_info["total balance"], "nodes": wallet_info["nodes"], "port": wallet_info["port"]}
    wallet_json = json.dumps(wallet_dict) #TODO: encrypt password (it's currently stored as plaintext)


    wallet_file = open("wallets.json", "w")

    wallet_file.write(wallet_json)

    wallet_file.close()

    response = {
        'message': f"Wallet '{wallet_info['username']}' created",
        'address': wallet_info['address']
    }

    return jsonify(response), 201



@app.route("/wallets/login", methods = ["GET"])
def login():

  #  print("-----1-----")
    # print(f"{request=}")
    # print(f"{request.__dict__}")
    # request.__dict__
    values = request

    #print(f"{type(values)=}")
    if values.query_string == b'':  #this means that the GET request is sending JSON instead of a query string
        values = request.get_json()
        username = values.get("username")
        password = sha256(values.get("password").encode()).hexdigest()
    
    else: #if it gets to this stage, it means that the request's content was not written in JSON
        #print("-------------------------handling exception")
        values = request.url.split("?")[1].split("&")
        # R = values.split("?")[1].split("&")
        # print(f"{R=}")
        username = values[0].split("=")[1]
        password = values[1].split("=")[1]

       # print(f"{username=}")
       # print(f"{password=}")
        
       

    #print("-----1.5-----")
    
    #print("-----2-----")
    wallet_dict = json.load(open("wallets.json", "r"))
    
    if username not in wallet_dict:
        #print(">>>")
        return "Error: Incorrect username or password", 400
    
    if wallet_dict[username]["password"] != password:
        #print("<<<")
        #print(f"{wallet_dict[username]["password"]=}")
        #print(f"{password=}")
        #print(f"{sha256(password.encode()).hexdigest()=}")
        return "Error: Incorrect username or password", 400
   
    wallet.username = username
    wallet.address = wallet_dict[username]["address"]
    wallet.available = wallet_dict[username]["available balance"]
    wallet.pending = wallet_dict[username]["pending balance"]
    wallet.total = wallet_dict[username]["total balance"]
    wallet.nodes = set(wallet_dict[username]["nodes"])

    #print("-----4-----")
    response = {"message": "Login successful",
                "details": {
                    "address": wallet_dict[username]["address"],
                    "available balance" : wallet_dict[username]["available balance"],
                    "pending balance" : wallet_dict[username]["pending balance"],
                    "total balance" : wallet_dict[username]["total balance"]
                }}
    #print("-----5-----")
    return jsonify(response), 200

# @app.route("/wallets/send", methods = ["GET"])
# def send():

@app.route("/wallets/register_node", methods = ["POST"])
def register_node():
    #registers a node that will propagate a transaction from a wallet to the rest of the network

    values = request.get_json()

    address = values.get("address")

    wallet.nodes.add(address)

    wallet_data = json.load(open("wallets.json", "r"))

    wallet_info = wallet_data[wallet.username]

    wallet_data[wallet.username]["nodes"] = list(wallet.nodes)

    wallet_file = open("wallets.json", "w")

    wallet_dump = json.dumps(wallet_data)

    wallet_file.write(wallet_dump)

    wallet_file.close()

    response = {"message": f"node '{address}' successfully registered"}

    return jsonify(response), 201















        
def login_offline():

  

  
    username = input("username: ")
    password = sha256(input("password: ").encode()).hexdigest()
    


    wallet_dict = json.load(open("wallets.json", "r"))
    
    if username not in wallet_dict:
        
        print("Error: Incorrect username or password")
        return -1
    
    if wallet_dict[username]["password"] != password:
   
        print("Error: Incorrect username or password")
        return -1

    wallet.username = username
    wallet.port = wallet_dict[username]["port"]
    wallet.address = wallet_dict[username]["address"]
    wallet.available = wallet_dict[username]["available balance"]
    wallet.pending = wallet_dict[username]["pending balance"]
    wallet.total = wallet_dict[username]["total balance"]
    wallet.nodes = set(wallet_dict[username]["nodes"])

    print("Login successful")
    print("      details:" )
    print(f"         address: {wallet_dict[username]["address"]}")
    print(f"         available balance : {wallet_dict[username]["available balance"]}")
    print(f"         pending balance : {wallet_dict[username]["pending balance"]}")
    print(f"         total balance : {wallet_dict[username]["total balance"]}")
                
    

    return wallet.port









def main(port = 5000, subprocess = False):
    if subprocess:
        
        app.run(host="0.0.0.0", port=port)
    else:
        
        port = login_offline()
        if port != -1:
            app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()


    





    
