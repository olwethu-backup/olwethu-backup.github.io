from gevent import monkey
monkey.patch_all() #TODO: Figure out what this does and why it works so beautifully

import grequests
# import asyncio
import time


def exception_handler(request, exception):
    # print(f"{request} failed with {exception}")
    pass

# def retry(requests, max_retries = 3):
    


def test_func():
    nodes = ['127.0.0.1:5042', '127.0.0.1:5046', '127.0.0.1:5050', '127.0.0.1:5054', '127.0.0.1:5058', '127.0.0.1:5062']
    urls = [f"http://{node}/chain" for node in nodes]

    # print(f"{urls=}")

    rs = [grequests.get(url, timeout = 20) for url in urls]

    responses = grequests.map(rs, exception_handler = exception_handler)
    print(f'{responses=}')

    if None in responses:

        max_retries = 20 
        
        for i in range(max_retries):
            
            print(f"retry #{i + 1}")
            responses = grequests.map(rs, exception_handler = exception_handler)
            print(f'#{i + 1} {responses=}')

            if None not in responses:
                break



    # print("sleeping")
    # time.sleep(15)
    # print("waking up")

    return responses

def main():
    print(test_func())

if __name__ == "__main__":
    main()
