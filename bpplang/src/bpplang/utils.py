import numbers
from typing import Any

def safe_cut(str: str, length=25) -> str:
    if len(str) <= length:
        return str
    return str[:length-4] + "..."

def char_length_to_bytes(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    unit_index = 0

    while size_in_bytes >= 1000 and unit_index < len(units) - 1:
        size_in_bytes /= 1000
        unit_index += 1

    if unit_index == 0:
        return f"{int(size_in_bytes)} bytes"
    else:
        return f"{size_in_bytes:.2f}{units[unit_index]}"
    
def raise_func(exc):
    raise exc

def is_whole(number: int | float):
    number = float(number)
    if isinstance(number, int):
        return True
    elif isinstance(number, float):
        return number.is_integer()
    return False

def is_number(number: Any):
    try: 
        number = float(number)
        return True
    except: 
        return False
    
def express_array(list):
	str_form = " ".join(["\"" + str(a) + "\"" for a in list])
	return f'[ARRAY {str_form}]'