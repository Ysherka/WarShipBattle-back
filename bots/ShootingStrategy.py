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
            x, y = hits[0]
            candidates = []
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < enemy_field.FIELD_SIZE and
                    0 <= ny < enemy_field.FIELD_SIZE and
                    enemy_field.get_shot_available(nx, ny)):
                    candidates.append((nx, ny))
            if candidates:
                return random.choice(candidates)

        else:
            # Несколько попаданий — определяем ориентацию и стреляем по линии
            xs = [h[0] for h in hits]
            ys = [h[1] for h in hits]

            if len(set(xs)) == 1:  # Горизонтальный корабль
                x = xs[0]
                min_y, max_y = min(ys), max(ys)
                candidates = []
                if enemy_field.get_shot_available(x, min_y - 1):
                    candidates.append((x, min_y - 1))
                if enemy_field.get_shot_available(x, max_y + 1):
                    candidates.append((x, max_y + 1))
                if candidates:
                    return random.choice(candidates)

            elif len(set(ys)) == 1:  # Вертикальный корабль
                y = ys[0]
                min_x, max_x = min(xs), max(xs)
                candidates = []
                if enemy_field.get_shot_available(min_x - 1, y):
                    candidates.append((min_x - 1, y))
                if enemy_field.get_shot_available(max_x + 1, y):
                    candidates.append((max_x + 1, y))
                if candidates:
                    return random.choice(candidates)

        # Если не удалось добить — случайный выстрел
        return None

    @staticmethod
    def _get_available_cells(enemy_field: EnemyField) -> List[Tuple[int, int]]:
        """Возвращает все доступные для выстрела клетки"""
        available = []
        for x in range(enemy_field.FIELD_SIZE):
            for y in range(enemy_field.FIELD_SIZE):
                if enemy_field.get_shot_available(x, y):
                    available.append((x, y))
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
        for x in range(size):
            for y in range(size):
                if (x + y) % 2 == 0 and enemy_field.get_shot_available(x, y):
                    phase1.append((x, y, x + y))
        
        # Сортировка: сначала меньшая сумма, при равной — меньший x
        phase1.sort(key=lambda c: (c[2], c[0]))
        
        for x, y, _ in phase1:
            return (x, y)

        # Фаза 2: Клетки (x + y) % 2 == 1 (белые поля)
        phase2 = []
        for x in range(size):
            for y in range(size):
                if (x + y) % 2 == 1 and enemy_field.get_shot_available(x, y):
                    phase2.append((x, y, x + y))
        
        phase2.sort(key=lambda c: (c[2], c[0]))
        
        for x, y, _ in phase2:
            return (x, y)

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
        
        for x in range(offset, size, step):
            for y in range(offset, size, step):
                if enemy_field.get_shot_available(x, y):
                    grid_cells.append((x, y))

        random.shuffle(grid_cells)

        if grid_cells:
            return grid_cells[0]

        # Переход к следующей фазе
        if phase > 1:
            return ShootingStrategy.make_move_hunter(enemy_field, history, hits, phase - 1)

        return ShootingStrategy.make_move_random(enemy_field)

    @staticmethod
    def update_hits(hits: List[Tuple[int, int]], x: int, y: int,
                    is_hit: bool, is_destroyed: bool) -> List[Tuple[int, int]]:
        """Обновляет список попаданий"""
        if is_hit and not is_destroyed:
            hits.append((x, y))
        elif is_destroyed:
            return []  # Корабль уничтожен — очищаем
        return hits