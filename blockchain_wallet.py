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


    
    def save_transactions(self):
        wallet_dict = json.load(open(f"{self.username}_wallet.json", "r"))

        wallet_dict["past_transactions"] = self.past_transactions

        wallet_dict_dump = json.dumps(wallet_dict)

        wallet_file = open(f"{self.username}_wallet.json", "w")
        
        wallet_file.write(wallet_dict_dump)

        wallet_file.close()






    def send(self, address, amount):

        self.update_balance()



    
        print(f"{self.available=}")


    
        

        values_dict = {
                        "recipient": address,
                        "amount": amount
                        }

        values_dict["transaction_id"] = str(uuid4()).replace("-", "")
        values_dict["sender"] = self.address
        values_dict["status"] = "pending"


        amount = values_dict["amount"]

        if amount > self.available:
            print(f"Requested amount ({amount}) exceeds available balance ({self.available}).")
            return f"Requested amount ({amount}) exceeds available balance ({self.available})."
        if amount < 0:
            print(f"Requested amount ({amount}) is less than zero.")
            return f"Requested amount ({amount}) is less than zero."

        response = {
            
            "message": "successful test",
            "values": values_dict

        }

        # print(f'{values_dict["transaction_id"]}')

        self.past_transactions[values_dict["transaction_id"]] = values_dict

        self.save_transaction(values_dict)
        
        print(f"{self.nodes=}")
        

        rs = [grequests.get(url = "http://" + i + "/propagate", params = values_dict) for i in self.nodes]
    

        node_responses = grequests.map(rs)

        print(f"{node_responses=}")
        

        self.available -= amount

        self.pending += amount

        self.total = self.available + self.pending


        print(f"{response['message']}\n\n{response['values']}")

       




    def send_(self, amount, address):
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

        transaction_address = self.address

        print(f"{transaction_address=}")

        available = 0
        # pending = 0

        transaction_recently_confirmed = False

        print(f"{len(chain)=}")
        block_num = 0
        for block in chain:
            print(f"{block_num=}")
            block_num += 1
            for transaction in block["transactions"]:
                print(f"[[[[{block_num=}]]]]")
                

                print()
                print(f"{transaction['sender']=}")
                print(f"{transaction['recipient']=}")
                print(f"{transaction['transaction_id']=}")
                print(f"{transaction['amount']=}")
                print()
                

                if transaction["sender"] == transaction_address:

                    if transaction["transaction_id"] in self.past_transactions:
                        if self.past_transactions[transaction["transaction_id"]]["status"] == "pending":
                            self.past_transactions[transaction["transaction_id"]]["status"] = "confirmed"
                       
                        if not transaction_recently_confirmed:
                            transaction_recently_confirmed = True
                   
                   

                    available -= float(transaction["amount"])
                    print("sender")
                    print(f"{float(transaction['amount'])=}")
                    print(f"{available=}")
                    print(".................")
                    


     
                
                if transaction["recipient"] == transaction_address:

                    if transaction["transaction_id"] in self.past_transactions:
                        if self.past_transactions[transaction["transaction_id"]]["status"] == "pending":
                            self.past_transactions[transaction["transaction_id"]]["status"] = "confirmed"
                       
                        if not transaction_recently_confirmed:
                            transaction_recently_confirmed = True
                   

                    
                    available += float(transaction["amount"])

                    print("recipient")
                    print(f"{float(transaction['amount'])=}")
                    print(f"{available=}")
                    print(".................")

                   

        
        
        self.available = available
        # self.pending = pending
        # self.total = self.available + self.pending

        if transaction_recently_confirmed:
            self.save_transactions()
        

    def register_node(self):
        #registers a node that will propagate a transaction from a wallet to the rest of the network
        
        values = request.get_json()

        

        nodes = []
        done_entering_nodes = False
        node = ""
        
        while not done_entering_nodes:
            node = input("Enter node address (enter 'done' to stop): ")
           

            if node == "done":
                done_entering_nodes = True

            nodes.append(node)

            
            

        for address in nodes:
            self.nodes.add(address)

        wallet_data = json.load(open(f"{self.username}_wallet.json", "r"))

        
        wallet_info = wallet_data

        wallet_data["nodes"] = list(self.nodes)

        wallet_file = open(f"{self.username}_wallet.json", "w")

        wallet_dump = json.dumps(wallet_data)

        wallet_file.write(wallet_dump)

        wallet_file.close()

        response = {"message": f"nodes successfully registered",
                    "nodes": nodes}

        return jsonify(response), 201

                



    def update_balance(self):

        
        print(f"{self.nodes=}")

        for node in self.nodes:
            print(f"{node=}")

            try:

                rs = [grequests.get(f"http://{node}/chain")]
                responses = grequests.map(rs)

                response = responses[0] #TODO: selects first chain in responses, it should instead select the longest chain

                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']

                    print("chain=")
                    for c in chain:
                        print(c)

                    self.read_chain(chain)

                    self.total = self.available + self.pending

                    print(f"{node} is available [wallet.update_balance()]")
                
                break

            except:

                print(f"{node} is unavailable [wallet.update_balance()]")

                continue

        pending = 0

        for past_transaction in self.past_transactions:
            if self.past_transactions[past_transaction]["status"] == "pending":
                pending += float(self.past_transactions[past_transaction]["amount"])
                print(f"FOUND PENDING TRANSACTION: {past_transaction}\nAMOUNT: {float(self.past_transactions[past_transaction]['amount'])}\nPENDING: {pending}")
        
        self.pending = pending
        self.total = self.available + self.pending
        

        
        wallets_dict = json.load(open(f"{self.username}_wallet.json", "r"))

        wallets_dict["available balance"] = self.available
        wallets_dict["pending balance"] = self.pending
        wallets_dict["total balance"] = self.total
        
        wallets_dump = json.dumps(wallets_dict)
        wallets_file = open(f"{self.username}_wallet.json", "w")
        wallets_file.write(wallets_dump)
        wallets_file.close()



#Instantiating a wallet with an API endpoint (wallet doesn't need an API endpoint, actually)

wallet = Wallet()

wallet_identifier = wallet.address






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


def register_offline(username = "", password = ""):
    """
        Receives a username and password, will automatically generate an address for this account.
    """
    # print("oneoneoneoneoneoneone")
    # values = request.get_json()

    print("\n\n")
    print(f"============REGISTER============")
    print("\n\n")
    
    
    if username == "" and password == "":
        username = input("username: ")
        password = sha256(input("password: ").encode()).hexdigest()




    
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
        print("Error: A wallet with this username already exists")
    
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

    print(f'{response["message"]}')
    print(f'address: {response["address"]}')

    # print("eleveneleveneleveneleveneleveneleveneleveneleven")

    # return jsonify(response), 201














        
def login_offline():

  
    login_or_register = input("login (l) or register new wallet(r): ")


    if login_or_register == "r":
        register_offline()
        return -1

    print("\n\n")
    print(f"============LOGIN============")
    print("\n\n")    

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

    wallet.update_balance()

    print("Login successful")
    print("      details:" )
    print(f"         address: {wallet_dict["address"]}")
    print(f"         available balance : {wallet_dict["available balance"]}")
    print(f"         pending balance : {wallet_dict["pending balance"]}")
    print(f"         total balance : {wallet_dict["total balance"]}")
                
    

    return wallet.port



def main():
    login_offline()

    while True:
        
        print('\n\n\n')

        print("===========WALLET DETAILS===========")
        print(f"USERNAME: {wallet.username}")
        print(f"ADDRESS: {wallet.address}")
        print(f"BALANCE:")
        print(f"              AVAILABLE: {wallet.available}")
        print(f"              PENDING:   {wallet.pending}")
        print(f"              TOTAL:     {wallet.total}")

        print('\n\n\n')

        print("===========OPTIONS===========")
        print("TYPE:")
        print("         1: send (send coins)")
        print("         2: register nodes (register nodes for transaction validation)")
        print("         3: update balance (update wallet balance to latest balance reflected on the chain)")


        print("\n\n\n")

        option = int(input("Enter option: "))


        if option == 1:

            address = input("Enter recipient address: ")
            amount = float(input("Enter transfer amount: "))

            wallet.send(address, amount)

        elif option == 2:

            wallet.register_node()
        
        elif option == 3:

            wallet.update_balance()
        


        





if __name__ == "__main__":
    main()


    





    
