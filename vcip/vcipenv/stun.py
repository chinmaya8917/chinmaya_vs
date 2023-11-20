import pystun

def check_stun_server(stun_host, stun_port):
    try:
        nat_type, external_ip, external_port = pystun.get_ip_info(stun_host, stun_port)
        print(f"NAT Type: {nat_type}")
        print(f"External IP: {external_ip}")
        print(f"External Port: {external_port}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# Replace with your STUN server's IP and port
stun_host = "192.168.63.103"
stun_port = 8585

if check_stun_server(stun_host, stun_port):
    print("STUN server is working.")
else:
    print("STUN server is not working.")
