from models.Field import BaseField, OwnField, EnemyField
from models.FieldState import FieldState
from models.Ship import Ship
from models.ShipOrientation import ShipOrientation
from models.User import User
from bots.Bot import Bot


class Game:
    def __init__(self, user: User | None = None, enemy: User | None = None, bot: Bot | None = None):
        self.user: User | None = user
        self.enemy: User | None = enemy
        self.bot: Bot | None = bot  # ◆ Композиция (Game создаёт Bot)
        self.turn: bool = True

    @staticmethod
    def check_all_ships_destroyed(field: OwnField) -> bool:
        """Проверка, все ли корабли уничтожены"""
        for ship in field.ships:
            for x, y in ship.decks_coordinates:
                if field.get_cell_display(x, y) != FieldState.DESTROYED:
                    return False
        return True

    """
    здесь инты обозначают размер корабля
    0 - пусто 
    1 - однопалубный корабль
    2 - двухпалубный
    3 - трехпалубный
    4 - четырехпалубный
    """
    @staticmethod
    def field_to_ship_list(grid: list[list[int]]) -> list[Ship]:
        """
            Преобразует двумерный массив в список объектов Ship.

            0 — пустая клетка, 1-4 — корабли соответствующей длины.
            Корабли могут быть расположены горизонтально (RIGHT) или вертикально (DOWN).
            """
        ships = []
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        visited = [[False] * cols for _ in range(rows)]

        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 0 or visited[r][c]:
                    continue

                length = grid[r][c]

                # Проверяем горизонтальное расположение (RIGHT)
                h_count = 1
                cc = c + 1
                while cc < cols and grid[r][cc] == length and not visited[r][cc]:
                    h_count += 1
                    cc += 1

                # Проверяем вертикальное расположение (DOWN)
                v_count = 1
                rr = r + 1
                while rr < rows and grid[rr][c] == length and not visited[rr][c]:
                    v_count += 1
                    rr += 1

                # Определяем ориентацию
                if h_count > 1:
                    orientation = ShipOrientation.RIGHT
                    for i in range(h_count):
                        visited[r][c + i] = True
                    ships.append(Ship(r, c, length, orientation))

                elif v_count > 1:
                    orientation = ShipOrientation.DOWN
                    for i in range(v_count):
                        visited[r + i][c] = True
                    ships.append(Ship(r, c, length, orientation))

                else:
                    # Однопалубный корабль
                    visited[r][c] = True
                    ships.append(Ship(r, c, length, ShipOrientation.RIGHT))

        return ships

    def add_ships(self, ships: list[Ship]):
        for ship in ships:
            self.user.own_field.add_ship(ship)

    def add_ships_int(self, field: list[list[int]]):
        ships: list[Ship] = self.field_to_ship_list(field)
        print("ships после перевода из системы длин\n", ships)
        for ship in ships:
            self.user.own_field.add_ship(ship)
        print(self.user.own_field.cells)

    def shoot(self, row: int, col: int) -> bool:
        is_hit, _ = self.enemy.own_field.shoot(row, col, self.user.enemy_field)
        self.user.enemy_field.known_cells[row][col] = True
        return is_hit

    def shoot_with_bot(self, row: int, col: int) -> bool:
        is_hit, _ = self.bot.own_field.shoot(row, col, self.user.enemy_field)
        self.user.enemy_field.known_cells[row][col] = True
        return is_hit
