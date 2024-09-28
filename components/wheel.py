from .utils import Color
from typing import List
import random

class Spoke:
    def __init__(self, label: str):
        self.label = label
        self.number = int(label)
        self.color = self._getColor(self.number)

    @staticmethod
    def _getColor(num: int) -> Color:
        red   = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        black = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        green = [0]

        if num in red:
            return Color.RED
        
        if num in black:
            return Color.BLACK
        
        if num in green:
            return Color.GREEN
        
    def __repr__(self):
        return f"Roulette Number(label={self.label}, color={self.color.value})"

class Wheel:
    def __init__(self):
          self.wheel = tuple([Spoke(label) for label in self._wheelOrder()])
    
    def spin(self) -> Spoke:
         return self.wheel[random.choice(range(len(self.wheel)))]

    @staticmethod
    def _wheelOrder() -> List[str]:
         return [
              "00",
              "1",
              "13",
              "36",
              "24",
              "3",
              "15",
              "34",
              "22",
              "5",
              "17",
              "32",
              "20",
              "7",
              "11",
              "30",
              "26",
              "9",
              "28",
              "0",
              "2",
              "14",
              "35",
              "23",
              "4",
              "16",
              "33",
              "21",
              "6",
              "18",
              "31",
              "19",
              "8",
              "12",
              "29",
              "25",
              "10",
              "27"
         ]