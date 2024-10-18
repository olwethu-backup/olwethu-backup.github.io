import blockchain
import subprocess
import json
from multiprocessing import Process
import time
import os



def main():

    # node_dict = json.load(open("nodes.json", "r"))

    # node_list = [node for node in node_dict]

    node_list = []
   
    dir_list = os.listdir()

    # print(f"{dir_list=}")
    
    for item in dir_list:
        if "_node" in item:
            node_list.append(item[:item.index("_")])
    
    # print(f"{node_list=}")


    node_processes = []

   

    for node in node_list:
        # print(f"{node=}")
        node_processes.append(Process(target = blockchain.main, kwargs = {"username" : node, "password" : "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"}))
    
    for process in node_processes:
        # print(f"{process=}")
        process.start()
        print(f"{process=}")
        time.sleep(20)

if __name__ == "__main__":
    main()

    
    

