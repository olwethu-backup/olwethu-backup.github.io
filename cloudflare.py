import subprocess 
import threading

ports = [5138, 5118, 5142, 5134, 5122, 5126, 5130, 5146]
threads = []

def open_tunnel(the_port):
    subprocess.run(["cloudflared", "tunnel", "--url", f"http://localhost:{the_port}"])

for port in ports:
    open_tunnel_thread = threading.Thread(target = open_tunnel, args = (port, ))
    open_tunnel_thread.daemon = True
    threads.append(open_tunnel_thread)

for thread in threads:
    thread.start()
    