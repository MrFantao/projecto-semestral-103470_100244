import socket
import logging
import pickle
import sys
import argparse
import os
from PIL import Image, ImageGrab
import imagehash
import selectors
import json
from io import BytesIO
import numpy

from protocolo import Join, Remove, ListRequest, NodeJoined, JoinRequest, ListReturn, ListReply,CDProto


class Daemon():

    def __init__(self, address, path, dht_address=None, timeout=3):

        self.canceled = False
        self.addr = tuple(address)  # My address
        self.main_addr = dht_address
        self.connections = {}
        self.lst_nodes = []
        self.clientSock = None
        self.path = path
        self.lst_img_hash = []
        self.last_node = None
        self.lst_connected_addr = []

        print("Address: ", self.addr)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket.settimeout(timeout)

        lst_img = []

        for im in os.listdir(path):
            i = f"{path}/{im}"
            lst_img.append(i)


        self.imageCodes = {}                #Dicionário com as imagens e os respetivos HashCodes

        """Atribuir a cada imagem o seu hashcode e verifica repetidas na mesma pasta"""

        for im in lst_img:
            i = Image.open(im)
            
            img_hash = str(imagehash.average_hash(i))

            if img_hash not in self.imageCodes.values():
                self.imageCodes[im] = img_hash
            else:
                os.remove(im)
                print("foi removida uma imagem")

        self.lst_img_hash = list(self.imageCodes.values())


        #print("Image hashing done")
        #print(self.imageCodes)

        try:
            self.socket.bind(self.addr)
            self.socket.listen()
            self.socket.setblocking(False)
            print('\n.........Broker iniciado..............')
        except:
            print('\nNÃ£o foi possivel iniciar o broker!\n')


        self.sel = selectors.DefaultSelector()
        self.sel.register(self.socket, selectors.EVENT_READ, self.accept)

        if self.main_addr != None:

            self.connections[self.main_addr] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connections[self.main_addr].connect(self.main_addr)

            self.lst_connected_addr.append(self.main_addr)
            self.last_node = self.main_addr

            #msg = {"method":"JOIN", "args": {"addr":self.addr}}
            msg = Join(self.addr)
            self.send(self.connections[self.main_addr], msg)
            
            #msg = {"method":"REMOVE", "args": {"img_hash": img_hash}}
            msg = Remove(img_hash)

            for img_hash in self.imageCodes.values():

                self.send(self.connections[self.main_addr], msg)

                
            
            #msg = {"method":"LIST_REQ", "args": {"addr":self.addr}}
            msg = ListRequest(self.addr)
            self.send(self.connections[self.main_addr], msg)
    
    def accept(self,sock, mask):
        conn, addr = self.socket.accept()  # Should be ready
        print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.read)

    def get(self,conn,id):

        for key,value in self.imageCodes.items():
            
            if value == id:
                #print("checked")

                file_size = os.path.getsize(key)
                size_msg = str(len(str(file_size//4096 + 1)))                            
                size_header = len(size_msg)                                          
                h = 'f'*(4-size_header) + size_msg
                conn.send(h.encode('utf-8'))
                conn.send(str((file_size//4096 + 1)).encode('utf-8'))

                with open(key, 'rb') as f:
                    print("sending...")
                    while True:
                        b = f.read(4096)
                        if not b:
                            break
                        conn.send(b)
                        #print("envio feito ", i)

                return True

        else:
            return False
    

    def send(self,conn, Message):

        msg = CDProto.serializeJSON(Message)

        size_msg = str(len(msg))                            
        size_header = len(size_msg)                                          
        h = 'f'*(10-size_header) + size_msg

        conn.send(h.encode('utf-8'))
        conn.send(msg)

    def remove(self,img_hash):
        for key,value in self.imageCodes.items():
            if img_hash == value:
                os.remove(key)
                print("foi removida uma imagem")

    def run(self):
        """Run until canceled."""

        while not self.canceled:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def select_node(self): #política RoundRobin

        for n in range(len(self.lst_connected_addr)):
            if self.last_node == self.lst_connected_addr[-1]:
                self.last_node = self.lst_connected_addr[0]
                return self.last_node
            else:
                if self.last_node == self.lst_connected_addr[n]:
                    self.last_node = self.lst_connected_addr[n+1]
                    return self.last_node  


    def read(self,conn, mask):

        header = conn.recv(10)
        size_msg = int(header.decode('utf-8').replace('f',''))
        msg = conn.recv(size_msg)

        msg = CDProto.unserializeJSON(msg)

        args = msg["args"]

        print(msg)

        if msg["method"] == "JOIN":

            addr = tuple(args["addr"])
            
            self.connections[addr] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connections[addr].connect(addr)

            self.lst_connected_addr.append(addr)

            #msg = {"method":"LIST_REQ", "args": {"addr":self.addr}}
            msg = ListRequest(self.addr)
            self.send(self.connections[addr], msg)

            #msg = {"method":"NODE_JOINED", "args": {"addr":addr}}
            msg = NodeJoined(addr)

            for addr in self.connections.keys():
                self.send(self.connections[addr], msg)

        elif msg["method"] == "NODE_JOINED":
            
            #print("chegou aqui")
            
            addr = tuple(args["addr"])

            if addr != self.addr:
                self.connections[addr] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connections[addr].connect(addr)

                #msg = {"method":"JOIN_REQ", "args": {"addr":self.addr}}
                msg = JoinRequest(self.addr)
                self.send(self.connections[addr], msg)

                #msg = {"method":"LIST_REQ", "args": {"addr":self.addr}}
                msg = ListRequest(self.addr)
                self.send(self.connections[addr], msg)


        elif msg["method"] == "JOIN_REQ":
            addr = tuple(args["addr"])

            self.connections[addr] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connections[addr].connect(addr)

            self.lst_connected_addr.append(addr)

            for img_hash in self.imageCodes.values():

                #msg = {"method":"REMOVE", "args": {"img_hash": img_hash}}
                msg = Remove(img_hash)
                self.send(self.connections[addr], msg)
            
            for key,value in self.imageCodes.items():
                filename = os.path.basename(key)

                bytesImage = None
                with open(key, 'rb') as f:
                    while True:
                        b = f.read(4096)
                        if not b:
                            break
                        if bytesImage is None:
                            bytesImage = b
                        else:
                            bytesImage += b
                        #conn.send(b)
                        #print("envio feito ", i)

                #addr = self.select_node() #política RoundRobin
                #msg = {"method":"MAKE_COPY", "args": {"filename":filename}}

                #self.send(self.connections[addr], msg)

            #msg = {"method":"LIST_REQ", "args": {"addr":self.addr}}
            msg = ListRequest(self.addr)
            self.send(self.connections[addr], msg)

        elif msg["method"] == "REMOVE":

            img_hash = args["img_hash"]

            self.remove(img_hash)

        elif msg["method"] == "MAKE_COPY":
            print("vai fazer cópia")

            """header = conn.recv(10)
            size_msg = int(header.decode('utf-8').replace('f',''))
            print(size_msg)"""
            #imageBytes = conn.recv(size_msg)

            #print("recebido")

            #for addr in self.lst_nodes:




        elif msg["method"] == "GET":

            img_id = args["id"]

            #print("antes do inside")
            inside = self.get(conn, img_id)
            #print("depois do inside")

            """if not inside:
                msg = {"method":"GET_IMG", "args": {"img_id":img_id, "addr":self.addr}}

                print("está qui")
                #self.send(conn, msg)
                for addr in self.connections.keys():
                    print("ok")
                    self.send(self.connections[addr], msg)
            else:"""

            if not inside:
                msg = {"method":"GET_IMG", "args": {"img_id":img_id, "addr":self.addr}}
                for addr in self.connections.keys():
                    print("ok")
                    self.send(self.connections[addr], msg)
                
                """size = None
                header = conn.recv(4)
                size = int.from_bytes(header, 'big')
                bytesImage = None
                length = int(conn.recv(size).decode('utf-8'))

                i = 0
                for n in range(length):

                    b = conn.recv(4096)
                #print(b)
                    print(i)
                    i += 1

                    if bytesImage is None:
                        bytesImage = b
                    else:
                        bytesImage += b
                    
                    print(bytesImage)
                
                else:"""
                

            self.sel.unregister(conn)
            conn.close()
        
        elif msg["method"] == "GET_IMG":
            print("vem aqui")
            img_id = args["img_id"]

            inside = self.get(conn, img_id)
        
        elif msg["method"] == "LIST":

            print("cehgou ao list")
            print(self.lst_img_hash)

            lst_img_hash = self.lst_img_hash

            #msg = {"method":"LIST_RETURN", "args": {"lst_img_hash":lst_img_hash}}
            msg = ListReturn(lst_img_hash)
            self.send(conn, msg)

            self.sel.unregister(conn)
            conn.close()
        
        elif msg["method"] == "LIST_REQ":

            addr = tuple(args["addr"])

            lst_img_hash = list(self.imageCodes.values())

            #msg = {"method":"LIST_REP", "args": {"lst_img_hash":lst_img_hash}}
            msg = ListReply(lst_img_hash)
            self.send(self.connections[addr], msg)


        elif msg["method"] == "LIST_REP":

            lst_img_hash = args["lst_img_hash"]

            self.lst_img_hash = self.lst_img_hash + lst_img_hash

        print("--------------------------------------------------")

"""
    def serializeJSON(self, Message):                                

        _method = Message.get("method")
        
        if _method == "JOIN":
            addr = Message.get("addr")

            msg = json.dumps({"method": _method, "args":{"addr":addr}})

        elif _method == "NODE_JOINED":
            addr = Message.get("addr")

            msg = json.dumps({"method": _method, "args":{"addr":addr}})
        
        elif _method == "REMOVE":
            img_hash = Message.get("img_hash")

            msg = json.dumps({"method": _method, "args":{"img_hash":img_hash}})
        
        elif _method == "LIST_REQ":
            addr = Message.get("addr")

            msg = json.dumps({"method": _method, "args":{"addr":addr}})

        elif _method == "JOIN_REQ":
            addr = Message.get("addr")

            msg = json.dumps({"method": _method, "args":{"addr":addr}})
        else:
            print("vazio")
            msg = json.dumps({})
            

        return msg.encode('utf-8')

    def unserializeJSON(self,data):
        data = data.decode('utf-8')
        data = json.loads(data)
        _method = data["method"]

        msg = {}
        msg["method"] = _method
        msg["args"] = {}

        if _method == "JOIN":
            msg["args"]["addr"] = data["args"]["addr"]

        elif _method == "NODE_JOINED":
            msg["args"]["addr"] = data["args"]["addr"]
        
        elif _method == "REMOVE":
            msg["args"]["img_hash"] = data["args"]["img_hash"]
        
        elif _method == "LIST_REQ":
            msg["args"]["addr"] = data["args"]["addr"]

        elif _method == "JOIN_REQ":
            msg["args"]["addr"] = data["args"]["addr"]
        else:
            msg = {}
        
        return msg


"""


def main(address,path):

    if args.port[0] == 5000:
        daemon = Daemon(('localhost', args.port[0]), path)
    else:
        daemon = Daemon(('localhost', args.port[0]), path, ('localhost', 5000))

    daemon.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path', metavar='PATH', type=str, nargs='+',
                    help='path for image folder')
    parser.add_argument('port', metavar='PORT', type=int, nargs='+',
                    help='port for daemon')

    args = parser.parse_args()

    main(args.port[0], args.path[0])
