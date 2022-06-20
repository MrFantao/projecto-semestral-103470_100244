import socket
import json
import logging
import sys
import argparse
from PIL import Image, ImageGrab
import imagehash
import json
from io import BytesIO
import numpy
import pickle
from protocolo import CDProto, Get, List


class Client:
    def __init__(self, address, action, id=None):
        """ Initialize client."""
        self.addr = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(address)
        self.img = ""
        #print("Conectado")


        if action == "GET" and id != None:

            #msg = {"method":"GET", "args": {"id": id}}
            msg = CDProto.serializeJSON(Get(id))

            size_msg = str(len(msg))                            
            size_header = len(size_msg)                                          
            h = 'f'*(10-size_header) + size_msg                                          
            self.socket.send(h.encode('utf-8'))
            self.socket.send(msg)

            size = None
            header = self.socket.recv(4)
            size = int.from_bytes(header, 'big')
            bytesImage = None
            length = int(self.socket.recv(size).decode('utf-8'))

            for n in range(length):

                b = self.socket.recv(4096)

                if bytesImage is None:
                    bytesImage = b
                else:
                    bytesImage += b

            """for n in range(length):

                b = self.socket.recv(4096)
                #print(b)
                print(i)
                i += 1

                if bytesImage is None:
                    bytesImage = b
                else:
                    bytesImage += b"""

            #print(bytesImage)
            
            image = Image.open(BytesIO(bytesImage))
            image.show()
                


            """header = self.socket.recv(10)
            print(header.decode('utf-8'))
            size_msg = int(header.decode('utf-8').replace('f',''))
            #print(size_msg)

            path = self.socket.recv(size_msg).decode('utf-8')
            print(path)"""

            #msg = pickle.loads(pickled_msg)
            #print(msg)
            #imgBytes = base64.b64decode(msg)

            #img = Image.open(BytesIO(imgBytes))
            #img.show()

            """msg.save(stream, "JPG")
            img = stream.read()
            image.show()"""

            #print(msg)

        elif action == "LIST" and id is None:
            #msg = {"method":"LIST", "args": {}}
            msg = CDProto.serializeJSON(List())

            #json_msg = json.dumps(msg)
            size_msg = str(len(msg))                            
            size_header = len(size_msg)                                          
            h = 'f'*(10-size_header) + size_msg                                          
            self.socket.send(h.encode('utf-8'))
            self.socket.send(msg)

            header = self.socket.recv(10)
            size_msg = int(header.decode('utf-8').replace('f',''))

            json_msg = self.socket.recv(size_msg)
            msg = CDProto.unserializeJSON(json_msg)

            #print(msg)
            args = msg["args"]

            lst_img_hash = args["lst_img_hash"]

            print("Lista de todas as imagens existentes na rede:")

            for img_hash in lst_img_hash:
                print(img_hash)


        self.socket.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', required=True)
    parser.add_argument('-port', required=True)
    parser.add_argument('-m', required=True)
    parser.add_argument('-id', required=False)

    args = parser.parse_args()

    host = args.ip
    port = int(args.port)

    action = args.m
    img_id = args.id

    addr = (host, port)
    #print(img_id)
    if img_id == None:
        client = Client(addr, action)
    else:
        client = Client(addr, action, img_id)

    #client.get("ffdf1710000107df")

    # add object to DHT (this key is not on the first node -> remote search)
    # retrieve from DHT (this key is not on the first node -> remote search)