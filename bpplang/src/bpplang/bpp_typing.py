from typing import Any, Callable

type BPPVariables = dict[str, Any]
type ProgramArguments = list[str]
type BPPFunctionArguments = list[Any]
type ParserArguments = dict[str, Any]
type ResultType = Any
type OutputType = str
type ExtrasDictionary = dict[Any, Any]
type ParsingHookReturn = tuple[ResultType, ExtrasDictionary]
type PreExitHookReturn = tuple[OutputType, ExtrasDictionary]
type ParsingHook = Callable[[BPPVariables, ProgramArguments, BPPFunctionArguments, ParserArguments, ResultType, ExtrasDictionary], ParsingHookReturn]
type PreExitHook = Callable[[BPPVariables, ProgramArguments, ParserArguments, OutputType, ExtrasDictionary], ParsingHookReturn]