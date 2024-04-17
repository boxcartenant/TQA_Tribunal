import os

dbfile = "TribunalDB.txt"

class Database:
    def __init__(self, filename):
        self.filename = filename
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                key = None
                value = ''
                for line in file:
                    line = line.strip()
                    if '([)]' in line:
                        if key is not None:
                            self.data[key] = value.strip()
                        key, value = line.split('([)]', 1)
                        key = key.strip()
                        if value.strip() == ">":
                            value += ' '
                    else:
                        if line.strip() == ">":
                            line += ' '
                        value += '\n' + line.strip()+' '
                if key is not None:
                    self.data[key] = value

    def save(self):
        with open(self.filename, 'w') as file:
            for key, value in self.data.items():
                file.write(f"{key}([)]{value}\n")

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save()

    def __delitem__(self, key):
        del self.data[key]
        self.save()

    def keys(self):
        return list(self.data.keys())

    def prefix(self, prefix):
        return [key for key in self.data.keys() if key.startswith(prefix)]

db = Database(dbfile)
