"""
Addressbook manipulation CLI-bot.

USAGE:
    --db file=db.json       -   Load JSON file on startup aka import initial DB
    --unattended file=None  -   Unattended mode. Process commands' file. See internal commands,
                                This mode can be used for automation processing of JSON files. Added just for fun.

Internal commands description:
    'insert "Firstname Lastname" phone1 phone2...phoneN'        -   insert record. If already exists insert phones that absent in contact
    'update "Firstname Lastname old" "Firstname Lastname new"'  -   Change contact name
    'update "Firstname Lastname" phone1 phone2...phoneN''       -   Replace stored phones with specified
    'delete "Firstname Lastname"'                               -   Remove contact by name
    'delete "Firstname Lastname" phone1 phone2...phoneN'        -   Remove specified phones in contact

    'delete_all'                        -   Clear DB
    'view       "Firstname Lastname"'   -   View contact
    'view_all   "Firstname Lastname"'   -   View all contact

    'load filename.json=db.json'    -   Append DB records from JSON
    'save filename.json=db.json'    -   Save DB to JSON

    JSON file example:
        [{'name': 'Sasha', 'phones': ['123', '456', '789']}, {'name': 'Vova', 'phones': ['123', '456', '789']}]
    For command aliases see argparser creation function - create_argument_parser()

    TODO: birthday processing
"""


import argparse
import json
from pathlib import Path
import re
import sys

from ab_lib import AddressBook
from ab_lib import Record
from ab_lib import Phone
from ab_lib import Name



"""Globals"""
ARGS = None
CONTACTS = AddressBook()


"""Error handler decorator"""
def error_handler(function):

    def wrapper(*args,**kwargs) -> str:
        result = ""
        try:
            result = function(*args,**kwargs)
        except KeyError as e:
            result = e
        except TypeError as e:
            result = e
        except Exception as e:
            result = e
        return result
    
    return wrapper


@error_handler
def load(args)-> str:
    db_file = None
    if args and args.file:
        db_file = args.file
    elif ARGS.db:
        db_file = ARGS.db
    if db_file and db_file.exists():
        with open(db_file, "r+") as db:
            records = json.load(db)
            if records:
                # CONTACTS = AddressBook() #.update(contacts)
                for record in records:
                    # for key,value in record.items():
                    CONTACTS[record["name"]] = Record(record["name"],record["phones"])
        return ""
    else:
        raise Exception(f"{db_file} not found.")


@error_handler
def save(args)-> str:
    db_file = None
    if args.file:
        db_file = args.file
    elif ARGS.db:
        db_file = ARGS.db
    if db_file:
        with open(db_file, "w+") as db:
            data = CONTACTS.toJSON()
            db.write(data)
        return ""
    else:
        raise Exception("File name isn't specified.")


def hello(args)-> str:
    return "How can I help you?"


def bye(args)-> str:
    return "Good bye!"


"""
    TODO: use regexp
    For now, just check for all chars is digits
"""
def check_phone(phone,raise_exception=True):
    result = phone.isdigit()
    if raise_exception:
        if not result:
            raise TypeError(f"Phone:{phone} is not valid.")
        else:
            return phone
    return result


"""DB functions"""
@error_handler
def insert(args)-> str:
    # Filter phone list with check_phone function
    phones = list(filter(lambda x: check_phone(x,False), args.phone))
    if phones:
        record = CONTACTS.get(args.name)
        if record:  # If contact exists append absent phone numbers
            error_phones = [] #phone numbers already present in contact
            for phone in phones:
                try:
                    record.phones += Phone(phone)
                except Exception as e:
                    error_phones.append(phone)
            if error_phones:
                raise KeyError(f"Phone numbers {error_phones} can't be duplicated.")
        else: # Add new contact
            record = Record(args.name,phones)
            CONTACTS[args.name] = record
    if len(phones) != len(args.phone): # Filtered out phone numbers from args
        error_phones = list(filter(lambda x: not check_phone(x,False), args.phone))
        raise TypeError(f"Phone numbers {error_phones} is not valid.")
    return ""

@error_handler
def update(args)-> str:
    # Filter phone list with check_phone function
    phones = list(filter(lambda x: check_phone(x,False), args.phone))
    record = CONTACTS.get(args.name)
    if record and len(args.phone) == 1 and not phones: # Update contact's name
        CONTACTS.pop(args.name)
        record.name = Name(args.phone[0])
        CONTACTS[args.phone[0]] = record
    else: # Replace contact's phone list with new one
        CONTACTS.pop(args.name)
        CONTACTS[args.name] = Record(args.name,phones)
        if len(phones) != len(args.phone): # Filtered out phone numbers from args
            error_phones = list(filter(lambda x: not check_phone(x,False), args.phone))
            raise TypeError(f"Phone numbers {error_phones} is not valid.")
    return ""


@error_handler
def delete(args)-> str:
    if args.phone:
        # Filter phone list with check_phone function
        phones = list(filter(lambda x: check_phone(x,False), args.phone))
        if phones: # If phone list specified on args, try to remove it
            record = CONTACTS[args.name]
            error_phones = []
            for phone in phones:
                try:
                    record.phones.pop(phone)
                except Exception as e:
                    error_phones.append(phone)
            if error_phones: # Phone numbers that absents in contacts
                raise KeyError(f"Phone numbers {error_phones} number not found.")
        if len(phones) != len(args.phone): # Filtered out phone numbers from args
            error_phones = list(filter(lambda x: not check_phone(x,False), args.phone))
            raise TypeError(f"Phone numbers {error_phones} is not valid.")
    else: # Just remove contact with name in args
        phone = CONTACTS.pop(args.name)
    return ""


@error_handler
def delete_all(args)-> str:
    CONTACTS.clear()
    return ""


@error_handler
def view(args)-> str:
    record = CONTACTS[args.name]
    if record:
        return f"{record}"
    return ""


@error_handler
def view_all(args)-> str:
    return f"{CONTACTS}"


def create_parser():

    exit_alias = ["good","bye","good_bye","close"]
    exit_on_error = False

    """Global parser options"""
    parser = argparse.ArgumentParser(
        exit_on_error = exit_on_error,
        description = "Addressbook manipulation CLI-bot.",
        formatter_class = argparse.RawTextHelpFormatter,
        epilog = "HELP:\n\
    --db file=db.json       -   Load JSON file on startup aka import initial DB\n\
    --unattended file=None  -   Unattended mode. Process commands' file. See internal commands,\n\
                                This mode can be used for automation processing of JSON files. Added just for fun.\n\
    \n\
    Internal commands description:\n\
    'insert \"Firstname Lastname\" phone1 phone2...phoneN'        -   insert record. If already exists insert phones that absent in contact\n\
    'update \"Firstname Lastname old\" \"Firstname Lastname new\"'  -   Change contact name\n\
    'update \"Firstname Lastname\" phone1 phone2...phoneN''       -   Replace stored phones with specified\n\
    'delete \"Firstname Lastname\"'                               -   Remove contact by name\n\
    'delete \"Firstname Lastname\" phone1 phone2...phoneN'        -   Remove specified phones in contact\n\
    \n\
    'delete_all'                      -   Clear DB\n\
    'view       \"Firstname Lastname\"' -   View contact\n\
    'view_all   \"Firstname Lastname\"' -   View all contact\n\
    \n\
    'load filename.json=db.json'    -   Append DB records from JSON\n\
    'save filename.json=db.json'    -   Save DB to JSON\n\
    JSON file example:\n\
        [{'name': 'Sasha', 'phones': ['123', '456', '789']}, {'name': 'Vova', 'phones': ['123', '456', '789']}]"
    )
    parser.add_argument(
        "--db",
        help = "Specify path to DB(JSON) file. By default: db.json",
        type = Path,
        metavar = "db.json",
        default = "db.json",
        required=False
    )

    parser.add_argument(
        "--unattended",
        help = "Unattended mode",
        type = Path,
        metavar = "stdin",
        default = None,
        required = False
    )

    """Internal commands' parser"""
    subparsers = parser.add_subparsers(dest = "command")
    
    parser_insert = subparsers.add_parser(
        "insert",
        exit_on_error = exit_on_error,
        aliases = ["i","add","a"],
        help = "Add contact or phone numbers to existing contact"
    )
    parser_insert.add_argument(
        "name",
        help = "Contact's name"
    )
    parser_insert.add_argument(
        "phone",
        nargs = "+",
        help = "Phone number"
    )
    parser_insert.set_defaults(func = insert)
    for action in parser_insert._actions: # Hook - Positional options can't be unrequired
        action.required = False

    parser_update = subparsers.add_parser(
        "update",
        exit_on_error = exit_on_error,
        aliases = ["u","change","c"],
        help = "Change contact's name or contact's phone numbers."
    )
    parser_update.add_argument(
        "name",
        help = "Contact's name"
    )
    parser_update.add_argument(
        "phone",
        nargs = "+",
        help = "Phone number or new contact's name"
    )
    parser_update.set_defaults(func = update)
    for action in parser_update._actions: # Hook - Positional options can't be unrequired
        action.required = False

    parser_delete = subparsers.add_parser(
        "delete",
        exit_on_error = exit_on_error,
        aliases = ["d","remove","r"],
        help = "Remove contact or specified contact's phone numbers"
    )
    parser_delete.add_argument(
        "name",
        help = "Contact's name"
    )
    parser_delete.add_argument(
        "phone",
        nargs= "*",
        help = "Phone number to remove from contact"
    )
    parser_delete.set_defaults(func = delete)
    for action in parser_delete._actions: # Hook - Positional options can't be unrequired
        action.required = False

    parser_delete_all = subparsers.add_parser(
        "delete_all",
        exit_on_error=False,
        aliases = ["da","clear"],
        help = "Clear DB"
    )
    parser_delete_all.set_defaults(func = delete_all)

    parser_view = subparsers.add_parser(
        "view",
        exit_on_error = exit_on_error,
        aliases = ["v","phone","p"],
        help = "View contact data"
    )
    parser_view.add_argument(
        "name",
        help = "Contact's name"
    )
    parser_view.set_defaults(func = view)

    parser_view_all = subparsers.add_parser(
        "view_all",
        exit_on_error = exit_on_error,
        aliases = ["va","show","show_all","sa"],
        help = "View all contacts in DB"
    )
    parser_view_all.set_defaults(func = view_all)

    parser_hello = subparsers.add_parser(
        "hello",
        exit_on_error = exit_on_error,
        aliases = ["h"]
    )
    parser_hello.set_defaults(func = hello)

    parser_bye = subparsers.add_parser(
        "exit",
        exit_on_error = exit_on_error,
        aliases = exit_alias,
        help = "Exit"
    )
    parser_bye.set_defaults(func = bye)

    parser_load = subparsers.add_parser(
        "load",
        exit_on_error = exit_on_error,
        aliases = ["l"],
        help = "Load data(JSON) from file and append it to DB"
    )
    parser_load.add_argument(
        "file",
        type = Path,
        help = "JSON file's path to load from"
    )
    parser_load.set_defaults(func = load)
    for action in parser_load._actions: # Hook - Positional options can't be unrequired
        action.required = False

    parser_save = subparsers.add_parser(
        "save",
        exit_on_error = exit_on_error,
        aliases = ["s"],
        help = "Save all data(JSON) to file"
    )
    parser_save.add_argument(
        "file",
        type = Path,
        help = "JSON file's path to save to"
    )
    parser_save.set_defaults(func = save)
    for action in parser_save._actions: # Hook - Positional options can't be unrequired
        action.required = False

    return parser, exit_alias

"""Parse command line"""
def parse_command(command: str) -> list:
    commands = re.split("\"|\'", command) # For correct parsing options enclosed by " or '
    if len(commands) == 1: # If no options enclosed by " or ', try by space
        commands = re.split(" ", command)
    commands = list(map(lambda x: x.strip(), commands))
    commands = list(filter(lambda x: len(x), commands)) # Remove empties
    return commands


def parse_commands(parser, commands: list):
    parsed_commands = None
    try:
        parsed_commands = parser.parse_args(commands)
    except SystemExit as e: # Hook
        result =  ""
    except argparse.ArgumentError as e:
        result = e
    # Execute command
    if parsed_commands:
        result = parsed_commands.func(parsed_commands)
    if result: print(result)
    return parsed_commands


def check_exit(command,exit_alias) -> bool:
    return command in exit_alias or command == "exit"


def main():

    global CONTACTS
    global ARGS

    parser, exit_alias = create_parser()
    ARGS = parser.parse_args()
    # Load DB
    try:
        load(None)
    except Exception as e:
        print(e)

    if ARGS.unattended:
        if ARGS.unattended.exists():
            with open(ARGS.unattended) as cmd_file:
                command = cmd_file.readline()
                while command:
                    commands = parse_command(command)
                    parsed_commands = parse_commands(parser, commands)
                    # exit
                    if parsed_commands:
                        if check_exit(parsed_commands.command,exit_alias):
                            break
                    command = cmd_file.readline()
        elif ARGS.unattended == "stdin":
            for command in sys.stdin:
                commands = parse_command(command)
                parsed_commands = parse_commands(parser, commands)
                # exit
                if parsed_commands:
                    if check_exit(parsed_commands.command,exit_alias):
                        break
    else:
        while True:
            command = input(">")
            commands = parse_command(command)
            parsed_commands = parse_commands(parser, commands)
            # exit
            if parsed_commands:
                if check_exit(parsed_commands.command,exit_alias):
                    break


if __name__ == "__main__":
    main()
