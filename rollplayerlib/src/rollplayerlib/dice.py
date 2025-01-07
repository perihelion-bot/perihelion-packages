import random
import re
from typing import List, Optional

from .enums import OperationEnum, FormatType, SolveMode
from .exceptions import RollException, SplitFailException
from .formatting import Format
from .bonuses import Bonus, TargetedBonus
from .config import MAX_DICE

class BasicDice:
    def __init__(self, count, start, end):
        self.count = count
        self.start = start
        self.end = end

    def __repr__(self):
        return f"BasicDice(count={self.count}, range={self.start}:{self.end})"

    @classmethod
    def parse(cls, input_string):
        # Check if the string starts directly with 'd', implying a single die
        if input_string.startswith('d'):
            count = 1
            range_part = input_string[1:]  # Exclude the 'd' to get the range part
        else:
            try:
                count_part, range_part = input_string.split('d')
            except ValueError as e:
                raise SplitFailException("Cannot split dice string (you have too many fields for dice notation!)")
            count = min(int(count_part), MAX_DICE+1) if count_part.isdigit() else 1

        if count == MAX_DICE+1:
            raise RollException(f"Dice count limit exceeded [max {MAX_DICE}]")

        # Check if there's a colon in the range part
        if not range_part:
            start, end = 1, 100
        elif ':' in range_part:
            start, end = range_part.split(':')
            try:
                start, end = int(start), int(end)  # Convert start and end to integers
            except ValueError as e:
                raise ValueError(f"The start or end of your dice string isn't a integer! (start: '{start}', end: '{end}')")
        else:
            try:
                start, end = 1, int(range_part)  # If no colon, range is from 1 to the specified number
            except ValueError as e:
                raise ValueError(f"The amount of sides to roll isn't an integer! ('{range_part}')")

        # Flip the start and end values if end is less than start
        if end < start:
            start, end = end, start  # Swap the values

        return BasicDice(count, start, end)


class RollResult:
    def __init__(self, roll_string: str, rolls: List[int], original_rolls: List[int]):
        self.roll_string = roll_string
        self.rolls = rolls
        self.original_rolls = original_rolls
        self.threshold = None

    def _format_numbers(self, numbers: List[int]):
        # Convert numbers close to an integer to int, then to string
        rounded_nums = [int(x) if abs(x - round(x)) < 0.000000001 else x for x in numbers]
        if self.threshold is not None:
            passing_nums = self.threshold.passing(rounded_nums)
            return [f'**{x}**' if pass_result else str(x) for x, pass_result in zip(rounded_nums, passing_nums)]
        else:
            return [str(x) for x in rounded_nums]

    def _format_rolls(self, rolls: List[int]):
        # Convert numbers close to an integer to int, then to string
        formatted_nums = self._format_numbers(rolls)
        # Join the stringified numbers with commas
        return ', '.join(formatted_nums)

    def _format_and_split_rolls(self, rolls: List[int], n: int):
        # Convert numbers close to an integer to int, then to string
        formatted_nums = self._format_numbers(rolls)
        # Split the list into chunks of size n, join each chunk with commas, then join chunks with newlines
        return '\n'.join(', '.join(formatted_nums[i:i + n]) for i in range(0, len(formatted_nums), n))

    def _format_and_split_rolls__repr__(self, rolls: List[int], n: int):
        # Convert numbers close to an integer to int, then to string
        formatted_nums = self._format_numbers(rolls)
        # Split the list into chunks of size n, join each chunk with commas, then join chunks with newlines
        return '\n┃ '.join(', '.join(formatted_nums[i:i + n]) for i in range(0, len(formatted_nums), n))

    def _format_sum(self, rolls: List[int]):
        # Convert close to an integer to int, then to string
        formatted_sum = str(int(sum(rolls))) if abs(sum(rolls) - round(sum(rolls))) < 0.000000001 else str(sum(rolls))
        return formatted_sum

    def __repr__(self):
        return f"┏━━━━ {self.roll_string} ━━━━ \n┃ {self._format_and_split_rolls__repr__(self.rolls, 20)}\n┃ sum: {self._format_sum(self.rolls)}"

    def format(self, formatting: Format) -> List[tuple[str, str]]:
        # roll_icon = "<:roll_icon:1223801360273903656>"
        roll_icon = ""

        results = []
        format_type = formatting.format_type
        format_args = formatting.format_args
        self.threshold = formatting.threshold

        if format_type == FormatType.FORMAT_DEFAULT:
            results.append((
                f"{roll_icon} You rolled a {self.roll_string} and got...",
                self._format_rolls(self.rolls) + (
                    f" (sum: {self._format_sum(self.rolls)})" if len(self.rolls) > 1 else "")
            ))
            if self.rolls != self.original_rolls:
                results.append((
                    f"{roll_icon} You rolled a {self.roll_string} and without modifiers got...",
                    self._format_rolls(self.original_rolls) + (
                        f" (sum: {self._format_sum(self.original_rolls)})" if len(self.original_rolls) > 1 else "")
                ))
        elif format_type == FormatType.FORMAT_SUM:
            results.append((
                f"{roll_icon} You rolled a {self.roll_string} and got...",
                self._format_sum(self.rolls)
            ))
            if self.rolls != self.original_rolls:
                results.append((
                    f"{roll_icon} You rolled a {self.roll_string} and without modifiers got...",
                    self._format_sum(self.original_rolls)
                ))
        elif format_type == FormatType.FORMAT_LIST:
            results.append((
                f"{roll_icon} You rolled a {self.roll_string} and got...",
                self._format_rolls(self.rolls)
            ))
            if self.rolls != self.original_rolls:
                results.append((
                    f"{roll_icon} You rolled a {self.roll_string} and without modifiers got...",
                    self._format_rolls(self.original_rolls)
                ))
        elif format_type == FormatType.FORMAT_LIST_SPLIT:
            if format_args is None:
                raise ValueError("format_args must be an integer for FORMAT_LIST_SPLIT")
            results.append((
                f"{roll_icon} You rolled a {self.roll_string} and got...",
                self._format_and_split_rolls(self.rolls, format_args)
            ))
            if self.rolls != self.original_rolls:
                results.append((
                    f"{roll_icon} You rolled a {self.roll_string} and without modifiers got...",
                    self._format_and_split_rolls(self.original_rolls, format_args)
                ))
        else:
            # base case
            results.append((
                f"{roll_icon} You rolled a {self.roll_string} and got...",
                self._format_rolls(self.rolls)
            ))
            if self.rolls != self.original_rolls:
                results.append((
                    f"{roll_icon} You rolled a {self.roll_string} and without modifiers got...",
                    self._format_rolls(self.original_rolls)
                ))

        return results

class UnifiedDice:

    def __init__(self):
        self.original_string: str = ""
        self.targeted_bonuses: List[TargetedBonus] = []
        self.bonuses: List[Bonus] = []
        self.basic_dice: Optional[BasicDice] = None

    def __repr__(self):
        return f"UnifiedDice(TargetedBonuses={self.targeted_bonuses}, Bonuses={self.bonuses}, BasicDice={self.basic_dice})"

    def solve(self, solve_mode: SolveMode) -> RollResult:
        if self.basic_dice is None:
            raise RollException("No dice to roll")

        dice: List[int] = []
        if solve_mode == SolveMode.RANDOM:
            dice = [random.randint(self.basic_dice.start, self.basic_dice.end) for _ in range(self.basic_dice.count)]
        elif solve_mode == SolveMode.MAX:
            dice = [self.basic_dice.end for _ in range(self.basic_dice.count)]
        elif solve_mode == SolveMode.MIN:
            dice = [self.basic_dice.start for _ in range(self.basic_dice.count)]

        orig_dice = dice.copy()
        for bonusset in (self.bonuses, self.targeted_bonuses):
            for bonus in bonusset:
                dice = bonus.apply_bonus(dice)
        return RollResult(self.original_string, dice, orig_dice)

    @classmethod
    def new(cls, input_string):
        dice = UnifiedDice()
        dice.original_string = input_string
        split_regex = r'(' + '|'.join(re.escape(op.value) for op in OperationEnum) + r'|i)'
        operations_regex = r'(' + '|'.join(re.escape(op.value) for op in OperationEnum) + r')'
        # can the int be coerced directly?
        try:
            dice.basic_dice = BasicDice(1, 1, int(input_string))
            return dice
        except Exception as e:
            pass

        # Initial split to separate BasicDice, Bonus, and TargetedBonus parts
        dice_part, *bonus_parts = re.split(split_regex, input_string, 1)
        bonus_part = ''.join(bonus_parts) if bonus_parts else ''

        # Further split to isolate TargetedBonus if present
        if 'i' in bonus_part:
            bonus_part, targeted_bonus_part = bonus_part.split('i', 1)
            targeted_bonus_part = 'i' + targeted_bonus_part  # Prepend 'i' back for correct parsing
        else:
            targeted_bonus_part = ''

        # Parse BasicDice if present
        if 'd' in dice_part:
            dice.basic_dice = BasicDice.parse(dice_part)

        # Parse Bonus if present
        if bonus_part:
            operation = OperationEnum.ADD.value
            for part in re.split(operations_regex, bonus_part):
                if part in [op.value for op in OperationEnum]:
                    operation = part
                elif part:  # Check if part is not empty
                    dice.bonuses.extend(Bonus.parse(operation + part))

        # Parse TargetedBonus if present
        if targeted_bonus_part:
            dice.targeted_bonuses.extend(TargetedBonus.parse(targeted_bonus_part))

        if dice.basic_dice is None:
            raise RollException("Your input was not parsable.")
        return dice
