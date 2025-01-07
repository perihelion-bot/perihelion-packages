
# rollplayerlib
This library provides a flexible and extensible way to handle complex dice roll expressions and formats. It supports a wide range of features, including basic dice rolls, bonuses, targeted bonuses, and various formatting options.
## Installation
You can install the library through pip: `pip install rollplayerlib`.
## Usage
### Basic Dice Roll

To roll a basic set of dice, you can use the UnifiedDice.new() method:

```python
from rollplayerlib import UnifiedDice, SolveMode

# Roll 3 six-sided dice
dice = UnifiedDice.new("3d6")
result = dice.solve(SolveMode.RANDOM)
print(result)
```
This will output something like:
```
┏━━━━ 3d6 ━━━━ 
┃ 4, 2, 6
┃ sum: 12
```
### Dice Rolls with Bonuses

You can apply bonuses to your dice rolls by using the +, -, *, and / operators:

```python
# Roll 2d6 and add 3
dice = UnifiedDice.new("2d6+3")
result = dice.solve(SolveMode.RANDOM)
print(result)
```

This will output something like:
```
┏━━━━ 2d6+3 ━━━━ 
┃ 8, 7
┃ sum: 15
```
Note that the bonus applies to each roll individually.
### Targeted Bonuses

You can apply targeted bonuses to specific dice in your roll using the i syntax:

```python
# Roll 45d100, multiply the 1st die by 20
dice = UnifiedDice.new("45d100i1:*20")
result = dice.solve(SolveMode.RANDOM)
print(result)
```
This will output something like:
```
┏━━━━ 45d100i1:*20 ━━━━ 
┃ 1080, 17, 63, 39, 47, 58, 98, 93, 16, 54, 90, 89, 99, 63, 68, 30, 26, 66, 36, 96
┃ 8, 85, 47, 3, 79, 5, 46, 56, 41, 41, 67, 45, 83, 44, 14, 19, 31, 96, 82, 98
┃ 26, 36, 39, 51, 7
┃ sum: 3377
```
### Formatting Options

You can control the formatting of the dice roll results using the Format class:

```python
from rollplayerlib import UnifiedDice, SolveMode, Format, FormatType, ThresholdType

# Roll 4d6, keep the highest 3 rolls
dice = UnifiedDice.new("4d6")
formatting = Format(FormatType.FORMAT_LIST, threshold=Threshold(3, ThresholdType.GREATER))
result = dice.solve(SolveMode.RANDOM)
print(result.format(formatting))
```

This will output something like:
```
┏━━━━ 4d6 ━━━━ 
┃ **5**, **4**, **3**, 2
┃ sum: 14
```
## API Reference
### `UnifiedDice`

    new(input_string: str) -> UnifiedDice: Constructs a UnifiedDice object from a dice roll expression.
    solve(solve_mode: SolveMode) -> RollResult: Solves the dice roll expression and returns the RollResult.

### `RollResult`

    format(formatting: Format) -> List[tuple[str, str]]: Formats the dice roll result according to the provided Format object.

### `Format`

    __init__(format_type: FormatType, format_args=None, threshold: Threshold=None): Constructs a Format object with the specified parameters.
    parse(expression: str) -> tuple[str, Format]: Parses a dice roll expression and returns the remaining text and the corresponding Format object.

### `Threshold`

    __init__(limit: int, threshold_type: ThresholdType): Constructs a Threshold object with the specified limit and type.
    passing(numbers: list[int]) -> list[bool]: Checks which numbers in the provided list pass the threshold condition.

### `SolveMode`

    RANDOM, MAX, MIN: Enum values representing different solve modes.

