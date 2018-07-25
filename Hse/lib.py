import base64

def decodif(value): 
    b = base64.b64decode(value.encode('utf-8')).decode("utf-8", "ignore")
    c = base64.b64decode(b).decode("utf-8", "ignore")
    d = base64.b64decode(c).decode("utf-8", "ignore")
    return d

def encoder(value): 
    a = base64.b64encode(bytes(value, "utf-8"))
    b = base64.b64encode(bytes(a.decode('utf-8'), "utf-8"))
    c = base64.b64encode(bytes(b.decode('utf-8'), "utf-8"))
    return c.decode('utf-8')