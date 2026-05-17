import sys
import os

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bots.Bot import Bot
from models.FieldState import FieldState
from models.Field import OwnField


def test_bot_battle():
    # Создаем двух ботов
    bot1 = Bot(name="Bot1", difficulty=1, field_size=10)
    bot2 = Bot(name="Bot2", difficulty=1, field_size=10)
    
    # Расставляем корабли случайным способом
    bot1.place_ships(method="perelman")
    bot2.place_ships(method="random")
    
    print(f"\nПоле {bot1.name}:")
    print_field(bot1.own_field)
    
    print(f"\nПоле {bot2.name}:")
    print_field(bot2.own_field)
    
    # Игровой цикл
    current_bot = bot1
    opponent_bot = bot2
    move_count = 0
    max_moves = 500  # Защита от бесконечного цикла
    
    print("=" * 50)
    print("НАЧАЛО ИГРЫ")
    print("=" * 50)
    
    while move_count < max_moves:
        move_count += 1
        print(f"\n--- Ход {move_count}: {current_bot.name} ---")
        
        # Делаем выстрел
        x, y = current_bot.make_move()
        print(f"{current_bot.name} стреляет в ({x}, {y})")
        
        # Проверяем попадание по полю противника
        is_hit, destroyed_ship = opponent_bot.own_field.shoot(x, y)
        
        # Обновляем поле зрения текущего бота
        current_bot.enemy_field.shoot_result(x, y, is_hit, destroyed_ship is not None)
        
        if destroyed_ship:
            print(f"💥 {current_bot.name} уничтожил корабль длиной {destroyed_ship.length}!")
        elif is_hit:
            print(f"🔥 {current_bot.name} попал!")
        else:
            print(f"🌊 {current_bot.name} промахнулся")
        
        # Проверяем конец игры
        if check_all_ships_destroyed(opponent_bot.own_field):
            print(f"\n🏆 {current_bot.name} ПОБЕДИЛ за {move_count} ходов!")
            break
        
        # Меняем ход при промахе, при попадании ходим еще раз
        if not is_hit:
            current_bot, opponent_bot = opponent_bot, current_bot
    
    else:
        print("\n⚠️ Достигнут лимит ходов")
    
    # Показываем финальное состояние полей
    print("\n" + "=" * 50)
    print("ФИНАЛЬНЫЕ ПОЛЯ")
    print("=" * 50)
    
    print(f"\nПоле {bot1.name} (свое):")
    print_field(bot1.own_field)
    
    print(f"\nПоле {bot1.name} (вид врага):")
    print_field(bot1.enemy_field)
    
    print(f"\nПоле {bot2.name} (свое):")
    print_field(bot2.own_field)
    
    print(f"\nПоле {bot2.name} (вид врага):")
    print_field(bot2.enemy_field)


def check_all_ships_destroyed(field: OwnField) -> bool:
    """Проверка, все ли корабли уничтожены"""
    for ship in field.ships:
        for x, y in ship.decks_coordinates:
            if field.get_cell_display(x, y) != FieldState.DESTROYED:
                return False
    return True


def print_field(field):
    """Красивый вывод поля в консоль"""
    symbols = {
        FieldState.EMPTY: "·",
        FieldState.MISS: "○",
        FieldState.UNDAMAGED: "■",
        FieldState.DAMAGED: "▲",
        FieldState.DESTROYED: "X"
    }
    
    size = field.FIELD_SIZE
    print("  " + " ".join(str(i) for i in range(size)))
    for y in range(size):
        row = [symbols[field.get_cell_display(x, y)] for x in range(size)]
        print(f"{y} " + " ".join(row))


if __name__ == "__main__":
    test_bot_battle()