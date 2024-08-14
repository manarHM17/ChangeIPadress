import grpc
import network_service_pb2
import network_service_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = network_service_pb2_grpc.NetworkServiceStub(channel)
        request = network_service_pb2.ChangeIPRequest(
            device_id="1",
            interface_name="enp0s3",
            netmask="255.255.255.0",
            gateway="10.0.2.1"
        )
        response = stub.ChangeIP(request)
        print(f"Reboot Successful: {response.success}")
        print(f"Message: {response.message}")

if __name__ == '__main__':
    run()

