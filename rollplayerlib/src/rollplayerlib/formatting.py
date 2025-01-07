import re
from typing import Optional, List
from .enums import ThresholdType, FormatType, FormatEnum
from .exceptions import RollException


class Threshold:
    def __init__(self, limit: int, threshold_type: ThresholdType):
        self.limit = limit
        self.threshold_type = threshold_type

    def passing(self, numbers: List[int]) -> List[bool]:
        if self.threshold_type == ThresholdType.GREATER:
            return [num >= self.limit for num in numbers]
        elif self.threshold_type == ThresholdType.LESS:
            return [num <= self.limit for num in numbers]
        elif self.threshold_type == ThresholdType.MAX:
            max_value = max(numbers)
            return [num == max_value for num in numbers]
        elif self.threshold_type == ThresholdType.MIN:
            min_value = min(numbers)
            return [num == min_value for num in numbers]
        elif self.threshold_type == ThresholdType.EQUALS:
            return [num == self.limit for num in numbers]
        elif self.threshold_type == ThresholdType.TOP:
            sorted_numbers = sorted(numbers, reverse=True)
            top_count = min(self.limit, len(numbers))
            top_values = set(sorted_numbers[:top_count])
            return [num in top_values for num in numbers]
        elif self.threshold_type == ThresholdType.BOTTOM:
            sorted_numbers = sorted(numbers)
            bottom_count = min(self.limit, len(numbers))
            bottom_values = set(sorted_numbers[:bottom_count])
            return [num in bottom_values for num in numbers]
        else:
            raise RollException("Invalid threshold type (how did you get here?)")


class Format:
    def __init__(self, format_type: FormatType, format_args: Optional[int] = None, threshold: Optional[Threshold] = None):
        self.format_type = format_type
        self.format_args = format_args
        self.threshold = threshold

    @classmethod
    def parse(cls, expression):
        formatting = Format(FormatType.FORMAT_DEFAULT, 20, None)
        format_regex = r'(' + '|'.join(re.escape(op.value) for op in FormatEnum) + r')'
        strip, *formats = re.split(format_regex, expression)
        idx = 0
        while idx < len(formats):
            format_char = formats[idx]
            if idx == len(formats) - 1:
                arg = False
            else:
                arg = formats[idx + 1]
                if re.match(format_regex, arg):
                    arg = False
            if arg == "":
                arg = False
            match format_char:
                case FormatEnum.LIST:
                    if arg:
                        formatting.format_type = FormatType.FORMAT_LIST_SPLIT
                        try:
                            formatting.format_args = int(arg)
                        except ValueError:
                            raise RollException("Attempted to split with non-integer")
                    else:
                        formatting.format_type = FormatType.FORMAT_LIST
                case FormatEnum.SUM:
                    formatting.format_type = FormatType.FORMAT_SUM
                case FormatEnum.GREATER:
                    if arg:
                        try:
                            formatting.threshold = Threshold(int(arg), ThresholdType.GREATER)
                        except ValueError:
                            raise RollException("Attempted to use > with non-integer")
                    else:
                        formatting.threshold = Threshold(int(arg), ThresholdType.MAX)
                case FormatEnum.LESS:
                    if arg:
                        try:
                            formatting.threshold = Threshold(int(arg), ThresholdType.LESS)
                        except ValueError:
                            raise RollException("Attempted to use < with non-integer")
                    else:
                        formatting.threshold = Threshold(int(arg), ThresholdType.MIN)
                case FormatEnum.EQUALS:
                    if arg:
                        try:
                            formatting.threshold = Threshold(int(arg), ThresholdType.EQUALS)
                            idx += 1
                        except ValueError:
                            raise RollException("Attempted to use == with non-integer")
                    else:
                        raise RollException("Attempted to use == without an argument")
                case FormatEnum.TOP:
                    if arg:
                        try:
                            formatting.threshold = Threshold(int(arg), ThresholdType.TOP)
                        except ValueError:
                            raise RollException("Attempted to use top with non-integer")
                    else:
                        formatting.threshold = Threshold(1, ThresholdType.TOP)
                case FormatEnum.BOTTOM:
                    if arg:
                        try:
                            formatting.threshold = Threshold(int(arg), ThresholdType.BOTTOM)
                        except ValueError:
                            raise RollException("Attempted to use bottom with non-integer")
                    else:
                        formatting.threshold = Threshold(1, ThresholdType.BOTTOM)
            idx += 2 if arg else 1
        return strip, formatting  # temporary!!!!!!!!!
