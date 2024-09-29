from .utils import Color
from typing import List, Dict
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