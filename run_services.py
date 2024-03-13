from subprocess import Popen

# Start authentication service
authentication_service_process = Popen(['python3', 'src/authentication_service.py'])
routing_service_process = Popen(['python3', 'src/routing_service.py'])

# Wait for services to finish (Ctrl+C to stop)
try:
    authentication_service_process.wait()
    routing_service_process.wait()
except KeyboardInterrupt:
    authentication_service_process.terminate()
    routing_service_process.terminate()