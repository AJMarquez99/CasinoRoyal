from .utils import Color
from typing import List, Dict, Union, Optional
from functools import total_ordering

@total_ordering
class Chip:
    __slots__ = ('_value', '_color')

    _instances: Dict[int, 'Chip'] = {}
    _color_value_map = {
        Color.WHITE: 5,
        Color.BLUE: 10,
        Color.RED: 20,
        Color.GREEN: 50,
        Color.BLACK: 100
    }
    _value_color_map = {value: color for color, value in _color_value_map.items()}

    def __new__(cls, value: int):
        if value not in cls._instances:
            if value not in cls._value_color_map:
                raise ValueError(f"Invalid chip value: {value}. Valid values are {list(cls._value_color_map.keys())}")
            instance = super().__new__(cls)
            instance._value = value
            instance._color = cls._value_color_map[value]
            cls._instances[value] = instance
        return cls._instances[value]
    
    @property
    def value(self) -> int:
        return self._value
    
    @property
    def color(self) -> Color:
        return self._color
    
    @classmethod
    def from_color(cls, color: Color) -> 'Chip':
        return cls(cls._color_value_map[color])
    
    @classmethod
    def get_chip_list(cls) -> Dict[Color, int]:
        return cls._color_value_map
    
    @staticmethod
    def optimize(chips: List['Chip']) -> List['Chip']:
        total_value = sum(chip.value for chip in chips)
        optimized = []
        for _, value in sorted(Chip._color_value_map, key=lambda item: item.value, reverse=True):
            while total_value >= value:
                optimized.append(Chip(value))
                total_value -= value
        return optimized
    
    @staticmethod
    def get_total(chips: List['Chip']) -> int:
        return sum(chip.value for chip in chips)
            
    def __repr__(self):
        return f"Chip(value={self._value}, color={self._color})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Chip):
            return NotImplemented
        return self._value == other._value
    
    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Chip):
            return NotImplemented
        return self._value < other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
    
class Pot(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validate_contents()
            
    @property
    def count(self):
        return sum(count for count in self.values())
    
    @property
    def total(self):
        return sum(Chip.from_color(color).value * count for color, count in self.items())

    def to_chips(self) -> List[Chip]:
        return [Chip.from_color(color) for color, count in self.items() for _ in range(count)]

    def append(self, val: Union[Chip, 'Pot']) -> 'Pot':
        if isinstance(val, Pot):
            for x, y in val.items():
                self[x] = self.get(x, 0) + y
        else:
            self[val.color] = self.get(val.color, 0) + 1
        return self

    def remove(self, val: Union[Chip, int]) -> 'Pot':
        removed = Pot()
        if isinstance(val, Chip):
            if val.color in self.keys() and self[val.color] > 0:
                self[val.color] -= 1
                removed[val.color] = removed.get(val.color, 0) + 1
                if self[val.color] == 0:
                    del self[val.color]
                return removed
            else:
                raise ValueError("Not enough chips in pot to remove")
        elif isinstance(val, int):
            if val % min(Chip.get_chip_list().values()) > 0:
                raise ValueError("Invalid Int")
            
            for color, value in reversed(Chip.get_chip_list().items()):
                if not color in self.keys():
                    continue
                while val >= value:
                    try:
                        self.remove(Chip(value))
                        val -= value
                        removed[color] = removed.get(color, 0) + 1
                    except:
                        break
            
            return removed
        else:
            raise TypeError("Invalid removal item")
    
    def optimize(self):
        chips = self.to_chips()
        optimized_chips = Chip.optimize(chips)
        self.clear()
        self.add_chips(optimized_chips)

    def multiply(self, x: int) -> 'Pot':
        for color, num in self.items():
            self[color] *= x

        return self

    @staticmethod
    def buy_in(total: int, ask: Optional['Pot'] = None) -> 'Pot':
        if ask is not None:
            if ask.total == total:
                return ask
            else:
                raise ValueError(f"The requested pot is not equal to the total cash in value: Total: {total}, Ask:{ask.total}")
            
        pot = Pot()
        for _, val in reversed(Chip.get_chip_list().items()):
            while total >= val:
                pot.append(Chip(val))
                total -= val
        if not total == 0:
            raise ValueError("Total must be divisble by 5")
        return pot

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
        new_pot = Pot(self)
        if isinstance(other, Pot):
            for color, count in other.items():
                new_pot[color] = new_pot.get(color, 0) + count
        else:
            raise TypeError("Can only add Pot to Pot")
        
        return new_pot
    
    def __repr__(self):
        return f"Pot(chips={self.count}, value={self.total}, {{{', '. join([f'{color.name.lower()}: {count}' for color, count in sorted(self.items(), key=lambda x: Chip.from_color(x[0]).value, reverse=True)])}}})"