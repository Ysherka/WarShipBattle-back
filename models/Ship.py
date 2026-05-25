from models.ShipOrientation import ShipOrientation


class Ship:
    def __init__(self, row: int, col: int, length: int, orientation: ShipOrientation):
        self.row: int = row
        self.col: int = col
        self.length: int = length
        self.orientation: ShipOrientation = orientation
        self.decks_coordinates: list[tuple[int, int]] = []
        self.__fill_decks_coordinates()
        #TODO возможно стоит добавить список палуб и создать класс Палуба с ссылкой на корабль родитель
        #TODO возможно нужно добавить поле состояния корабля (цел, ранен, убит) и поле состояния палубы (цела, ранена)

    def __fill_decks_coordinates(self):
        for i in range(self.length):
            match self.orientation:
                case ShipOrientation.RIGHT:
                    self.decks_coordinates.append((self.row, self.col + i))
                case ShipOrientation.DOWN:
                    self.decks_coordinates.append((self.row + i, self.col))

    def __repr__(self):
        return f"Ship(row={self.row}, col={self.col}, length={self.length}, orientation={self.orientation.name})"
