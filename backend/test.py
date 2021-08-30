class User



class Userlist(list):
    color: str
    name: str

    def __init__(self, kwargs=None):
        if kwargs is not None:
            for k, v in kwargs.items():
                setattr(self, k, v)

    def append(self, kwargs):
        super(Userlist, self).append(self.__init__(kwargs))



a = Userlist()
a.append({"b":1})
print(a)