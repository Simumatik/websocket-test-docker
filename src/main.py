# Thirdparty imports
from threading import Thread
from SimpleWebSocketServer import SimpleWebSocketServer, SimpleSSLWebSocketServer, WebSocket
import json
from collections import deque
from datetime import datetime
import ssl
import time


IP = "0.0.0.0"
PORT = 4848
USE_SSL = False
FPS = 50.0 # FPS = 1/calback period

# -----------------------------------------------------------------------------
# Global
WebSocketConnections = []

# WebSocket Server
class WebSocket_server(WebSocket):

    # Every time a msg is received by the socket this is executed
    def handleMessage(self):
        # Send data
        self.msg_queue.append(self.data)
        

    # Every time a client is connected this is executed
    def handleConnected(self):
        # Log
        print(f"{self.address} Connected")
        # Append connection
        global WebSocketConnections
        WebSocketConnections.append(self)
        # Data queue
        self.msg_queue = deque([])
        self.callback_period = 1.0/FPS
        self.last_callback = 0.0
        self.running = False
        self.callback_counter = 0


    # Every time a client is disconnected this is executed
    def handleClose(self):
        # Log
        print(f'Connection with {self.address} closed')
        # Remove connection
        global WebSocketConnections
        WebSocketConnections.remove(self)


# -----------------------------------------------------------------------------
# WebSocket Thread method
WebSocketServer = None

def WebSocket_thread():
    global WebSocketServer
    if USE_SSL:
        WebSocketServer = SimpleSSLWebSocketServer(IP, PORT, WebSocket_server, selectInterval = 0.001, certfile="./cert.pem", keyfile ="./key.pem", version=ssl.PROTOCOL_TLSv1_2)
    else:
        WebSocketServer = SimpleWebSocketServer(IP, PORT, WebSocket_server, selectInterval = 0.001)
    try:
        WebSocketServer.serveforever()
    except:
        pass
    print("Websocket server closed.")



if __name__ == "__main__":
    # Launch WebSocket Server
    t = Thread(target=WebSocket_thread, daemon=True)
    t.start()
    print(f"Server started at {IP}:{PORT}")

    while True:
        # Loop connections
        for connection in WebSocketConnections:
            
            # Check if message received
            if connection.msg_queue:
                # Get message data
                try:
                    msg = connection.msg_queue.popleft()
                    req = json.loads(msg).get('request', None)
                except Exception as e:
                    print(f"Wrong request received: {msg}")
                print(f"request received: {req}")

                # Process request
                if req == 'start':
                    connection.running = True
                elif req == 'stop':
                    connection.running = False
                
            # Check if there is data to be sent
            if connection.running:
                now = time.time()
                # Send callback if period completed
                if (now-connection.last_callback)>=connection.callback_period:
                    connection.callback_counter += 1
                    connection.last_callback = now
                    connection.sendMessage(json.dumps({'ts':str(datetime.utcnow().isoformat()), 'counter': connection.callback_counter}))
