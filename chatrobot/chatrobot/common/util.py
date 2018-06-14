#encoding:utf-8
def newServerXlsxByLocalXlsx(local_file, server_file):
    with open(server_file, 'wb') as f:
         for line in local_file.chunks():
             f.write(line)

def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

def utf_string(s):
    if isinstance(s, unicode):
        return s.encode("utf-8", "ignore")
    return str(s)
