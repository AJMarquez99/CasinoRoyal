from typing import Optional, Union, List
from .utils import Color
from .chip import Chip

class Pot(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validate_contents()
            
    @property
    def count(self) -> int:
        return sum(count for count in self.values())
    
    @property
    def total(self) -> int:
        return sum(Chip.get(color) * count for color, count in self.items())
    
    @property
    def empty(self) -> bool:
        for count in self.values():
            if count > 0:
                return False
            
        return True

    def to_chips(self) -> List[Chip]:
        return [Chip.from_color(color) for color, count in self.items() for _ in range(count)]

    def append(self, val: Union[Chip, 'Pot', int]) -> 'Pot':
        if isinstance(val, Pot):
            for color, count in val.items():
                self[color] = self.get(color, 0) + count
        elif isinstance(val, Chip):
            self[val.color] = self.get(val.color, 0) + 1
        elif isinstance(val, int):
            self.append(Pot.from_int(val))
        else:
            raise ValueError("Appending is constrained to Pot, Chip, and Int types")
        return self

    def remove(self, val: Union[Chip, 'Pot', int]) -> 'Pot':
        mod_exception = ValueError(f"Value removed must be a factor of {Chip.min_value()}, Value is {val}.")
        negative_exception = ValueError("Pot cannot be negative, value removed is greater than Pot total value.")

        if isinstance(val, Pot):
            if val.total % Chip.min_value() != 0:
                raise mod_exception
            if val.total > self.total:
                raise negative_exception
            return self._remove_pot(val)
        if isinstance(val, Chip):
            if val.value > self.total:
                raise negative_exception
            return self._remove_chip(val)
        elif isinstance(val, int):
            if val % Chip.min_value() != 0:
                raise mod_exception
            if val > self.total:
                raise negative_exception
            return self._remove_int(val)
    
        raise ValueError("Pot remove is constrained to Chip and Int types.")
    
    def _remove_pot(self, val: 'Pot') -> 'Pot':
        removed = Pot()
        try:
            for color, count in val.items():
                if self[color] < count:
                    raise ValueError("Pot cannot have negative values.")
                
                self[color] -= count
                removed[color] = count

                if self[color] == 0:
                    del self[color]

            return removed
        except Exception as e:
            self.append(removed)
            return self._remove_int(val.total)
        
    def _remove_chip(self, val: Chip) -> 'Pot':
        removed = Pot()

        if self[val.color] > 0:
            self[val.color] -= 1
            removed[val.color] = removed.get(val.color, 0) + 1
            if self[val.color] == 0:
                del self[val.color]
            return removed
        return self._remove_int(val.value)
    
    def _remove_int(self, val: int) -> 'Pot':
        removed = Pot()
        remaining = val

        for color, value in sorted(Chip.chip_types().items(), key=Pot.sort_by_value, reverse=True):
            while remaining >= value and self.get(color, 0) >= 1:
                self[color] -= 1
                removed[color] = removed.get(color, 0) + 1
                remaining -= value

                if self[color] == 0:
                    del self[color]

        while remaining > 0:
            for color, value in sorted(Chip.chip_types().items(), key=Pot.sort_by_value):
                if color not in self.keys():
                    continue
                if value > remaining:
                    self.append(self.split(color))
                    break
                while remaining >= value and self.get(color, 0) >= 1:
                    self[color] -= 1
                    removed[color] = removed.get(color, 0) + 1
                    remaining -= value
                if self[color] == 0:
                    del self[color]

        return removed

    def split(self, val: Union[Color, int]) -> 'Pot':
        if isinstance(val, Color):
            chip = Chip.from_color(val)
        elif isinstance(val, int):
            chip = Chip(val)
        else:
            raise ValueError("Splitting chips can only be done by value or color.")
        
        split = Pot()
        self._remove_chip(chip)
        smaller = Chip.next_denomination(chip)

        diff = chip.value % smaller.value
        if diff != 0:
            split.append(Chip(diff))
        for _ in range(chip.value // smaller.value):
            split.append(smaller)
        return split 
    
    def optimize(self):
        self = Pot.from_int(self.total)

    def multiply(self, x: int) -> 'Pot':
        copy = Pot()
        for color in self.keys():
            copy[color] = self[color] * x

        return copy
    
    def divide(self, x: int) -> 'Pot':
        total = self.total // x
        total -= (total % Chip.min_value())
        return Pot.buy_in(total)
    
    @staticmethod
    def from_int(val: int) -> 'Pot':
        if val % Chip.min_value() > 0:
            raise ValueError(f"Value must be a factor of {Chip.min_value()}")
        
        pot = Pot()
        for _, value in sorted(Chip.chip_types().items(), key=Pot.sort_by_value, reverse=True):
            if not val:
                break

            while val >= value:
                pot.append(Chip(value))
                val -= value
        return pot

    @staticmethod
    def buy_in(total: int, ask: Optional['Pot'] = None) -> 'Pot':
        if ask is not None:
            if ask.total == total:
                return ask
            else:
                raise ValueError(f"The requested pot is not equal to the total cash in value: Total: {total}, Ask:{ask.total}")
            
        return Pot.from_int(total)
    
    @staticmethod
    def sort_by_value(item):
        return Chip.chip_types()[item[0]]
    
    @staticmethod
    def sort_by_count(item):
        return item[1]

    def _validate_contents(self):
        for key, val in self.items():
            if not isinstance(key, Color) or not isinstance(val, int):
                raise TypeError("Pot can only contain Color enum keys and integer values")

    def __setitem__(self, key: Color, value: int) -> None:
        if not isinstance(key, Color):
            raise TypeError("Keys must be Color enums")
        if not isinstance(value, int):
            raise TypeError("Values must be integers")
        super().__setitem__(key, value)
        
    def __add__(self, other: 'Pot'):
        if isinstance(other, Pot):
            return self.append(other)
        raise TypeError("Can only add Pot to Pot")
    
    def __str__(self):
        return f"(Value: ${self.total}.00, {{{', '. join([f'{color.name.capitalize()}: {count}' for color, count in sorted(self.items(), key=self.sort_by_value, reverse=True)])}}})"
    
    def __repr__(self):
        return f"Pot(value=${self.total}.00, chips={self.count}, {{{', '. join([f'{color.name.capitalize()}: {count}' for color, count in sorted(self.items(), key=self.sort_by_value, reverse=True)])}}})"