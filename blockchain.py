from time import time
import json
import hashlib
from uuid import uuid4

from flask import Flask, jsonify, request
from urllib.parse import urlparse

import requests
import blockchain_wallet
import subprocess

from multiprocessing import Process
from hashlib import sha256


# example of a block
# block = {
#    'index': 1,
#    'timestamp': time.time(),
#    'transactions': [
#        {
#            'sender': 'd2kj32k3h4hjk232k3kh',
#            'recipient': 'ds977d7s9d779svbfs4',
#            'amount': 5,
#        }
#    ],
#    'proof': 37287329127,
#    'previous_hash': "75647dfaf7asd647as67asf4dsas5a7f64d7as6fsa7d"
# }

class BlockChain:
    def __init__ (self):
        self.chain = []
        self.current_transactions = [] #this list serves as the memory pool (mempool) for each node

        #Create genesis block

        self.new_block(previous_hash=1, proof=100)

        #code for consensus with other nodes
        self.nodes = set()

        self.username = ""
        self.wallet_address = ""
        self.port = -1

    def save_chain(self):
        nodes_dict = json.load(open("nodes.json", "r"))

        nodes_dict[self.username]["chain"] = self.chain

        nodes_json = json.dumps(nodes_dict)

        nodes_file = open("nodes.json", "w")

        nodes_file.write(nodes_json)

        nodes_file.close()


   




    def register_node(self,address):

        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        

    def valid_chain(self, chain):

        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        #the longest chain will be considered to be the valid one

        prev_block = chain[0]
        current_index = 1

        while current_index < len(chain):

            block = chain[current_index]

            print(f"{prev_block}")
            print(f"{block}")
            print("\n-----------\n")
            #Check that the hash of the block is correct

            if block['previous_hash'] != self.hash(prev_block):
                return False
            
            #Check that the Proof of Work is correct

            if not self.valid_proof(prev_block["proof"], block["proof"]):
                return False
            
            prev_block = block
            current_index += 1
            
        return True
    
    def resolve_conflicts(self):

        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        #We're only looking for chains longer than ours
        max_length = len(self.chain)

        #Get the chains of all the nodes in our network and verify them

        for node in neighbours:

            response = requests.get(f"http://{node}/chain") #is there a way to use https to ensure that packets are encrypted as they are sent and received?

            if response.status_code == 200:

                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        #Replace our chain if we discover a new valid chain that's longer than our chain

        if new_chain:
            self.chain = new_chain
            return True
        
        return False






    
    def proof_of_work(self, last_proof):

        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """
        
        proof = 0
        
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        # while sha256(f'{p*last_proof}'.encode()).hexdigest()[:4] != "0000":
        #     p += 1
        
        return proof
    
    @staticmethod
    def valid_proof(last_proof, proof):

        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash_digest  = hashlib.sha256(guess).hexdigest()

        return guess_hash_digest[:4] == "0000"
        

    
    def new_block(self, proof, previous_hash=None):

        #New block created and appended to the blockchain
        
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        # self.chain.append(block)

        #reset the current list of transactions, as the transactions have now been stored in the block (check that the transaction list in the block doesn't point to the same data as the variable that I'm now resetting)
        self.current_transactions = []

        self.chain.append(block)
        return block



    def new_transaction(self, sender, recipient, amount):

        #Appends a new transaction to the transaction list
        
        """
        Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """

        transaction_details = {'sender': sender,
                               'recipient': recipient,
                               'amount': amount}
        
        self.current_transactions.append(transaction_details)

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
         
        #Creates a hash from a block
        
         """
        Creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """
         
         #The dictionary should be ordered to prevent inconsistent hashes

         block_string = json.dumps(block, sort_keys=True).encode()
         return hashlib.sha256(block_string).hexdigest()
        

    @property
    def last_block(self):
        # Returns the chain's last block
        
        return self.chain[-1]
    

#Instantiating a node with a blockchain API endpoint

app = Flask(__name__)

# Generate a globally unique address for this node

node_identifier = str(uuid4()).replace('-','')

# Instantiate the BlockChain
blockchain = BlockChain()

@app.route('/mine', methods = ['GET'])
def mine():

    #We run the proof of work algorithm to get the next proof...

    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    #We must be rewarded for finding the proof. (New unit of cryptocurrency is created to reward the miner)
    #The sender is "0" to signify that this node has mined a new coin.

    blockchain.new_transaction(
        sender = "0",
        recipient = node_identifier,
        amount = 1
    )

    #Forge the new Block by adding it to the chain

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        "message": "New Block Forged",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"]
    }

    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():

    values = request.get_json()

    # Check that the required fields are in the POST'ed data

    required = ['sender', 'recipient', 'amount']

    if not all(k in values for k in required):
        return 'Missing values', 400

    #Create a new Transaction

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}

    return jsonify(response), 201
    # return "We'll add a new transaction"

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain':blockchain.chain,
        'length':len(blockchain.chain),
    }
    
    return jsonify(response), 200


@app.route("/nodes/register", methods=["POST"])
def register_nodes():
    values = request.get_json()

    nodes = values.get("nodes") # The function expects the client (which is posting information about the nodes) to provide a dict-like structure that contains a list of nodes

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    
    for node in nodes:
        blockchain.register_node(node)
    
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201

@app.route('/save_chain', methods=['GET'])
def save_chain():
    blockchain.save_chain()

    response = {
        "message": "Chain saved",
        "chain": blockchain.chain
                }
    
    return jsonify(response), 200


@app.route('/nodes/resolve', methods=['GET'])
def consensus():

    replaced = blockchain.resolve_conflicts() #returns True if chain has been replaced, False otherwise

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }

    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    
    return jsonify(response), 200


@app.route("/nodes/register_account", methods = ["POST"])
def register_account():
    
    values = request.get_json()
    username = values.get("username")
    password = sha256(values.get("password").encode()).hexdigest() #encrypted password

    node_info = {
        "username":username,
        "password":password,
        "password_encrypted": "True",
        "address":str(uuid4()).replace("-", ""),
        "connected wallets":"",
        "chain":[]
        
    }
    
    port_file = open("port_counter.txt", "r")
    port_data = int(port_file.read())
    print(f"{port_data=}")

   
    new_port = port_data + 2
    port_file = open("port_counter.txt", "w")
    port_file.write(str(new_port))
    port_file.close()


    node_dict = json.load(open("nodes.json", "r"))

    if node_info["username"] in node_dict:
        return "Error: A node with this username already exists", 400

    if node_info["connected wallets"] == "":
        #if no connected wallet already exists, then we create one
        
        wallet_info = {
            "username": username,
            "password": password,
            "password_encrypted": "True"
        }

        json_data = wallet_info
        
        # print(f"{json_data=}")


        wallet_response_data = requests.post(url = blockchain.wallet_address + "/wallets/register", json = json_data)
        # print(f"{wallet_response_data=}")
        wallet_response, wallet_response_code = wallet_response_data.json(), wallet_response_data.status_code
        # print(f"{wallet_response=}")
        # print(f"{wallet_response_code=}")
        if wallet_response_code == 400:     #already-existing wallet means that this username cannot be used
            return wallet_response, wallet_response_code
        
        node_info["connected wallets"] = wallet_info["username"]

        


    node_dict[node_info["username"]] = {"address":node_info["address"], "password":node_info["password"], "connected wallets": node_info["connected wallets"], "port": port_data, "chain": node_info["chain"]}
    node_json = json.dumps(node_dict)

    node_file = open("nodes.json", "w")

    node_file.write(node_json)

    response = {
        "message": f"Node '{node_info['username']}' created",
        "address": node_info["address"]
    }

    return jsonify(response), 201


@app.route("/propagate", methods = ["GET"])
def propagate():

    values = request.url.split("?")[1].split("&")
    
    

    
    # for address in blockchain.nodes:
    #     pass




@app.route("/nodes/login", methods = ["GET"])
def login():

    values = request.get_json()

    username = values.get("username")
    password = sha256(values.get("password").encode()).hexdigest()

    node_dict = json.load(open("nodes.json", "r"))


    if username not in node_dict:
        # print("----------->")
        return "Error: Incorrect username or password", 400
    
    if node_dict[username]["password"] != password:
        # print("<-----------")
        return "Error: Incorrect username or password", 400
    
    blockchain.address = node_dict[username]["address"]
    blockchain.username = username
    blockchain.port = node_dict[username]["port"]
    print(f"{blockchain.port=}")
    
    response = requests.get(url = blockchain.wallet_address + "/wallets/login", params = {"username": username, "password": password, "password_encrypted": "True"}) #TODO: Fix this because the password is getting encrypted twice (double encryption)
    # print(f"{response=}")
    response, status_code = response.json(), response.status_code
    
    if status_code != 200:
        return response, status_code

    response = {
        "message": "Login successful",
        "details": {
            "address": blockchain.address
        }
    }

    return jsonify(response), 200
    

def login_offline():

    

    username = input("username: ")
    password = sha256(input("password: ").encode()).hexdigest()

    node_dict = json.load(open("nodes.json", "r"))


    if username not in node_dict:
        # print("----------->")
        print("Error: Incorrect username or password")
        return -1
    
    if node_dict[username]["password"] != password:
        # print("<-----------")
        print("Error: Incorrect username or password")
        return -1
       
    blockchain.address = node_dict[username]["address"]
    blockchain.username = username
    blockchain.port = node_dict[username]["port"]
    print(f"{blockchain.port=}")

    
    print("Login successful")
    return blockchain.port




    

def main():
    # blockchain_wallet.main()
    # subprocess.check_call("python blockchain_wallet.py", shell = True)

    port = login_offline() #int(input("Blockchain Node - Select port (5000/5001): "))
    if port != -1:
        p1 = Process(target = blockchain_wallet.main, kwargs = {"port" : port + 1, "subprocess" : True})

        blockchain.wallet_address = "http://localhost:" + str(port + 1) #all transactions to and from this node will use this wallet port

        p1.start()
        app.run(host="0.0.0.0", port=port)

        # p2 = Process(target = app.run, kwargs = {"host":"0.0.0.0", "port": int(input("Blockchain Node - Select port (5000/5001): "))})
        
    

if __name__ == '__main__':
    main()



