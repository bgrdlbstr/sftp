from enum import Enum, unique, auto


@unique
class PasswordHandlers(Enum):
    CyberArk = "CyberArk",
    PlainTextFile = "PlainTextFile"
    EncryptedFile = "EncryptedFile",
    EncryptedText = "EncryptedText",
    PlainText = "PlainText"


def get_cyberark(args):
    return None
#    raise Exception("CyberArk not yet supported")


def get_plaintext_file(args):
    return None
#    raise Exception("Plain Text File not yet supported")


def get_encrypted_file(args):
    return None
#    raise Exception("Encrypted File not yet supported")


def get_encrypted_text(args):
    return None
#    raise Exception("Encrypted Text not yet supported")


def get_plain_text(args):
    if len(args) > 1:
        raise Exception("Plain Text password handler only expects one arg - i.e. the password")
    return str(args[0])


def get_password_handler(requested_handler, *args):
    if type(requested_handler) is str:
        req_handler = PasswordHandlers(requested_handler)
    elif type(requested_handler) is PasswordHandlers:
        req_handler = requested_handler
    else:
        raise Exception("Invalid value in get_password_handler() '" % requested_handler % "'")

    return {
        PasswordHandlers.CyberArk: get_cyberark(args),
        PasswordHandlers.PlainTextFile: get_plaintext_file(args),
        PasswordHandlers.EncryptedFile: get_encrypted_file(args),
        PasswordHandlers.EncryptedText: get_encrypted_text(args),
        PasswordHandlers.PlainText: get_plain_text(args)
    }.get(req_handler, get_plain_text(args))
