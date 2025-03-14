

from hooks import PARSING_HOOKS, PRE_EXIT_HOOKS
from utils import safe_cut, raise_func, is_whole, express_array
from functions import FUNCTIONS
import re, copy
from time import time as timenow

def str_array(s):
    out = "["
    for x in s:
        if type(x) == list:
            out += str_array(x)+', '
        else:
            out += "'"+str(x).replace('\\', '\\\\').replace("'", "\\'")+"', "
    return out[:-2]+"]"
    
def undo_str_array(s):
    
    if s[:1] == "[": s = s[1:]
    if s[-1:] == "]": s = s[:-1]

    is_quote = False
    bracket_count = 0
    is_escaped = False
    outlist = []
    current_append = ""
    for char in s:
        
        if char == "'" and not is_escaped and bracket_count == 0:
            is_quote = not is_quote
            if not is_quote:
                outlist.append(current_append)
                current_append = ""
            continue
        
        if char == "\\" and is_quote and not is_escaped and bracket_count == 0:
            is_escaped = True
            continue
        
        if char == "[" and not is_quote:
            bracket_count += 1
            continue
        if char == "]" and not is_quote:
            bracket_count -= 1
            if bracket_count == 0:
                outlist.append(undo_str_array(current_append))
                current_append = ""
            continue
        
        if is_quote or char not in " ,":
            current_append += char
            is_escaped = False
    return outlist

def run_bpp_program(code, p_args, **parserargs):
    # Pointers for tag and function organization
    tag_level = 0
    tag_code = []
    tag_globals = {}
    tag_str = lambda: ' '.join([str(s) for s in tag_code])
    buttons_to_add = []
    extras = {}
    debug_values = ""

    backslashed = False    # Flag for whether to unconditionally escape the next character
    
    functions = {}    # Dict flattening a tree of all functions to be evaluated

    current = ["", False] # Raw text of what's being parsed right now + whether it's a string

    output = "" # Stores the final output of the program

    goto = 0 # Skip characters in evaluating the code
        
    for ind, char in enumerate(list(code)):
        normal_case = True

        if ind < goto:
            continue

        if backslashed:
            if tag_code == []:
                output += char
            else:
                current[0] += char
            
            backslashed = False
            continue

        if char == "\\":
            backslashed = True
            continue

        if char == "[" and not current[1]:
            tag_level += 1

            if tag_level == 1:
                try:
                    tag_code = [max([int(k) for k in functions if is_whole(k)]) + 1]
                except ValueError:
                    tag_code = [0]
                
                output += "{}"

                found_f = ""

                for f_name in FUNCTIONS.keys():
                    try:
                        attempted_f = ''.join(code[ind+1:ind+len(f_name)+2]).upper()
                        if attempted_f == f_name + " ":
                            found_f = f_name
                            goto = ind + len(f_name) + 2
                        elif attempted_f == f_name + "]":
                            found_f = f_name
                            goto = ind + len(f_name) + 1
                    except IndexError: pass
                
                if found_f == "":
                    end_of_f = min(code.find(" ", ind+1), code.find("]", ind+1))
                    called_f = ''.join(code[ind+1:end_of_f])
                    raise NameError(f"Function {called_f} does not exist")
                
                functions[tag_str()] = [found_f]
            
            else:
                old_tag_code = tag_str()
                
                k = 1
                while old_tag_code + f" {k}" in functions.keys():
                    k += 1

                new_tag_code = old_tag_code + f" {k}"

                found_f = ""

                for f_name in FUNCTIONS.keys():
                    try:
                        attempted_f = ''.join(code[ind+1:ind+len(f_name)+2]).upper()
                        if attempted_f == f_name + " ":
                            found_f = f_name
                            goto = ind + len(f_name) + 2
                        elif attempted_f == f_name + "]":
                            found_f = f_name
                            goto = ind + len(f_name) + 1
                    except IndexError: pass
                
                if found_f == "":
                    end_of_f = min(code.find(" ", ind+1), code.find("]", ind+1))
                    called_f = ''.join(code[ind+1:end_of_f])
                    raise NameError(f"Function {called_f} does not exist")

                functions[new_tag_code] = [found_f]
                functions[tag_str()].append((new_tag_code,))

                tag_code.append(k)
            
            normal_case = False
        
        if char == "]" and not current[1]:
            if current[0] != "":
                functions[tag_str()].append(current[0])
                current = ["", False]
            tag_level -= 1
            normal_case = False
        
        if char in " \n":
            if not current[1] and tag_level != 0:
                if current[0] != "":
                    functions[tag_str()].append(current[0])
                    current = ["", False]
                normal_case = False
        
        if char in '"“”':
            if current[0] == "" and not current[1]:
                current[1] = True
            elif current[1]:
                functions[tag_str()].append(current[0])
                current = ["", False]
            normal_case = False
        
        if normal_case:
            if tag_level == 0: output += char
            else: current[0] += char
        
        tag_code = tag_code[:tag_level]
        tag_code += [1] * (tag_level - len(tag_code))

    VARIABLES = {}

    base_keys = [k for k in functions if is_whole(k)]

    type_list = [int, float, str, list]

    match = re.finditer("(?i)\[global var \w*?\]", code)
    found_vars = []
    for var in match:
        var = var[0].replace("]", "").replace("\n", " ").strip().split(" ")[-1]
        found_vars.append(var)
    
    def var_type(v):
        try:
            return type_list.index(type(v))
        except IndexError:
            raise TypeError(f"Value {safe_cut(v)} could not be attributed to any valid data type")
    
    def evaluate_result(k, extras={}):
        v = functions[k]

        if type(v) == tuple:
            k1 = v[0]
            functions[k] = evaluate_result(k1, extras=extras)
            return functions[k]
        
        args = v[1:]

        for i, a in enumerate(args):
            if v[0] == "IF" and is_whole(v[1]) and int(v[1]) != 2-i:
                continue
            if type(a) == tuple:
                k1 = a[0]
                functions[k][i+1] = evaluate_result(k1, extras=extras)
        
        args = v[1:]

        result = FUNCTIONS[v[0]](*args)

        # Tuples indicate special behavior necessary
        if type(result) == tuple:
            hook = PARSING_HOOKS.get(result[0], lambda: raise_func(LookupError(f"Parser op {result[0]} invalid.")))
            result, extras = hook(VARIABLES, p_args, args, parserargs, result, extras)
        functions[k] = result
        return result

    for k in base_keys:
        evaluate_result(k, extras=extras)
    
    for k in base_keys:
        if type(functions[k]) == tuple:
            evaluate_result(k, extras=extras)

    results = []
    for k, v in functions.items():
        if is_whole(k):
            if type(v) == list: v = express_array(v)
            results.append(v)

    for hook in PRE_EXIT_HOOKS:
        output, extras = hook(VARIABLES, p_args, parserargs, output, extras)
    
    output = output.replace("{}", "\t").replace("{", "{{").replace("}", "}}").replace("\t", "{}")

    return [output.format
    (*results).replace("\v", "{}")+debug_values,buttons_to_add]

if __name__ == "__main__":
    program = input("Program:\n\t")
    print("\n")
    program = program.replace("{}", "\v")
    print(run_bpp_program(program, [])[0])