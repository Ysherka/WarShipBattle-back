import random
from typing import List, Tuple, Optional
from models.Field import EnemyField
from models.FieldState import FieldState


class ShootingStrategy:
    """Утилитарный класс со стратегиями стрельбы бота"""

    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    @staticmethod
    def _finish_ship(enemy_field: EnemyField, hits: List[Tuple[int, int]]) -> Tuple[int, int]:
        """
        Добивание раненого корабля.
        Вызывается из любой стратегии при наличии попаданий.
        """
        if not hits:
            return None

        if len(hits) == 1:
            # Одно попадание — ищем направление (крест)
            row, col = hits[0]
            candidates = []
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = row + dr, y + dc
                if (0 <= nr < enemy_field.FIELD_SIZE and
                        0 <= nc < enemy_field.FIELD_SIZE and
                        enemy_field.get_shot_available(nr, nc)):
                    candidates.append((nr, nc))
            if candidates:
                return random.choice(candidates)

        else:
            # Несколько попаданий — определяем ориентацию и стреляем по линии
            rows = [h[0] for h in hits]
            colss = [h[1] for h in hits]

            if len(set(rows)) == 1:  # Горизонтальный корабль
                row = rows[0]
                min_col, max_col = min(cols), max(cols)
                candidates = []
                if enemy_field.get_shot_available(row, min_col - 1):
                    candidates.append((row, min_col - 1))
                if enemy_field.get_shot_available(row, max_col + 1):
                    candidates.append((row, max_col + 1))
                if candidates:
                    return random.choice(candidates)

            elif len(set(cols)) == 1:  # Вертикальный корабль
                col = cols[0]
                min_row, max_row = min(rows), max(rows)
                candidates = []
                if enemy_field.get_shot_available(min_row - 1, col):
                    candidates.append((min_row - 1, col))
                if enemy_field.get_shot_available(max_row + 1, col):
                    candidates.append((max_row + 1, col))
                if candidates:
                    return random.choice(candidates)

        # Если не удалось добить — случайный выстрел
        return None

    @staticmethod
    def _get_available_cells(enemy_field: EnemyField) -> List[Tuple[int, int]]:
        """Возвращает все доступные для выстрела клетки"""
        available = []
        for row in range(enemy_field.FIELD_SIZE):
            for col in range(enemy_field.FIELD_SIZE):
                if enemy_field.get_shot_available(row, col):
                    available.append((row, col))
        return available

    # ==================== СТРАТЕГИИ ====================

    @staticmethod
    def make_move_random(enemy_field: EnemyField, hits: List[Tuple[int, int]] = None) -> Tuple[int, int]:
        """
        Случайная стратегия С ДОБИВАНИЕМ:
        - Если есть раненый корабль — добиваем
        - Иначе — случайный выстрел
        """
        hits = hits or []

        # Фаза добивания
        if hits:
            finish = ShootingStrategy._finish_ship(enemy_field, hits)
            if finish:
                return finish

        # Фаза случайного поиска
        available = ShootingStrategy._get_available_cells(enemy_field)
        if not available:
            raise ValueError("No available shots")
        return random.choice(available)

    @staticmethod
    def make_move_diagonal(enemy_field: EnemyField, hits: List[Tuple[int, int]] = None) -> Tuple[int, int]:
        """
        Диагональная стратегия С ДОБИВАНИЕМ:
        - Если есть раненый корабль — добиваем
        - Иначе — обстрел по шахматной доске (x + y) % 2 == 0
        """
        size = enemy_field.FIELD_SIZE
        hits = hits or []

        # Фаза добивания: приоритет №1
        if hits:
            finish = ShootingStrategy._finish_ship(enemy_field, hits)
            if finish:
                return finish

        # Фаза 1: Клетки (x + y) % 2 == 0 (чёрные поля шахматной доски)
        phase1 = []
        for row in range(size):
            for col in range(size):
                if (row + col) % 2 == 0 and enemy_field.get_shot_available(row, col):
                    phase1.append((row, col, row + col))
        
        # Сортировка: сначала меньшая сумма, при равной — меньший x
        phase1.sort(key=lambda c: (c[2], c[0]))

        for row, col, _ in phase1:
            return (row, col)

        # Фаза 2: Клетки (x + y) % 2 == 1 (белые поля)
        phase2 = []
        for row in range(size):
            for col in range(size):
                if (row + col) % 2 == 1 and enemy_field.get_shot_available(row, col):
                    phase2.append((row, col, row + col))
        
        phase2.sort(key=lambda c: (c[2], c[0]))

        for row, col, _ in phase2:
            return (row, col)

        # Фаза 3: Всё занято — случайно
        return ShootingStrategy.make_move_random(enemy_field)

    @staticmethod
    def make_move_hunter(enemy_field: EnemyField, history: List[Tuple[int, int]] = None,
                          hits: List[Tuple[int, int]] = None, phase: int = 4) -> Tuple[int, int]:
        """
        Стратегия «Охота на большие корабли» С ДОБИВАНИЕМ:
        - Если есть раненый корабль — добиваем
        - Иначе — сетка с шагом (4 → 3 → 2 → 1)
        """
        size = enemy_field.FIELD_SIZE
        hits = hits or []

        # Фаза добивания: приоритет №1
        if hits:
            finish = ShootingStrategy._finish_ship(enemy_field, hits)
            if finish:
                return finish

        # Генерируем сетку с заданным шагом
        step = phase
        grid_cells = []
        offset = (phase * 7) % step

        for row in range(offset, size, step):
            for col in range(offset, size, step):
                if enemy_field.get_shot_available(row, col):
                    grid_cells.append((row, col))

        random.shuffle(grid_cells)

        if grid_cells:
            return grid_cells[0]

        # Переход к следующей фазе
        if phase > 1:
            return ShootingStrategy.make_move_hunter(enemy_field, history, hits, phase - 1)

        return ShootingStrategy.make_move_random(enemy_field)

    @staticmethod
    def update_hits(hits: List[Tuple[int, int]], row: int, col: int,
                    is_hit: bool, is_destroyed: bool) -> List[Tuple[int, int]]:
        """Обновляет список попаданий"""
        if is_hit and not is_destroyed:
            hits.append((row, col))
        elif is_destroyed:
            return []  # Корабль уничтожен — очищаем
        return hits