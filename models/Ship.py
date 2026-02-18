from models.ShipOrientation import ShipOrientation


class Ship:
    def __init__(self, x: int, y: int, length: int, orientation: ShipOrientation):
        self.x: int = x
        self.y: int = y
        self.length: int = length
        self.orientation: ShipOrientation = orientation
        self.decks_coordinates: list[tuple[int, int]] = []
        self.__fill_decks_coordinates()
        #TODO возможно стоит добавить список палуб и создать класс Палуба с ссылкой на корабль родитель
        #TODO возможно нужно добавить поле состояния корабля (цел, ранен, убит) и поле состояния палубы (цела, ранена)

    def __fill_decks_coordinates(self):
        for i in range(self.length):
            match self.orientation:
                case ShipOrientation.UP:
                    self.decks_coordinates.append((self.x, self.y + i))
                case ShipOrientation.RIGHT:
                    self.decks_coordinates.append((self.x + i, self.y))
                case ShipOrientation.DOWN:
                    self.decks_coordinates.append((self.x, self.y - i))
                case ShipOrientation.LEFT:
                    self.decks_coordinates.append((self.x - i, self.y))