import re
p = re.compile(r'^\w+$')
def is_valid_uuid(uuid:str):
    l = uuid.split('-')
    first, second, third, fourth, last = l
    if len(l) == 5:
        if len(first) != 8:
            return False
        if len(second) != 4 :
            return False
        if len(third) != 4 :
            return False
        if len(fourth) != 4:
            return False
        if len(last) != 12:
            return False
        for element in l:
            if not p.match(element):
                return False
        return True
    else:
        return False
