import os
import json



def create_node_file(username):

    dir_list = os.listdir()
    print(f"{dir_list=}")
    for i in dir_list:
        print(i)

    node_file = open(f"{username}_node.json", "w")

    node_dict = dict({})

    node_dump = json.dumps(node_dict)
        
    node_file.write(node_dump)
    
    node_file.close() 


def create_wallet_file(username):


    wallet_file = open(f"{username}_wallet.json", "w")

 
    wallet_file.close()




def main():
    test_usernames = ["a", "b", "c", "d", "e", "f"]

    for test_username in test_usernames:

        create_node_file(test_username)






if __name__ == "__main__":
    main()

