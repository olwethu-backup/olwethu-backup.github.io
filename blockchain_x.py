from time import time
import json
import hashlib
from uuid import uuid4

from flask import Flask, jsonify, request
from urllib.parse import urlparse

import requests



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
        self.current_transactions = [] 

        self.address = ""
        #Create genesis block

        self.new_block(previous_hash=1, proof=100)

        #code for consensus with other nodes
        self.nodes = set()

    def register_node(self,address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """
        # print(f"address = {address}")
        # print(f"type(address) = {type(address)}")
        parsed_url = urlparse(address)
        # print(f"parsed_url = {parsed_url}")
        # print(f"type(parsed_url) = {type(parsed_url)}")
        parsed_url_netloc = parsed_url.netloc
        # print(f"parsed_url_netloc = {parsed_url_netloc}")
        # print(f"type(parsed_url_netloc) = {type(parsed_url_netloc)}")
        self.nodes.add(parsed_url_netloc)

        
        self.get_nodes(parsed_url_netloc)

    def register_node_base_case(self, address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """
        # print(f"address = {address}")
        # print(f"type(address) = {type(address)}")
        parsed_url = urlparse(address)
        # print(f"parsed_url = {parsed_url}")
        # print(f"type(parsed_url) = {type(parsed_url)}")
        parsed_url_netloc = parsed_url.netloc
        # print(f"parsed_url_netloc = {parsed_url_netloc}")
        # print(f"type(parsed_url_netloc) = {type(parsed_url_netloc)}")
        self.nodes.add(parsed_url_netloc)


    def get_nodes(self, address):
        prefix = "http://"
        full_address = prefix + address
        response = requests.get(full_address + "/nodes/total_nodes")
        response_json = response.json()
        node_addresses = response_json['nodes'] #expects list of parsed URLs

        
        
        json_data = jsonify({
            'nodes': [self.address]  
        })

        for node_address in node_addresses:

            if node_address != self.address:
                self.nodes.add(node_address)               
                #self.register_node(prefix + address, get_node_addresses = False) 
                requests.post(url = full_address + "/nodes/register_base_case", json = json_data) #base case function to prevent recursion from the combo of register_node() and get_nodes()

        
        



        






    
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

@app.route("/nodes/register_base_case", methods = ["POST"])
def register_nodes_base_case():
    values = request.get_json()

    nodes = values.get("nodes") # The function expects the client (which is posting information about the nodes) to provide a dict-like structure that contains a list of nodes

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    
    for node in nodes:
        blockchain.register_node_base_case(node)
    
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201

@app.route("/nodes/total_nodes", methods = ["GET"])
def total_nodes():
    response = {
        'nodes':list(blockchain.nodes)
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


def main():

    port = int(input("Select port (5000/5001): "))

    blockchain.address = "http://localhost:" + str(port)




    app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    main()



