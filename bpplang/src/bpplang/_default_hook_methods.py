from bpp_typing import *
from utils import safe_cut, char_length_to_bytes

def example_parser_hook(variables: BPPVariables, program_args: ProgramArguments, func_args: BPPFunctionArguments, parser_args: ParserArguments, prev_result: ResultType, prev_extras: ExtrasDictionary) -> ParsingHookReturn:
    ...


def _defaults(max_var_size: int) -> dict[str, ParsingHook]:
    hooks = {}
    
    def define_variable(variables: BPPVariables, program_args: ProgramArguments, func_args: BPPFunctionArguments, parser_args: ParserArguments, prev_result: ResultType, prev_extras: ExtrasDictionary) -> ParsingHookReturn:
        if len(str()) > max_var_size:
            raise MemoryError(f"The variable {safe_cut(func_args[0])} is too large: {safe_cut(prev_result[1])} (limit {char_length_to_bytes(max_var_size)})")
        variables[func_args[0]] = prev_result[1]
        return ["", prev_extras]
    hooks["d"] = define_variable
    
    def get_variable(variables: BPPVariables, program_args: ProgramArguments, func_args: BPPFunctionArguments, parser_args: ParserArguments, prev_result: ResultType, prev_extras: ExtrasDictionary) -> ParsingHookReturn:
        try:
            return [variables[func_args[0]], prev_extras]
        except KeyError:
            raise NameError(f"No variable by the name {safe_cut(func_args[0])} defined")
    hooks["v"] = get_variable
    
    def get_arg_singular(variables: BPPVariables, program_args: ProgramArguments, func_args: BPPFunctionArguments, parser_args: ParserArguments, prev_result: ResultType, prev_extras: ExtrasDictionary) -> ParsingHookReturn:
        if prev_result[1] >= len(program_args) or -prev_result[1] >= len(program_args) + 1:
            return ["", prev_extras]
        return [program_args[prev_result[1]], prev_extras]
    
    def get_args_all(variables: BPPVariables, program_args: ProgramArguments, func_args: BPPFunctionArguments, parser_args: ParserArguments, prev_result: ResultType, prev_extras: ExtrasDictionary) -> ParsingHookReturn:
        return [program_args, prev_extras]
    
    hooks["a"] = get_arg_singular
    hooks["aa"] = get_args_all
    return hooks