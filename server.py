import grpc
from concurrent import futures
import subprocess
import ipaddress
import network_service_pb2
import network_service_pb2_grpc

# Define a predefined IP range
IP_RANGE_START = "10.0.2.20"
IP_RANGE_END = "10.0.2.50"

class NetworkService(network_service_pb2_grpc.NetworkServiceServicer):

    def ChangeIP(self, request, context):
        device_id = request.device_id
        interface_name = request.interface_name
        netmask = request.netmask
        gateway = request.gateway

        # Find an available IP from the predefined range
        static_ip = find_available_ip(IP_RANGE_START, IP_RANGE_END)
        if not static_ip:
            return network_service_pb2.ChangeIPResponse(success=False, message="No available IP addresses found.")

        # Configure the static IP on the device
        success, message = configure_static_ip(interface_name, static_ip, netmask, gateway)

        return network_service_pb2.ChangeIPResponse(success=success, message=message)

def is_ip_in_use(ip):
    try:
        output = subprocess.check_output(['ping', '-c', '1', ip], stderr=subprocess.STDOUT, universal_newlines=True)
        if '1 packets transmitted, 1 received' in output:
            return True
    except subprocess.CalledProcessError:
        return False
    return False

def find_available_ip(start_ip, end_ip):
    start = ipaddress.ip_address(start_ip)
    end = ipaddress.ip_address(end_ip)
    
    for ip in ipaddress.IPv4Network(f"{start_ip}/{end_ip}", strict=False):
        ip_str = str(ip)
        if not is_ip_in_use(ip_str):
            return ip_str
    return None

def configure_static_ip(interface, static_ip, netmask, gateway):
    try:
        subprocess.run(['sudo', 'ifconfig', interface, static_ip, 'netmask', netmask], check=True)
        subprocess.run(['sudo', 'route', 'add', 'default', 'gw', gateway, interface], check=True)
        return True, f"IP address {static_ip} configured successfully."
    except subprocess.CalledProcessError as e:
        return False, f"Failed to configure IP address: {str(e)}"

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    network_service_pb2_grpc.add_NetworkServiceServicer_to_server(NetworkService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Network Service Server running...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

