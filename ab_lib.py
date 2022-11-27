import json
from collections import UserDict



class Field:
    def __init__(self, data) -> None:
        self.data = data

    def __str__(self) -> str:
        return str(self.data)

    def __eq__(self, data) -> bool:
        return self.data == data

    @property
    def value(self):
        return self.data
    
    @value.setter
    def value(self, data):
        self.data = data
    
    def toJSON(self):
        return self.data
    # def __hash__(self) -> int:
    #     print(hash(str(self.value)))
    #     return hash(str(self.value))


class Name(Field):
    pass


class Phone(Field):
    pass


"""dict as list with unique values - respect to dict"""
class UDict(UserDict):

    def __init__(self, key: str = None, value: Field = None) -> None:
        UserDict.__init__(self)
    # += operator
    def __iadd__(self, value: Field = None):
        # v = value.value if isinstance(value,Field) else value
        self.__setitem__(value.value, value)
        return self
    # []
    def __getitem__(self, key: str):
        if key in self.data:
            return self.data[key]
        else:
            raise KeyError(f"{self.__class__.__name__} error:Data '{key}' is not found.")
    # []=
    def __setitem__(self, key: str, value: Field):
        if not key in self.data:
            self.data[key] = value # Add data
        else:
            if not value.value in self.data: # Update data
                self.data.pop(key) # Remove old data
                self.data[value.value] = value # Add new data
            else:
                raise KeyError(f"{self.__class__.__name__} error:'Data {value.value}' can't be duplicated.")
    
    def __str__(self):
        return f"{self.value}"

    """Convert to native types. Used for serialization and to string convertion"""
    @property
    def value(self):
        result = []
        for value in self.data.values():
            result.append(value.value)
        return result
    
    # @datas.setter
    # def datas(self,data):
    #     pass # raise NotImplementedError(self)

    def toJSON(self):
        return json.dumps(self.value)


"""
    Contact's storage class
"""
class Record():

    def __init__(self, name: str, phone = None) -> None:
        self._name      = Name(name)
        self._phones    = UDict()

        if isinstance(phone,Phone):
            self._phones[phone.value] = phone
        elif isinstance(phone,list):
            for p in phone:
                self._phones[p] = Phone(p)
        else:
            self._phones[phone] = Phone(phone)

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name: Name):
        self._name = name

    """Convert to native types. Used for serialization and to string convertion"""
    @property
    def value(self):
        result = {}
        result["name"]   = self.name.value
        result["phones"] = self.phones.value
        return result
    
    @property
    def phones(self):
        return self._phones
    
    @phones.setter
    def phones(self, phones: UDict):
        self._phones = phones

    def toJSON(self):
        return json.dumps(self.value)
    

    def __str__(self):
        return f"{self.value}"

    def add_phone(self, phone: Phone) -> None:
        self.phones += phone

    def remove_phone(self, phone: Phone) -> None:
        self.phones.pop(phone.value)

    def change_phone(self, phone_old: Phone, phone_new: Phone) -> None:
        if not phone_new.value in self.phones:
            self.phones.pop(phone_old.value)
            self.phones[phone_new.value] = phone_new


"""
    Record containier class
"""
class AddressBook(UDict):
    
    def __init__(self, record: Record = None) -> None:
        super().__init__()
        if record:
            self.data[record.name.datas] = record
    
    def add_record(self, record: Record) -> None:
        if record:
            self.data[record.name.value] = record

def tests():
    record = Record("User",["111","222","333"])
    record.add_phone(Phone("444"))
    # record.add_phone(Phone("333"))
    record.remove_phone(Phone("111"))
    # record.remove_phone(Phone("1111"))
    record.change_phone(Phone("333"),Phone("555"))
    # record.change_phone(Phone("888"),Phone("777"))

if __name__ == "__main__":
    tests()