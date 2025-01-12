from abc import ABC, abstractmethod
import random
from typing import Generic, TypeVar, List

from .config import MAX_DICE
from .enums import OperationEnum
from .exceptions import BonusParseException

ABCBonusTypeVar = TypeVar('ABCBonusTypeVar', bound='ABCBonus')


class ABCBonus(ABC, Generic[ABCBonusTypeVar]):
    @abstractmethod
    def apply_bonus(self, rolled_dice: List[int]) -> List[int]: ...
    
    @property
    def value(self) -> float | int: ...

    @classmethod
    @abstractmethod
    def parse(cls, input_string: str) -> ABCBonusTypeVar: ...


class Bonus(ABCBonus):
    def __init__(self, operation, bonus_value):
        self.operation = operation
        self.bonus_value = bonus_value
    
    @property
    def value(self):
        if type(self.bonus_value) == tuple:
            return sum([random.randint(1, self.bonus_value[1]) for _ in range(self.bonus_value[0])])
        return self.bonus_value

    def __repr__(self):
        return f"Bonus(operation={self.operation}, bonus_value={self.bonus_value})"

    def apply_bonus(self, rolled_dice: List[int]) -> List[int]:
        new_dice = []
        for i in rolled_dice:
            if self.operation == "+":
                new_dice.append(i + self.value)
            if self.operation == "-":
                new_dice.append(i - self.value)
            if self.operation == "/":
                try:
                    new_dice.append(i / self.value)
                except ZeroDivisionError as e:
                    raise ZeroDivisionError("You can't divide rolls by zero!")
            if self.operation == "*":
                new_dice.append(i * self.value)
            if self.operation == "^":
                new_dice.append(i ** self.value)
            if self.operation == "%":
                new_dice.append(i % self.value)
        return new_dice

    @classmethod
    def parse(cls, input_string) -> List['Bonus']:
        bonuses = []
        current_val = ''
        current_op = None

        for char in input_string:
            if char in [op.value for op in OperationEnum]:  # Check if char is an operation
                if current_val:  # If there's a number buffered, create a Bonus
                    bonuses.append(Bonus(current_op, float(current_val)))
                    current_val = ''  # Reset current number
                current_op = OperationEnum(char)  # Set current operation
            else:
                current_val += char  # Buffer the number

        # Handle the last buffered number
        if current_val and current_op:
            try:
                current_val = float(current_val)
            except ValueError as e:
                try:
                    if "d" in current_val:
                        if current_val.startswith('d'):
                            count, sides = 1, int(current_val[1:])
                        else:
                            count, sides = current_val.split('d')
                            count = int(count)
                            if count > int(MAX_DICE / 10):
                                raise MemoryError(f"You can't roll more than {int(MAX_DICE / 10):,} dice for a subroll! (Tried rolling {count:,} dice)")
                            sides = int(sides)
                    else:
                        raise ValueError
                    current_val = (count, sides)
                except ValueError as e:
                    raise ValueError(f"The number provided to be parsed as a bonus is unparsable! ({current_val})")
            bonuses.append(Bonus(current_op, current_val))

        return bonuses


class TargetedBonus(ABCBonus):
    def __init__(self, rolls, operations):
        self.rolls = rolls
        self.operations = operations

    def __repr__(self):
        return f"TargetedBonus(rolls={self.rolls}, operations={self.operations})"

    def apply_bonus(self, rolled_dice: List[int]) -> List[int]:
        new_dice = rolled_dice[:]

        # Apply each operation in sequence
        for operation in self.operations:
            temp_dice = new_dice[:]  # Copy the current state of new_dice for modification
            for i, dice_val in enumerate(new_dice):
                # Check if the dice index + 1 is in the targeted rolls
                if i + 1 in self.rolls:
                    # Apply the operation based on the operation type
                    if operation[0] == "+":
                        temp_dice[i] = dice_val + operation[1]
                    elif operation[0] == "-":
                        temp_dice[i] = dice_val - operation[1]
                    elif operation[0] == "/":
                        try:
                            temp_dice[i] = dice_val / operation[1]
                        except ZeroDivisionError as e:
                            raise ZeroDivisionError("You can't divide rolls by zero!")
                    elif operation[0] == "*":
                        temp_dice[i] = dice_val * operation[1]
                    elif operation[0] == "^":
                        temp_dice[i] = dice_val ** operation[1]
                    elif operation[0] == "%":
                        temp_dice[i] = dice_val % operation[1]
            # Update new_dice with the results of the current operation
            new_dice = temp_dice[:]

        # Return the final modified dice
        return new_dice

    @classmethod
    def parse_string(cls, input_string):
        # Split the input string into two parts: the numbers and the operations
        parts = input_string.split(':')
        numbers_str = parts[0][1:]  # Remove the leading 'i' from the numbers part
        ops_str = parts[1] if len(parts) > 1 else ''  # Get the operations string if it exists

        # Convert the numbers part into a list of integers
        numbers = [int(num) for num in numbers_str.split(',')]

        # Convert the operations string into a list of tuples (OperationEnum, value)
        ops = []
        if ops_str:
            current_op = ''
            for char in ops_str:
                if char in [op.value for op in OperationEnum]:
                    if current_op:
                        op_enum, value = OperationEnum(current_op[0]), float(current_op[1:])
                        ops.append((op_enum, value))
                        current_op = char
                    else:
                        current_op = char
                else:
                    current_op += char

            if current_op:
                op_enum, value = OperationEnum(current_op[0]), float(current_op[1:])
                ops.append((op_enum, value))

        return TargetedBonus(numbers, ops)


    @classmethod
    def parse(cls, input_string) -> List['TargetedBonus']:
        parsed_data_list = []
        # Find the position of the last semicolon
        last_semicolon_idx = input_string.rfind(';')
        # If there's no semicolon, use the entire text; otherwise, use text up to the last semicolon
        text_to_parse = input_string if last_semicolon_idx == -1 else input_string[:last_semicolon_idx]

        segment_starts = [i for i, char in enumerate(text_to_parse) if char == 'i']  # Find all 'i' positions

        for i, start_idx in enumerate(segment_starts):
            # Determine the end of the current segment
            if i < len(segment_starts) - 1:
                next_start = segment_starts[i + 1]
                end_idx = text_to_parse.rfind(';', start_idx, next_start)
                if end_idx == -1:  # If no semicolon is found before the next 'i', use the next 'i' as the end
                    end_idx = next_start
            else:
                # For the last segment, the end is the position of the last semicolon or the end of the text
                end_idx = len(text_to_parse)

            # Parse the segment into a TargetedBonus object
            segment = text_to_parse[start_idx:end_idx]
            parsed_data = cls.parse_string(segment)
            parsed_data_list.append(parsed_data)

        return parsed_data_list
