from gevent import monkey
monkey.patch_all() #TODO: Figure out what this does and why it works so beautifully


# import grequests
from time import time, sleep
import json
import hashlib
from uuid import uuid4

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from urllib.parse import urlparse

import threading
import socket

from random import randint
import os

# import requests
import grequests

import blockchain_wallet
import subprocess

from multiprocessing import Process
from hashlib import sha256

from blockchain_wallet import register_offline


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



listener_port_offset = 5000

class BlockChain:
    def __init__ (self):
        self.chain = []
        self.current_transactions = [] #this list serves as the memory pool (mempool) for each node

        self.past_transactions = dict({}) #keeps a dictionary withpast transaction id's as keys. I am using a dictionary for the sake of efficency since dict search has O(N) (constant) complexity

        #Create genesis block

        self.username = ""
        self.wallet_address = ""
        self.port = -1

        self.received_blocks = []

        self.num_proofs = 0
        
        self.ip_address = ""

        #code for consensus with other nodes
        self.nodes = set()

        self.broadcasted_block = threading.Event()
        
 
    def create_node_file(self, username):

        node_file = open(f"{username}_node.json", "w")

        node_dict = dict({})

        node_dump = json.dumps(node_dict)
        
        node_file.write(node_dump)
    
        node_file.close() 
    
    

    def save_chain(self):
        nodes_dict = json.load(open(f"{self.username}_node.json", "r"))
        print(f"{self.username=}")
        nodes_dict["chain"] = list(self.chain)

        nodes_json = json.dumps(nodes_dict)

        nodes_file = open(f"{self.username}_node.json", "w")

        nodes_file.write(nodes_json)

        nodes_file.close()

    def load_chain(self):
        nodes_dict = json.load(open(f"{self.username}_node.json", "r"))

        chain = nodes_dict["chain"]

        return chain

    def broadcast_block(self, block):


        #TODO: Write code that, when accepting a broadcasting block, confirms that the received block does infact contain the correct proof of work

        for i in range(20):
            print(i*"[]")
        
        print(f"{self.nodes=}")

        urls = [f"http://{node[:node.index("t")] + "t" + str(int(node[node.index("t") + 1:node.index("t") + 5]) + listener_port_offset)}" for node in self.nodes]

        # print(f"\n\n\n\n\n{urls=}\n\n\n\n\n")
        
        for i in range(20):
            print(i*"<>")

        print(f"{urls=}")

        rs = [grequests.post(url = url, json = block) for url in urls]

        responses = grequests.map(rs)

        # print(f"\n\n\n\n\nbroadcast responses = {[r.__dict__ for r in responses]}\n\n\n\n\n")
        
        print(f"\n\n\n\n\nbroadcast responses = {responses}\n\n\n\n\n")


        print(100*"\n")
        

    




    def register_node(self,address):

        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

        node_dict = json.load(open(f"{self.username}_node.json", "r"))

        node_dict["nodes"] = list(self.nodes)


        
       
        node_json = json.dumps(node_dict)
        node_file = open(f"{self.username}_nodes.json", "w")
        node_file.write(node_json)
        node_file.close()
        

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

            # print(f"{prev_block}")
            # print(f"{block}")
            # print("\n-----------\n")
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
            try:

                for i in range(10):
                    print(i*"*")
                    
                rs = [grequests.get(f"http://{node}/chain")] #is there a way to use https to ensure that packets are encrypted as they are sent and received?
                responses = grequests.map(rs)
                response = responses[0]
                
                print(f"{responses=}")
                print(f"{response=}")
                
                idx = 0

                if response is None: #TODO:figure out why this has recently been returning None
                    
                    print(f"------------->???{node} is unavailable [blockchain.resolve_conflicts()]")
                    continue

                    # while idx < len(responses):
                    #     print(f"{responses[idx]=}")
                    #     if responses[idx] is not None:
                    #         response = responses[idx]
                    #         print('BREAK --------------------')
                    #         break
                    #     idx += 1




                print(f'======\n{node}\n======')
                if response.status_code == 200:

                    length = response.json()['length']
                    chain = response.json()['chain']

                    print(f"{length=}")
                    print(f'{len(self.chain)=}')
                    print(f"{max_length=}")

                    # Check if the length is longer and the chain is valid
                    chain_valid = self.valid_chain(chain)
                    if length > max_length and chain_valid:
                        max_length = length
                        new_chain = chain
                        print(f"{chain_valid=} and length > max_length")

                    else:

                        if length <= max_length:
                            print("\n\n\n\n")
                            print("length <= max_length")
                            print(f"{chain_valid=}")
                            print("\n\n\n\n")
                            
                        if not chain_valid:
                            print("\n\n\n\n")
                            
                            print(f"{chain_valid=}")
                            print("\n\n\n\n")
            except ConnectionError:
                print(f"{node} is unavailable [blockchain.resolve_conflicts()]")
        #Replace our chain if we discover a new valid chain that's longer than our chain

        if new_chain:
            self.chain = new_chain
            self.save_chain()
            return True
        
        return False

    def clear_chain(self):
        nodes_dict = json.load(open(f"{self.username}_node.json", "r"))
        print(f"{self.username=}")


        self.chain = []
        nodes_dict["chain"] = self.chain

        nodes_json = json.dumps(nodes_dict)

        nodes_file = open(f"{self.username}_node.json", "w")

        nodes_file.write(nodes_json)

        nodes_file.close()



    def is_valid_transaction(self, incoming_transaction):

        sender_address = incoming_transaction["sender"]
        print(f"{sender_address=}")

        available = 0

        if float(incoming_transaction["amount"]) < 0:
            return False
        
        for block in self.chain:
            
            for transaction in block["transactions"]:
                
                print(f"------------>{transaction['sender']=}")
                print(f"<------------{transaction['recipient']=}")


                if transaction["sender"] == sender_address:

                   
                   

                    available -= float(transaction["amount"])

                    print("sender")
                    print(f"{float(transaction['amount'])=}")
                    print(f"{available=}")
                    print(">>>>>>>>>>>>>>>>>>>>>")
                
                if transaction["recipient"] == sender_address:

                   
                    
                    available += float(transaction["amount"])

                    print("recipient")
                    print(f"{float(transaction['amount'])=}")
                    print(f"{available=}")
                    print(">>>>>>>>>>>>>>>>>>>>>")

        print(f"------- {available=}")
        print(f"------- {incoming_transaction['amount']=}")
        
        if available >= float(incoming_transaction["amount"]):
            return True
        else:
            return False

        

       
    def accept_broadcasted_blocks(self):

        for i in range(28):
            print(i*"~&")

        print(f"~~~~~~~~~~~RECEIVED BROADCASTED BLOCKS (port: {self.port})")
        self.broadcasted_block = threading.Event()

        print(f"{self.broadcasted_block=}")
        
        print(f"~~~~~~~~~~~-----Adding received blocks to chain (port: {self.port}) (len(self.received_blocks): {len(self.received_blocks)})")
        
        print("~~~~~~~~~~~__________________________________________________________________")
        print(f'\n_+\n_+\n_+\n_+\n_+\n{self.broadcasted_block=}\n_+\n_+\n_+\n_+\n_+\n')

        print(f'\n|\n|\n|\n|\n|\n{self.received_blocks=}    {self.port=} \n|\n|\n|\n|\n|\n')

        for i in range(len(self.received_blocks)):
            print(f">~<~<~>~<~{i}")

            if self.chain[-1]["index"] == self.received_blocks[i]["index"] - 1:

                self.received_blocks[i]["previous_hash"] = self.hash(self.chain[-1])

                duplicate_transaction_indices = []
                new_current_transactions = []

                for transaction in self.received_blocks[i]["transactions"]:

                    idx = 0
                    for current_transaction in self.current_transactions:

                        if current_transaction["transaction_id"] == transaction["transaction_id"]:
                            duplicate_transaction_indices.append(idx)
                            # print(50*"\n")
                            # for a in range(100):
                            #     print(a*f"DUPLICATE TRANSACTION (transaction ID: {transaction['transaction_id']}) (current_transaction ID: {current_transaction['transaction_id']}) {idx =}")
                            # print(50*"\n")
                        else:
                            if idx not in duplicate_transaction_indices:
                                new_current_transactions.append(current_transaction)
                                # print(f"{self.current_transactions=}")
                                # print(f"{new_current_transactions=}")
                                # print(f"{(current_transaction['transaction_id'] == transaction['transaction_id'])=}")
                                # print(f"{current_transaction['transaction_id']=}")
                                # print(f"{transaction['transaction_id']=}")


                        
                        idx += 1
                
                print(f"{len(self.current_transactions)=}")
                print(f"{self.current_transactions=}")
                
                self.current_transactions = new_current_transactions #eliminates duplicate transactions that were already accounted for in the received block
                print(f"{len(self.current_transactions)=}")
                print(f"{self.current_transactions=}")
                print("removed duplicate transactions")
                
            
               
                self.received_blocks[i]["previous_hash"] = self.hash(self.chain[-1])
                self.chain.append(self.received_blocks[i])

                # self.broadcast_block(self.received_blocks[i]) #TODO: Look into why this broadcast call is cauing such a big delay in the network (could it be infinite recursion)
                
                print("~~~~~~~~~~~ADDING BLOCK TO CHAIN") #TODO: broadcast again after adding block
                print(f"{self.received_blocks[i]=}")

            
            
            if self.chain[-1]["index"] == self.received_blocks[i]["index"]:

                for y in range(50):
                    print(y*"$")
                print(f"FOUND MATCHING BLOCK")

                print(f"{(self.chain[-1]["index"] == self.received_blocks[i]["index"])=}")

                print(f"{self.chain[-1]=}      {self.chain[-1]["timestamp"]=}      {self.chain[-1]["proof"]=}")

                print(10*"\n")

                print(f"{self.received_blocks[i]=}      {self.received_blocks[i]["timestamp"]=}      {self.received_blocks[i]["proof"]=}")

                print(10*"\n")

                print(f"{self.received_blocks[i]=}      {self.received_blocks[i]["timestamp"]=}      {self.received_blocks[i]["proof"]=}")

                if float(self.received_blocks[i]["timestamp"]) < float(self.chain[-1]["timestamp"]):
                    head = self.chain.pop(-1)

                    print("REPLACING HEAD WITH EARLIER-TIMESTAMPED BLOCK")

                    print(f"{head=}")
                    print(f"{self.received_blocks[i]=}")

                    self.received_blocks[i]["previous_hash"] = self.hash(self.chain[-1])
                    self.chain.append(self.received_blocks[i])

                    # self.broadcast_block(self.received_blocks[i]) #TODO: Look into why this broadcast call is cauing such a big delay in the network (could it be infinite recursion)

                    print("DONE ADDING EARLIER-TIMESTAMPED BLOCK")
                    print(f"[{self.chain[-1]}]")

                    print(f"{(self.chain[-1] == self.received_blocks[i])=}")

                    









        print("~~~~~~~~~~~__________________________________________________________________")
        
       

    
    def proof_of_work(self, last_proof):

        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """
        #TODO: Figure out why the nodes are mining an extra time after receiving broadcasted blocks
        #TODO: Make sure that received blocks hash the previous block in the chain
        #TODO: Make sure that the node prioritises the block with the earliest timestamp to add to its chain. Therefore, if it receives a broadcasted block with an earlier timestamp, it should be prioritise that one to add to a block

        # random_delay = randint(0, 40)


       
        random_delay = randint(0, 3)

        # delay = 0

        self.num_proofs += 1

        print(60*"u\n")
        print(f"{last_proof=} {self.num_proofs=} {self.current_transactions=}")
        print(60*"\n")


        proof = 0

        for i in range(28):
                    print(i*"_-")

        
        
        print(f"starting proof of work ({self.port=}) ({self.num_proofs=}) ")

        # for i in range(0, random_delay*500):
        #     delay += 1
        
        sleep(random_delay)
        print(f"{random_delay=} ({self.port=}) ({self.username=})")

        
        while self.valid_proof(last_proof, proof) is False:

            if self.broadcasted_block.is_set():

                # self.accept_broadcasted_blocks()        
                # self.save_chain()
                

                return -1    
                # break

            proof += 1

            sleep(0) #relinquishes control over CPU so that listener thread can interrupt the mining if necessary

        
        for i in range(28):
                    print(i*"v^")

        print("proof of work complete")
       
        
        

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

        # difficulty = 5

        difficulty = 3

        return guess_hash_digest[:difficulty] == difficulty*"0"
        

        #["127.0.0.1:5042", "127.0.0.1:5046", "127.0.0.1:5050", "127.0.0.1:5054", "127.0.0.1:5058", "127.0.0.1:5062"]
    
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

        # for c_t in self.current_transactions:
        #     self.past_transactions[c_t["transaction_id"]] = 1
        print(f"{self.past_transactions=}")

        self.chain.append(block)

        self.save_chain()
        return block



    def new_transaction(self, sender, recipient, amount, transaction_id, priority = False):

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
                               'amount': amount,
                               'transaction_id': transaction_id}
            
        if priority:
            self.current_transactions = [transaction_details] + self.current_transactions
        else:
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

# app = Flask(__name__)
# CORS(app,    resources={r"/*": {"origins": "*"}})



app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Generate a globally unique address for this node

node_identifier = str(uuid4()).replace('-','')

# Instantiate the BlockChain
blockchain = BlockChain()


def register_account_offline():
    
    print("\n\n")
    print(f"============REGISTER============")
    print("\n\n")   

    username = input("Username: ")
    password = sha256(input("Password: ").encode()).hexdigest() #encrypted password
    ip_address = input("IP Address: ")

    node_info = {
        "username":username,
        "password":password,
        "password_encrypted": "True",
        "address":str(uuid4()).replace("-", ""),
        "connected wallets":"",
        "chain":[],
        "nodes":[]
        
    }
    
    # blockchain.create_node_file(username)

    port_file = open("port_counter.txt", "r")
    port_data = int(port_file.read())
    print(f"{port_data=}")

   
    new_port = port_data + 2
    # print("111111111")
    port_file = open("port_counter.txt", "w")
    # print("22222222222")
    port_file.write(str(new_port))
    # print("3333333333")
    port_file.close()
    # print("444444444")

    
    # print("5555555555")
    dir_list = os.listdir()

    if f"{node_info['username']}_node.json" in dir_list:

        print("Error: A node with this username already exists")


    
    if node_info["connected wallets"] == "":
        # print("7777777777")
        #if no connected wallet already exists, we create one
        

        register_offline(username, password)
        
        node_info["connected wallets"] = username

    blockchain.create_node_file(username)

    # node_dict = json.load(open(f"{username}_node.json", "r"))


    node_dict = {"address":node_info["address"], "password":node_info["password"], "connected wallets": node_info["connected wallets"], "port": port_data, "chain": node_info["chain"], "nodes":node_info["nodes"], "ip_address": ip_address}
    node_json = json.dumps(node_dict)

    node_file = open(f"{username}_node.json", "w")

    node_file.write(node_json)

    response = {
        "message": f"Node '{node_info['username']}' created",
        "address": node_info["address"]
    }

    print(f'{response["message"]}')
    print(f'address: {response["address"]}')



def listen_for_broadcasts(port):
    print(f"{port=}")

    node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    node_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    print("Socket successfully created")

    node_socket.bind(("", port))

    print(f"socket bound to {port}")

    max_connections = 20
    node_socket.listen(max_connections)

    print(f"socket is listening (max connections = {max_connections})")

    while True:
        client_connection, client_address = node_socket.accept()

        print(f"Got connection from {client_address}")

        request = client_connection.recv(1024).decode()

        print(f"\n]\n\n]\n\n]\n\n]\n\n]\n{request=}\n]\n\n]\n\n]\n\n]\n\n]\n")

        request_split = request.split('\r\n\r\n')
        
        block_string = request_split[1]
        print(f"\n-o\n-o\n-o\n-o{block_string=}\n-o\n-o\n-o\n-o")
        block_dict = json.loads(block_string)

        block_dict["previous_hash"] = blockchain.hash(blockchain.chain[-1])

        print(f"\n+\n\n+\n\n+\n\n+\n\n+\n{block_dict=}\n+\n\n+\n\n+\n\n+\n\n+\n")

        for i in range(10):
            print(i*"()")
        
        blockchain.broadcasted_block.set()
        blockchain.received_blocks.append(block_dict)

        blockchain.accept_broadcasted_blocks()        
        blockchain.save_chain()
                


        # print(f'\n=\n=\n=\n=\n=\n{blockchain.broadcasted_block=}\n=\n=\n=\n=\n=\n')

        # print(f'\n>\n>\n>\n>\n>\n{blockchain.received_blocks=}    {blockchain.port=} \n>\n>\n>\n>\n>\n')


        response = f"HTTP/1.0 200 OK\n\nBlock received."

        client_connection.sendall(response.encode())
        
        client_connection.close()
    
    node_socket.close()


@app.route('/mine', methods = ['GET'])
def mine():

    #We run the proof of work algorithm to get the next proof...

    last_block = blockchain.last_block

    # print(f"{50*'09\n'}{last_block=}\n-----------------------------------------------------------------")
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    #We must be rewarded for finding the proof. (New unit of cryptocurrency is created to reward the miner)
    #The sender is "0" to signify that this node has mined a new coin.
    
    # blockchain.new_transaction(
    #     sender = "0",
    #     recipient = node_identifier,    #TODO: Maybe change this recipient identifier to the node's IP address
    #     amount = 1,
    #     transaction_id = str(uuid4()).replace("-", "")
    # )
    
    # print(f"--------BLOCK CREATION TRANSACTIONS--------") #TODO: There might be a problem where the reward is added to the current transactions, and isn't removed from there in the case where the node receives a broadcasted block. This can result in the node being paid for a block it never mined. Fix this.
    # for transaction in blockchain.current_transactions:
    #     if transaction["sender"] == "0":
    #         print("\n\n\n")
    #         print(transaction)
    #         print("::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    #         print("\n\n\n")

   
    # print(f"--------DONE ADDING LATEST BLOCK CREATION TRANSACTION--------")

    #Forge the new Block by adding it to the chain

    response = {"message":"error"}

    #TODO: Implement Merkle Tree for transactions, then compare the Merkle Tree of the latest block to the Merkle Tree of the current transactions to see if they match. If they do match, cancel the current mining process as the block with our current transactions already exists
    #TODO: Modify transaction IDs so that they're hashes of transactions

    if proof > 0:   #if proof_of_work() returned the correct proof

        #check that we didn't already receive a block with the proof that we want
        #TODO: when adding the verification that this proof is correct as per the other TODO, make sure that you do that verification in this block of code too
        
        block_already_exists = False

        for received_block in blockchain.received_blocks:

            print(f"{received_block['proof']}")

            if received_block["proof"] == proof:
                block_already_exists = True
                break
         

        
        if not block_already_exists: #if the current node didn't already receive a block from another node which is the same as the one that the current node mined
            blockchain.new_transaction(
            sender = "0",
            recipient = blockchain.wallet_address,    #TODO: Maybe change this recipient identifier to the node's wallet's IP address
            amount = 1,
            transaction_id = str(uuid4()).replace("-", "")
                )
            
            previous_hash = blockchain.hash(last_block)

        
            block = blockchain.new_block(proof, previous_hash)

            print(f"\n\n\n\n\n\n\n{block=}\n\n\n\n\n\n\n\n")

            response = {
                "message": "New Block Forged",
                "index": block["index"],
                "transactions": block["transactions"],
                "proof": block["proof"],
                "previous_hash": block["previous_hash"]
            }

            blockchain.save_chain()
    
            blockchain.broadcast_block(block)
        
        else:

            print("\n5\n5\n5\n")
            print(f"broadcasted block was already available ({blockchain.username=}) ({blockchain.port=}) ({blockchain.wallet_address=})")
            print("\n5\n5\n5\n")
            response = {
            "message": "Failed to forge block (because broadcasted block was already available)"          
            }
    
    else:
        response = {
            "message": "Failed to forge block"          
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

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'], str(uuid4()).replace("-", ""))

    response = {'message': f'Transaction will be added to Block {index}'}

    return jsonify(response), 201
    # return "We'll add a new transaction"

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain':blockchain.chain,
        'length':len(blockchain.chain),
    }
    print(">>>>>>>>")
    print([{i: blockchain.chain[i]["previous_hash"]} for i in range(len(blockchain.chain))])
    print(">>>>>>>>")
    
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

#TODO: Add 6-block wat before confirming transactions (might be necessary)
#TODO: Research Merkle trees and incorporate them if applicable


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    print("\n\n\n\n\nCONSENSUS\n\n")

    replaced = blockchain.resolve_conflicts() #returns True if chain has been replaced, False otherwise

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
        print('Our chain was replaced')
        print(50*"\n/+")
        blockchain.save_chain()

    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
        print('Our chain is authoritative')
        print(50*"\n/=")
    
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
        "chain":[],
        "nodes":[]
        
    }
    
    # blockchain.create_node_file(username)

    port_file = open("port_counter.txt", "r")
    port_data = int(port_file.read())
    print(f"{port_data=}")

   
    new_port = port_data + 2
    # print("111111111")
    port_file = open("port_counter.txt", "w")
    # print("22222222222")
    port_file.write(str(new_port))
    # print("3333333333")
    port_file.close()
    # print("444444444")

    
    # print("5555555555")
    dir_list = os.listdir()

    if f"{node_info['username']}_node.json" in dir_list:

        return "Error: A node with this username already exists", 400


    
    if node_info["connected wallets"] == "":
        # print("7777777777")
        #if no connected wallet already exists, we create one
        
        wallet_info = {
            "username": username,
            "password": password,
            "password_encrypted": "True"
        }

        # print("88888888888888")

        json_data = wallet_info

        # print("99999999999")        
        # # print(f"{json_data=}")

        # rs = [grequests.post(url = blockchain.wallet_address + "/wallets/register", json = json_data)]
        # responses = grequests.map(rs)
        # wallet_response_data = responses[0]
        # # wallet_response_data = requests.post(url = blockchain.wallet_address + "/wallets/register", json = json_data)

        # # print("101010101010101010")
        # # print(f"{wallet_response_data=}")
        # wallet_response, wallet_response_code = wallet_response_data.json(), wallet_response_data.status_code
        # # print(f"{wallet_response=}")
        # # print(f"{wallet_response_code=}")
        # if wallet_response_code == 400:     #already-existing wallet means that this username cannot be used
        #     return wallet_response, wallet_response_code
        
        node_info["connected wallets"] = wallet_info["username"]

    blockchain.create_node_file(username)

    # node_dict = json.load(open(f"{username}_node.json", "r"))


    node_dict = {"address": node_info["address"], "password":node_info["password"], "connected wallets": node_info["connected wallets"], "port": port_data, "chain": node_info["chain"], "nodes":node_info["nodes"]}
    node_json = json.dumps(node_dict)

    node_file = open(f"{username}_node.json", "w")

    node_file.write(node_json)

    response = {
        "message": f"Node '{node_info['username']}' created",
        "address": node_info["address"]
    }

    return jsonify(response), 201




@app.route("/propagate", methods = ["GET"])
def propagate():

    values = request.url.split("?")[1].split("&")

    print(f"=============={blockchain.username}==============")
    print(f"{values=}")
    print(f"{blockchain.current_transactions=}")
    values_dict = {}

    for v in values:
        v_split = v.split("=")
        values_dict[v_split[0]] = v_split[1]
    
    print(f"{values_dict=}")

    response = {
            "message": "propagation test successful",
            "values": values
                    }

    past_transaction_test = ""




    if values_dict not in blockchain.current_transactions:


        
        if values_dict['transaction_id'] in blockchain.past_transactions:
            print(f'{(values_dict['transaction_id'] in blockchain.past_transactions)=}')
            # past_transaction_test = blockchain.past_transactions[values_dict['transaction_id']]
            pass

        else:

            valid_transaction = blockchain.is_valid_transaction(values_dict)

            if valid_transaction:

                print(f"\n+\n+\n+\n+\n+\n{valid_transaction=}\n+\n+\n+\n+\n+\n")

                blockchain.past_transactions[values_dict["transaction_id"]] = 1
                print(f"\n\n\n----->{blockchain.past_transactions=}\n\n\n")

                blockchain.new_transaction(values_dict['sender'], values_dict['recipient'], values_dict['amount'], values_dict['transaction_id'])
                
                
                print("======ENTERING ASYNCHRONOUS PROPAGATION REQUESTS (grequests.get)======")
                print(f"{blockchain.nodes=}")

                # node_addresses = ["http://" + node + "/propagate" for node in blockchain.nodes]
                # node_responses = [grequests.get(url = "http://" + node + "/propagate", params = values_dict) for node in blockchain.nodes]

                # grequests.map(node_responses)

                rs = [grequests.get(url = "http://" + node + "/propagate", params = values_dict) for node in blockchain.nodes]
                responses = grequests.map(rs)
                print(f'{responses=} (/propagate)')


                # for node in blockchain.nodes:
                #         try:
                #             node_response = requests.get(url = "http://" + node + "/propagate", params = values_dict)
                #             print(f">>>>>> {node_response.json()=}")
                #         except ConnectionError:
                #             print(f"{node} is unavailable")
                
                # print(f"{50*'k\n'}pre-'mine()': {blockchain.current_transactions=}")

                if len(blockchain.current_transactions) > 0: #if the current transactions weren't already put into a block that we received from a broadcast
                    mine()
                    consensus()
               
            else:

                print(f"\n-\n-\n-\n-\n-\n{valid_transaction=}\n-\n-\n-\n-\n-\n")

    else:
        pass

    # mine() #this function call is in the wrong place (it should be in the if-else statement)
    # for i in range(10):
    #     print(i*"?")
    return jsonify(response), 200


    
    

    
    # for address in blockchain.nodes:
    #     pass




@app.route("/nodes/login", methods = ["GET"])
def login():

    values = request.get_json()

    username = values.get("username")
    password = sha256(values.get("password").encode()).hexdigest()

    dir_list = os.listdir()

    if f"{username}_node.json" not in dir_list:
        # print("----------->")
        return "Error: Incorrect username or password", 400

    node_dict = json.load(open(f"{username}_node.json", "r"))

    if node_dict["password"] != password:
        # print("<-----------")
        return "Error: Incorrect username or password", 400
    
    blockchain.address = node_dict["address"]
    blockchain.nodes = node_dict["nodes"]
    blockchain.username = username
    blockchain.port = node_dict["port"]
    blockchain.chain = node_dict["chain"]

    
    broadcast_listener_thread = threading.Thread(target = listen_for_broadcasts, args = (blockchain.port + listener_port_offset, ))
    broadcast_listener_thread.daemon = True
    broadcast_listener_thread.start()
    
    # if len(blockchain.chain) == 0:
    #     mine()


    print(f"{blockchain.port=}")
    
    # rs = [grequests.get(url = blockchain.wallet_address + "/wallets/login", params = {"username": username, "password": password, "password_encrypted": "True"})]
    # responses = grequests.map(rs)
    # response = responses[0]

    
    # # response = requests.get(url = blockchain.wallet_address + "/wallets/login", params = {"username": username, "password": password, "password_encrypted": "True"}) #TODO: Fix this because the password is getting encrypted twice (double encryption)
    
    
    
    # # print(f"{response=}")
    # response, status_code = response.json(), response.status_code
    
    # if status_code != 200:
    #     return response, status_code
    

    print(f"{len(blockchain.chain)=}")
    if len(blockchain.chain) == 0:

        blockchain.new_block(previous_hash=1, proof=100)


    response = {
        "message": "Login successful",
        "details": {
            "address": blockchain.address
        }
    }

    return jsonify(response), 200
    

def login_offline(username = "", password = ""):


    
    print("\n\n")
    print(f"============LOGIN============")
    print("\n\n")   

    print("--------------1")
    if (username == "") or (password == ""):

        login_or_register = input("login (l) or register new node(r): ")


        if login_or_register == "r":
            register_account_offline()
            return -1


        # print(">>>>>>>>><<<<<<<<<<<<<")
        username = input("username: ")
        password = sha256(input("password: ").encode()).hexdigest()

    print("--------------2")
    # node_dict = json.load(open("nodes.json", "r"))

    print("--------------3")

    dir_list = os.listdir()


    if f"{username}_node.json" not in dir_list:
        # print("----------->")
        print("Error: Incorrect username or password")
        return -1
    
    print("--------------4")

    node_dict = json.load(open(f"{username}_node.json", "r"))

    if node_dict["password"] != password:
        # print("<-----------")
        print("Error: Incorrect username or password")
        return -1
    
    print("--------------5")
    blockchain.address = node_dict["address"]
    blockchain.nodes = node_dict["nodes"]
    blockchain.username = username
    blockchain.port = node_dict["port"]
    try:
        blockchain.ip_address = node_dict["ip_address"]
    except KeyError:
        pass

    # p1 = Process(target = blockchain_wallet.main, kwargs = {"port" : blockchain.port + 1, "subprocess" : True})
    # p1.start()


    wallet_dict = json.load(open(f"{blockchain.username}_wallet.json"))

    wallet_address = wallet_dict["address"]

    blockchain.wallet_address = wallet_address  #all transactions to and from this node will use this wallet address
    blockchain.chain = node_dict["chain"]

    broadcast_listener_thread = threading.Thread(target = listen_for_broadcasts, args = (blockchain.port + listener_port_offset, ))
    broadcast_listener_thread.daemon = True
    broadcast_listener_thread.start()
    #TODO: fix chain previous block hashing
    print("--------------6")

    print(f"{len(blockchain.chain)=}")
    if len(blockchain.chain) == 0:

        print("mining new block for len == 0")
        blockchain.new_block(previous_hash=1, proof=100)

    print("--------------7")
    

    print(f"{blockchain.port=}")

    print("--------------8")
    
    print("--------------8.1")
    
    print("--------------8.2")

    # print(f">=======\n\n\n\n{blockchain.wallet_address}\n\n\n\n=======<")
    # print("--------------8.3")
    # print("--------------------------------------------------")
    # print("--------------8.4")
    # rs = [grequests.get(url = blockchain.wallet_address + "/wallets/login", params = {"username": username, "password": password, "password_encrypted": "True"})]
    # print("====sleeping...")
    # sleep(12)
    # print("====waking up...")
    # # grequests.map(rs)
    # print(f'{rs=}')
    # print("--------------8.5")
    # responses = grequests.map(rs)
    # print(f"{responses=}")
    # print("--------------8.6")
    # response = responses[0]
    # print(f"{responses[0].__dict__=}")
    # print("--------------9")
    
    # print(":::::::::::::::::::::::::::::::::::::::::::::::::")
    # response, status_code = response.json(), response.status_code
    # print("--------------------------->")

    # print(f"{response=}")
    # print(f"{status_code=}")

    # print("--------------10")
    
    # if status_code != 200:
    #     print("Login unsuccessful")
    #     return "Error"

    print("--------------11")
    
    print("Login successful")

    print("--------------12")

    return [blockchain.ip_address, blockchain.port]




def open_tunnel(the_port):
    subprocess.run(["lt", "--port", f"{the_port}", "--subdomain", f"mywallet{the_port}"], shell = True)
    
def open_tunnel2(the_port):
    subprocess.run(["cloudflared", "tunnel", "--url", f"http://localhost:{the_port}"])

def main(username = "", password = "", mode = ""):
    # blockchain_wallet.main()
    # subprocess.check_call("python blockchain_wallet.py", shell = True)
    
        
    ip_address, port = login_offline(username, password) #int(input("Blockchain Node - Select port (5000/5001): "))

    if mode == "clear":
        blockchain.clear_chain()
        print(f"{blockchain.port} node's chain has been cleared")
        print("--------------------------------------------------")
        return
    if ip_address == "":
        if port != -1:
            # p1 = Process(target = blockchain_wallet.main, kwargs = {"port" : port + 1, "subprocess" : True})

            # blockchain.wallet_address = "http://localhost:" + str(port + 1) #all transactions to and from this node will use this wallet port

            # p1.start()
            

            # open_tunnel2_thread = threading.Thread(target = open_tunnel2, args = (port, ))
            # open_tunnel2_thread.daemon = True
            # open_tunnel2_thread.start()

            open_tunnel_thread = threading.Thread(target = open_tunnel, args = (port, ))
            open_tunnel_thread.daemon = True
            open_tunnel_thread.start()

            
            # subprocess.run(["lt", "--port", f"{port}", "--subdomain", f"mywallet{port}"], shell = True)

            app.run(host="0.0.0.0", port=port)
            

            # p2 = Process(target = app.run, kwargs = {"host":"0.0.0.0", "port": int(input("Blockchain Node - Select port (5000/5001): "))})
    else:
        ip_address_without_port = ip_address[:ip_address.index(":")]
        port = int(ip_address[ip_address.index(":") + 1:])

        print(f"{ip_address_without_port=}")
        print(f"{port=}")       
        
        # subprocess.run(["lt", "--port", f"{port}", "--subdomain", f"mywallet{port}"], shell = True)
        
        open_tunnel_thread = threading.Thread(target = open_tunnel, args = (port, ))
        open_tunnel_thread.daemon = True
        open_tunnel_thread.start()


        sleep(5)

        app.run(host=ip_address_without_port, port=port)
        



if __name__ == '__main__':
    main()



