from .utils import Color
from typing import List, Dict, Union
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
    _min = min(_value_color_map.keys())

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
    def min_value(cls) -> int:
        return min(cls._color_value_map.values())
    
    @classmethod
    def get(cls, val: Union[int, Color]) -> Union[int, Color]:
        if not isinstance(val, int) and not isinstance(val, Color):
            raise ValueError("Can only get Chip values by Color or Int.")

        if isinstance(val, int):
            if val in cls._value_color_map.keys():
                return cls._value_color_map[val]
            else:
                raise ValueError(f"There is no chip color that correlates to int ({val}).")
        
        if isinstance(val, Color):
            if val in cls._color_value_map.keys():
                return cls._color_value_map[val]
            else:
                raise ValueError(f"There is no chip color that correlates to color ({val.value}).")
    
    @classmethod
    def from_color(cls, color: Color) -> 'Chip':
        return cls(cls._color_value_map[color])
    
    @classmethod
    def chip_types(cls) -> Dict[Color, int]:
        return cls._color_value_map
    
    @classmethod
    def next_denomination(cls, val: 'Chip', ascending: bool = False) -> 'Chip':
        val_map = list(sorted(cls._color_value_map.values(), reverse=ascending))
        index = val_map.index(val.value)

        if not index:
            denomination = "bigger" if ascending else "smaller"
            raise IndexError(f"There is no {denomination} denomination.")
        
        return Chip(val_map[index - 1])
    
    @staticmethod
    def get_total(chips: List['Chip']) -> int:
        return sum(chip.value for chip in chips)
    
    @staticmethod
    def to_chip_int(val: Union[int, float]) -> int:
        return int(val - (val % Chip.min_value()))
            
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