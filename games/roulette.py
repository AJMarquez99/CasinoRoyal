from components import Table, Seat, Wheel

class RouletteTable(Table):
    def __init__(self, min_bet: int, max_bet: int | None = None, limit: int = 6):
        super().__init__(min_bet, max_bet, limit)
        self._wheel = Wheel()

    @property
    def wheel(self) -> Wheel:
        return self._wheel