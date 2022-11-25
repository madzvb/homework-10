import json
from collections import UserDict



class Field:
    def __init__(self, data: object) -> None:
        self._data = data

    def __str__(self) -> str:
        return str(self._data)

    def __eq__(self, data: object) -> bool:
        return self._data == data

    # @property
    # def data(self):
    #     return self._data

    @property
    def datas(self):
        return self._data
    
    @datas.setter
    def datas(self, data):
        self._data = data
    
    def toJSON(self):
        return self._data
    # def __hash__(self) -> int:
    #     print(hash(str(self.value)))
    #     return hash(str(self.value))


class Name(Field):
    # _name =  "Name"
    pass


class Phone(Field):

    def __init__(self, data: str) -> None:
        super().__init__(data)

    def normalized(self) -> str:
        return self._data

    def __eq__(self, data: str) -> bool:
        return self.normalized() == data

    # def __str__(self):
    #     return str(self.data)
   # def __hash__(self) -> int:
    #     print(hash(self.normalized()))
    #     return hash(self.normalized())

"""dict as list with unique values - respect to dict"""
class UDict(UserDict):

    def __init__(self, key: str = None, value: Field = None) -> None:
        UserDict.__init__(self)
    # += operator
    def __iadd__(self, value: Field = None):
        # v = value.value if isinstance(value,Field) else value
        self.__setitem__(value.datas, value)
        return self
    # []
    def __getitem__(self, key: str):
        if key in self.data:
            return self.data[key]
        else:
            raise KeyError(f"{self.__class__.__name__}:'{key}' is not found.")
    # []=
    def __setitem__(self, key: str, value: Field):
        if not key in self.data:
            self.data[key] = value # Add data
        else:
            if not value.datas in self.data: # Update data
                self.data.pop(key) # Remove old data
                self.data[value.datas] = value # Add new data
            else:
                raise KeyError(f"{self.__class__.__name__}:'{value.datas}' can't be duplicated.")
    
    def __str__(self):
        return f"{self.datas}"

    """Convert to native types. Used for serialization and to string convertion"""
    @property
    def datas(self):
        values = []
        for value in self.data.values():
            values.append(value.datas)
        return values
    
    # @datas.setter
    # def datas(self,data):
    #     pass # raise NotImplementedError(self)

    def toJSON(self):
        return json.dumps(self.datas)

"""
    Contact's storage class
"""
class Record():

    def __init__(self, name: str, phone = None) -> None:
        self._name      = Name(name)
        self._phones    = UDict()

        if isinstance(phone,Phone):
            self._phones[phone.datas] = phone
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
    def datas(self):
        datas = {}
        datas["name"]   = self.name.datas
        datas["phones"] = self.phones.datas
        return datas
    
    @property
    def phones(self):
        return self._phones
    
    @phones.setter
    def phones(self, phones: UDict):
        self._phones = phones

    def toJSON(self):
        return json.dumps(self.datas)
    

    def __str__(self):
        return f"{self.datas}"

    # def add_phone(self, phone: Phone) -> None:
    #     if not phone.value in self.data:
    #         self.data[phone.value] = phone
    #     else:
    #         raise KeyError(f"Phone:'{phone}' can't be duplicated.")

    # def remove_phone(self, phone: Phone) -> None:
    #     if phone.value in self.data:
    #         self.data.pop(phone.value)
    #     else:
    #         raise KeyError(f"Phone:'{phone}' is not found.")

    # def change_phone(self, phone_old: Phone, phone_new: Phone) -> None:
    #     if not phone_new.value in self.data:
    #         if phone_old.value in self.data:
    #             self.data.pop(phone_old.value)
    #             self.data[phone_new.value] = phone_new
    #         else:
    #             raise KeyError(f"Phone:'{phone_old}' is not found.")
    #     else:
    #         raise KeyError(f"Phone:'{phone_new}' can't be duplicated.")

"""
    Record containier class
"""
class AddressBook(UDict):
    
    def __init__(self, record: Record = None) -> None:
        super().__init__()
        if record:
            self.data[record.name.datas] = record
    
    # def add_record(self, record: Record) -> None:
    #     self.data[record.name.data] = record

    """Convert to native types. Used for serialization and to string convertion"""
    @property
    def datas(self):
        return super().datas

    def __str__(self):
        result = f"{self.datas}"
        return result
