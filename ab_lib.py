import calendar
import json
from collections import UserDict
from datetime  import datetime



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

    @property
    def value(self):
        return self.data

    @value.setter
    def value(self, data):
        if data.isnumeric():
            self.data = data
        else:
            raise Exception(f"Phone '{data}' is not valid.")


class Birthday(Field):
    @property
    def value(self)-> datetime:
        return self.data

    @value.setter
    def value(self, data: datetime):
        self.data = data

    # @value.setter
    # def value(self, data: str):
    #     try:
    #         birthday = datetime.strptime(data,"%Y.%M.%d")
    #         self.data = birthday
    #     except:
    #         raise Exception(f"{self.__class__.__name__} error: Can't create datetime from '{data}'.)")

    # @value.setter
    # def value(self, data, year = None: int, month = None: int, day = None: int):
    #     try:
    #         birthday = datetime(year, month, day)
    #         self.data = birthday
    #     except:
    #         raise Exception(f"{self.__class__.__name__} error: Can't create datetime from '{self.data}'.)")

"""dict as list with unique values - respect to dict"""
class UDict(UserDict):

    def __init__(self, key: str = None, value: Field = None) -> None:
        UserDict.__init__(self)
        self._current_data = 0
    # += operator
    def __iadd__(self, value: Field):
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

    # def __iter__(self):# -> Iterator[_KT]:
    #     return iter(self.data.values())
    
    # def __next__(self):
    #     return self.data.next()
    

"""
    Contact's storage class
"""
class Record():

    def __init__(self, name: str, phone = None, birthday: Birthday = None) -> None:
        self._name      = Name(name)
        self._phones    = UDict()
        self._birthday  = birthday

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
        result["name"]      = self.name.value
        result["phones"]    = self.phones.value if self.birthday else None
        result["birthday"]  = self.birthday.value if self.birthday else None
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

    @property
    def birthday(self):
        return self._birthday
    
    @birthday.setter
    def birthday(self, birthday: Birthday):
        self._birthday = birthday

    def days_to_birthday(self) -> int:
        if not self._birthday:
            return None
        now = datetime.now()
        # birthday = datetime(year = now.year, month = now.month, day = self._birthday.day)
        if self._birthday.value.day == 29 and self._birthday.value.month == 2 and not calendar.isleap(now.year):
            birthday = datetime(now.year,self._birthday.value.month,28)
        else:
            birthday = datetime(now.year,self._birthday.value.month,self._birthday.value.day)
        diff = birthday - now
        if diff.days < 0:
            year = birthday.year + 1
            if self._birthday.value.day == 29 and self._birthday.value.month == 2 and not calendar.isleap(year):
                birthday = datetime(year,self._birthday.value.month,28)
            else:
                birthday = datetime(year,birthday.month,birthday.day)
            diff = birthday - now
        return diff.days

    # def __iter__(self):# -> Iterator[_KT]:
    #     return self.phones.itervalues()
    
    # def __next__(self):
    #     return self.phones.next()

"""
    Record containier class
"""
class AddressBook(UDict):
    
    def __init__(self, record: Record = None) -> None:
        super().__init__()
        if record:
            self.data[record.name.datas] = record
    
     # += operator
    def __iadd__(self, value: Record):
        # v = value.value if isinstance(value,Field) else value
        self.__setitem__(value.name.value, value)
        return self

    def add_record(self, record: Record) -> None:
        if record:
            self.data[record.name.value] = record
    
    def iterator(self, count: int):
        records = []
        index = 0
        for record in self.data.values():
            records.append(record)
            index += 1
            if index >= count:
                yield records
                index = 0
                records = []
        if records:
            yield records
            index = 0
            records = []

def tests():
    record = Record("User",["111","222","333"],Birthday(datetime(year=1997,month=1,day=3)))
    print("Days to birthday:",record.days_to_birthday())
    record = Record("User",["111","222","333"],Birthday(datetime(year=2000,month=2,day=29)))
    print("Days to birthday:",record.days_to_birthday())
    # record = Record("User",["111","222","333"],Birthday(2000,2,29))
    # print("Days to birthday:",record.days_to_birthday())
    record = Record("User",["111","222","333"])
    print("Days to birthday:",record.days_to_birthday())

    record.add_phone(Phone("444"))
    # record.add_phone(Phone("333"))
    record.remove_phone(Phone("111"))
    # record.remove_phone(Phone("1111"))
    record.change_phone(Phone("333"),Phone("555"))
    # record.change_phone(Phone("888"),Phone("777"))
    for r in record.phones:
        print(r)
    
    ab = AddressBook()
    record = Record("User1",["111","222","333"])
    ab += record
    record = Record("User2",["111","222","333"])
    ab += record
    record = Record("User3",["111","222","333"])
    ab += record
    record = Record("User4",["111","222","333"])
    ab += record
    record = Record("User5",["111","222","333"])
    ab += record
    record = Record("User6",["111","222","333"])
    ab += record
    record = Record("User7",["111","222","333"])
    ab += record
    record = Record("User8",["111","222","333"])
    ab += record
    record = Record("User9",["111","222","333"])
    ab += record
    record = Record("User10",["111","222","333"])
    ab += record

    # records = ab.iterator(3)
    for records in ab.iterator(3):
        print("\n".join(str(record) for record in records))
    
    return

if __name__ == "__main__":
    # tests()
    pass