from gevent import monkey
monkey.patch_all() #TODO: Figure out what this does and why it works so beautifully

# from blockchain import BlockChain
from uuid import uuid4
from flask import Flask, jsonify, request
import grequests
import json
from hashlib import sha256
import time

import os


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
        self.past_transactions = dict({})
    

    def create_wallet_file(self, username):


        wallet_file = open(f"{username}_wallet.json", "w")
       
        wallet_dict = dict({})

        wallet_dump = json.dumps(wallet_dict)
        
        wallet_file.write(wallet_dump)
 
        wallet_file.close()

    def save_transaction(self, transaction):
        wallet_dict = json.load(open(f"{self.username}_wallet.json", "r"))

        past_transactions = wallet_dict["past_transactions"]

        past_transactions[transaction["transaction_id"]] = transaction

        wallet_dict["past_transactions"] = past_transactions

        wallet_dict_dump = json.dumps(wallet_dict)

        wallet_file = open(f"{self.username}_wallet.json", "w")
        
        wallet_file.write(wallet_dict_dump)

        wallet_file.close()








    def send(self, amount, address):
        #Creates a transaction that sends currency to a specific address.
        #The transaction will only be valid once it is on the chain as a block

        if amount <= self.available:
            
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
    
    def read_chain(self, chain):

        transaction_address = "127.0.0.1:" + str(self.port)

        print(f"{transaction_address=}")

        available = 0

        for block in chain:
            
            for transaction in block["transactions"]:
                
                print(f"{transaction['sender']=}")
                print(f"{transaction['recipient']=}")
                if transaction["sender"] == transaction_address:

                   

                    available -= float(transaction["amount"])
                    print("sender")
                    print(f"{float(transaction['amount'])=}")
                    print(f"{available=}")
                    print(".................")
                
                if transaction["recipient"] == transaction_address:
                    
                    available += float(transaction["amount"])

                    print("recipient")
                    print(f"{float(transaction['amount'])=}")
                    print(f"{available=}")
                    print(".................")

        self.available = available
        


                



    def update_balance(self):

        for node in self.nodes:

            try:
                rs = [grequests.get(f"http://{node}/chain")]
                responses = grequests.map(rs)

                response = responses[0]

                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']

                    print("chain=")
                    for c in chain:
                        print(c)

                    self.read_chain(chain)

                    self.total = self.available + self.pending
                
                break

            except:

                print(f"{node} is unavailable [wallet.update_balance()]")

                continue
        
        wallets_dict = json.load(open(f"{self.username}_wallet.json", "r"))

        wallets_dict["available balance"] = self.available
        wallets_dict["pending balance"] = self.pending
        wallets_dict["total balance"] = self.total
        
        wallets_dump = json.dumps(wallets_dict)
        wallets_file = open(f"{self.username}_wallet.json", "w")
        wallets_file.write(wallets_dump)
        wallets_file.close()



#Instantiating a wallet with an API endpoint

app = Flask(__name__)

wallet = Wallet()

wallet_identifier = wallet.address


@app.route("/wallets/register", methods = ["POST"])
def register():
    """
        Receives a username and password (in JSON), will automatically generate an address for this account.
    """
    # print("oneoneoneoneoneoneone")
    values = request.get_json()
    username = values.get("username")
    if ("password_encrypted" not in values) or values.get("password_encrypted") == "False":
        # print("twotwotwotwotwotwotwotwotwo")
        # print(f"{values=}")
        password = sha256(values.get("password").encode()).hexdigest() #TODO: Encrypt this password
    else:
        # print("threethreethreethreethreethreethreethree")
        password = values.get("password")
    


    
    port_file = open("port_counter.txt", "r")
    port_data = int(port_file.read())
    # print("fourfourfourfourfourfourfourfourfourfour")
   
    new_port = port_data + 2
    port_file = open("port_counter.txt", "w")
    port_file.write(str(new_port))
    port_file.close()

    # print("sixsixsixsixsixsixsix")




    wallet_info = {
        "username": username,
        "port": port_data,
        "password": password,
        "address": str(uuid4()).replace('-', ''),
        "available balance": 0,
        "pending balance": 0,
        "total balance": 0,
        "nodes": [],
        "past_transactions": []
    }
    
    # print("sevensevensevensevensevenseven")
    
    
    
    dir_list = os.listdir()



    # wallet_dict = json.load(open("wallets.json", "r"))

    if f"{wallet_info['username']}_wallet.json" in dir_list:
        # print("eighteighteighteighteighteight")
        return "Error: A wallet with this username already exists", 400
    
    # print("nineninenineninenineninenineninenine")

    wallet.create_wallet_file(username)
    
    wallet_dict = {"address": wallet_info['address'], "password": wallet_info['password'], "available balance": wallet_info["pending balance"], "pending balance": wallet_info["total balance"], "total balance": wallet_info["total balance"], "nodes": wallet_info["nodes"], "port": wallet_info["port"], "past_transactions": wallet_info["past_transactions"]}
    wallet_json = json.dumps(wallet_dict) #TODO: encrypt password (it's currently stored as plaintext)


    wallet_file = open(f"{username}_wallet.json", "w")

    wallet_file.write(wallet_json)

    wallet_file.close()

    # print("tententententententententen")

    response = {
        'message': f"Wallet '{wallet_info['username']}' created",
        'address': wallet_info['address']
    }

    # print("eleveneleveneleveneleveneleveneleveneleveneleven")

    return jsonify(response), 201



""""


(sending)
available   = 50
pending     = -20
total       = available - pending
            = 50 - (-20)
            = 70

(receiving)
available   = 50
pending     = 20
total       = available - pending
            = 50 - 20
            = 30

    

"""





@app.route("/send", methods = ["POST"])
def send():

    wallet.update_balance()
    print(f"{wallet.available=}")

    

    values = request.get_json()

    print(f"{values=}")

    values_dict = {i : values[i] for i in values}

    values_dict["transaction_id"] = str(uuid4()).replace("-", "")
    values_dict["sender"] = "127.0.0.1:" + str(wallet.port)

    amount = values_dict["amount"]

    if amount > wallet.available:
        return f"Requested amount ({amount}) exceeds available balance ({wallet.available})."


    response = {
        
        "message": "successful test",
        "values": values

    }

    wallet.past_transactions[values_dict["transaction_id"]] = values_dict

    wallet.save_transaction(values_dict)
    
    print(f"{wallet.nodes=}")
    

    rs = [grequests.get(url = "http://" + i + "/propagate", params = values_dict) for i in wallet.nodes]
    # print(f"{rs=}")
    # print("[sleeping] (/propagate)")
    # time.sleep(12)
    # print("[waking up] (/propagate)")

    node_responses = grequests.map(rs)

    print(f"{node_responses=}")
    

    # for i in wallet.nodes:

    #     try:
    #         node_response = requests.get(url = "http://" + i + "/propagate", params = values_dict)
    #         print(f"{node_response.json()=}")
    #     except:
    #         print(f"{i} is unavailable")
    #         pass


    return response, 200

@app.route("/wallets/login", methods = ["GET"])
def login():

    print("-----1-----")
    # print(f"{request=}")
    # print(f"{request.__dict__}")
    # request.__dict__
    values = request

    print(f"{type(values)=}")
    if values.query_string == b'':  #this means that the GET request is sending JSON instead of a query string
        values = request.get_json()
        username = values.get("username")
       
        password = sha256(values.get("password").encode()).hexdigest()
    
    else: #if it gets to this stage, it means that the request's content was not written in JSON
        print("-------------------------handling exception")
        values = request.url.split("?")[1].split("&")
        # R = values.split("?")[1].split("&")
        # print(f"{R=}")
        username = values[0].split("=")[1]
        
        password = values[1].split("=")[1]

       # print(f"{username=}")
       # print(f"{password=}")
        
       

    print("-----1.5-----")
    
    print("-----2-----")
    # wallet_dict = json.load(open("wallets.json", "r"))
    
    dir_list = os.listdir()

    if f"{username}_wallet.json" not in dir_list:
        print(">>>")
        return "Error: Incorrect username or password", 400
    
    wallet_dict = json.load(open(f"{username}_wallet.json", "r"))

    if wallet_dict["password"] != password:
        print("<<<")
        print(f"{wallet_dict["password"]=}")
        print(f"{password=}")
        print(f"{sha256(password.encode()).hexdigest()=}")
        return "Error: Incorrect username or password", 400
   
    wallet.username = username

    print(f"{wallet.username=}")
    
    # wallet.update_balance()
    # print(f"{wallet.available=}")

    wallet.address = wallet_dict["address"]
    wallet.available = wallet_dict["available balance"]
    wallet.pending = wallet_dict["pending balance"]
    wallet.total = wallet_dict["total balance"]
    wallet.nodes = set(wallet_dict["nodes"])
    wallet.port = wallet_dict["port"]
    wallet.past_transactions = wallet_dict["past_transactions"]

    print(f"=\n=\n=\n=\n=\n=\n{wallet.nodes=}=\n=\n=\n=\n=\n=\n")

    print("-----4-----")
    response = {"message": "Login successful",
                "details": {
                    "address": wallet_dict["address"],
                    "available balance" : wallet_dict["available balance"],
                    "pending balance" : wallet_dict["pending balance"],
                    "total balance" : wallet_dict["total balance"]
                }}
    
    print("-----5-----")
    return jsonify(response), 200

# @app.route("/wallets/send", methods = ["GET"])
# def send():

@app.route("/wallets/register_node", methods = ["POST"])
def register_node():
    #registers a node that will propagate a transaction from a wallet to the rest of the network

    values = request.get_json()

    nodes = values.get("nodes")

    for address in nodes:
        wallet.nodes.add(address)

    wallet_data = json.load(open(f"{wallet.username}_wallet.json", "r"))

    
    wallet_info = wallet_data

    wallet_data["nodes"] = list(wallet.nodes)

    wallet_file = open(f"{wallet.username}_wallet.json", "w")

    wallet_dump = json.dumps(wallet_data)

    wallet_file.write(wallet_dump)

    wallet_file.close()

    response = {"message": f"nodes successfully registered",
                "nodes": nodes}

    return jsonify(response), 201















        
def login_offline():

  

  
    username = input("username: ")
    password = sha256(input("password: ").encode()).hexdigest()
    


    

    dir_list = os.listdir()

    
    if f"{username}_wallet.json" not in dir_list:
        
        print("Error: Incorrect username or password")
        return -1
    
    wallet_dict = json.load(open(f"{username}_wallet.json", "r"))
    
    if wallet_dict["password"] != password:
   
        print("Error: Incorrect username or password")
        return -1

    # wallet.update_balance()
    # print(f"{wallet.available=}")

    wallet.username = username
    wallet.port = wallet_dict["port"]
    wallet.address = wallet_dict["address"]
    wallet.available = wallet_dict["available balance"]
    wallet.pending = wallet_dict["pending balance"]
    wallet.total = wallet_dict["total balance"]
    wallet.nodes = set(wallet_dict["nodes"])
    wallet.past_transactions = wallet_dict["past_transactions"]

    print("Login successful")
    print("      details:" )
    print(f"         address: {wallet_dict["address"]}")
    print(f"         available balance : {wallet_dict["available balance"]}")
    print(f"         pending balance : {wallet_dict["pending balance"]}")
    print(f"         total balance : {wallet_dict["total balance"]}")
                
    

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


    





    
