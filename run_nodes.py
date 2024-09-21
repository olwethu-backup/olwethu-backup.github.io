import blockchain
import subprocess
import json
from multiprocessing import Process


def main():

    node_dict = json.load(open("nodes.json", "r"))

    node_list = [node for node in node_dict]
   

    node_processes = []

   

    for node in node_list:
        # print(f"{node=}")
        node_processes.append(Process(target = blockchain.main, kwargs = {"username" : node, "password" : node_dict[node]["password"]}))
    
    for process in node_processes:
        # print(f"{process=}")
        process.start()

if __name__ == "__main__":
    main()

    
    

