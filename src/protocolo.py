import json

class Message():
    pass

class Join(Message):

    def __init__(self, addr):
        self.addr = addr
        self.method = "JOIN"

    def get(self, addr):
        if addr == "method":
            return self.__repr__()["method"]
        return self.__repr__()["args"][addr]
    
    def __repr__(self):
        return {"method": self.method, "args": {"addr":self.addr}}

class Remove(Message):

    def __init__(self, img_hash):
        self.img_hash = img_hash
        self.method = "REMOVE"
    
    def get(self, img_hash):
        if img_hash == "method":
            return self.__repr__()["method"]
        return self.__repr__()["args"][img_hash]
    
    def __repr__(self):
        return {"method": self.method, "args": {"img_hash":self.img_hash}}

class ListRequest(Message):

    def __init__(self, addr):
        self.addr = addr
        self.method = "LIST_REQ"

    def get(self, addr):
        if addr == "method":
            return self.__repr__()["method"]
        return self.__repr__()["args"][addr]
    
    def __repr__(self):
        return {"method": self.method, "args": {"addr":self.addr}}

class ListReply(Message):

    def __init__(self, lst_img_hash):
        self.lst_img_hash = lst_img_hash
        self.method = "LIST_REP"
    
    def get(self, lst_img_hash):
        if lst_img_hash == "method":
            return self.__repr__()["method"]
        return self.__repr__()["args"][lst_img_hash]
    
    def __repr__(self):
        return {"method": self.method, "args": {"lst_img_hash":self.lst_img_hash}}

class NodeJoined(Message):

    def __init__(self, addr):
        self.addr = addr
        self.method = "NODE_JOINED"

    def get(self, addr):
        if addr == "method":
            return self.__repr__()["method"]
        return self.__repr__()["args"][addr]
    
    def __repr__(self):
        return {"method": self.method, "args": {"addr":self.addr}}

class JoinRequest(Message):

    def __init__(self, addr):
        self.addr = addr
        self.method = "JOIN_REQ"
    
    def get(self, addr):
        if addr == "method":
            return self.__repr__()["method"]
        return self.__repr__()["args"][addr]
    
    def __repr__(self):
        return {"method": self.method, "args": {"addr":self.addr}}

class Get(Message):

    def __init__(self, id):
        self.id = id
        self.method = "GET"
    
    def get(self, addr):
        if addr == "method":
            return self.__repr__()["method"]
        return self.__repr__()["args"][addr]
    
    def __repr__(self):
        return {"method": self.method, "args": {"id":self.id}}

class List(Message):

    def __init__(self):
        self.method = "LIST"
    
    def get(self, method):
        if method == "method":
            return self.__repr__()["method"]
    
    def __repr__(self):
        return {"method": self.method, "args": {}}

class ListReturn(Message):

    def __init__(self, lst_img_hash):
        self.lst_img_hash = lst_img_hash
        self.method = "LIST_RETURN"
    
    def get(self, lst_img_hash):
        if lst_img_hash == "method":
            return self.__repr__()["method"]
        return self.__repr__()["args"][lst_img_hash]
    
    def __repr__(self):
        return {"method": self.method, "args": {"lst_img_hash":self.lst_img_hash}}


class CDProto():


    @classmethod
    def serializeJSON(cls, Message):                                

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
        
        elif _method == "GET":
            _id = Message.get("id")

            msg = json.dumps({"method": _method, "args":{"id":_id}})

        elif _method == "LIST":

            msg = json.dumps({"method": _method, "args":{}})
        
        elif _method == "LIST_RETURN":
            lst_img_hash = Message.get("lst_img_hash")

            msg = json.dumps({"method": _method, "args":{"lst_img_hash":lst_img_hash}})

        elif _method == "LIST_REP":
            lst_img_hash = Message.get("lst_img_hash")

            msg = json.dumps({"method": _method, "args":{"lst_img_hash":lst_img_hash}})

        else:
            print("vazio")
            msg = json.dumps({})
            

        return msg.encode('utf-8')


    @classmethod
    def unserializeJSON(cls,data):
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
        
        elif _method == "GET":
            msg["args"]["id"] = data["args"]["id"]

        elif _method == "LIST":
            msg["args"] = data["args"]

        elif _method == "LIST_RETURN":
            msg["args"]["lst_img_hash"] = data["args"]["lst_img_hash"]
        
        elif _method == "LIST_REP":
            msg["args"]["lst_img_hash"] = data["args"]["lst_img_hash"]

        else:
            msg = {}
            
        return msg