from _default_hook_methods import _defaults
from bpp_typing import ParsingHook, PreExitHook


PARSING_HOOKS: dict[str, ParsingHook] = _defaults(1_000_000)
# Hooks in the form of function(VARIABLES, program args, b++ function args, parser args, result, extras dictionary) -> new result, new extras dictionary [take care not to override the dict]

PRE_EXIT_HOOKS: list[PreExitHook] = []