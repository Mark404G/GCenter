import tkinter as tk
import random
from collections import deque

class Snake:
    def __init__(self, parent_window, on_game_end):
        """
        Инициализация игры Змейка
        :param parent_window: Окно Game Center (для возврата управления)
        :param on_game_end: Функция, вызываемая при завершении игры (передает счет)
        """
        # --- Настройки игры (легко изменяемые параметры) ---
        self.WIDTH = 600               # Ширина игрового поля
        self.HEIGHT = 600              # Высота игрового поля
        self.CELL_SIZE = 15            # Размер одной клетки змейки/еды
        self.DELAY = 100               # Задержка между движениями (мс)
        self.INITIAL_SNAKE_LENGTH = 3  # Начальная длина змейки
        self.MINE_SPAWN_SCORE = 10     # Каждые 10 очков добавляется мина
        self.MAX_MINE_SIZE = 5         # Максимальный размер мины (в клетках)
        
        # Цвета и оформление
        self.BG_COLOR = "black"        # Цвет фона
        self.SNAKE_COLOR = "green"     # Цвет змейки
        self.SNAKE_OUTLINE = "darkgreen"  # Контур змейки
        self.MINE_COLOR = "white"      # Цвет мин
        self.TEXT_COLOR = "white"      # Цвет текста
        
        # Настройки шрифтов
        self.MAIN_FONT = ("Arial", 16)      # Основной шрифт
        self.BONUS_FONT = ("Arial", 24)     # Шрифт бонусных сообщений
        
        # Направления движения
        self.DIRECTIONS = ["Up", "Down", "Left", "Right"]
        
        # Типы еды с их свойствами
        self.FOOD_TYPES = {
            "blue": {"color": "deep sky blue", "value": 1, "spawn_chance": 0.7, "size": 1},
            "yellow": {"color": "yellow", "value": 4, "spawn_chance": 0.2, "size": 2},
            "red": {"color": "red", "value": 9, "spawn_chance": 0.07, "size": 3},
            "purple": {"color": "purple", "value": 16, "spawn_chance": 0.03, "size": 4}
        }
        
        # Сообщения при завершении игры
        self.ATE_A_MINE = [
            "Взрывной финал!", 
            "Мина решила не церемониться", 
            "Взрыв эмоций и змейка в прошлом", 
            "Этим всё и закончилось!", 
            "Минуту назад было всё хорошо", 
            "Не всё, что блестит — безопасно",
            "Змейка попала под раздачу",
            "Урок выучен — мину обходить!"
        ]
        
        self.ATE_HIMSELF = [
            "Ну вот, сожрал сам себя!",
            "Ужин в стиле каннибала", 
            "Вот так и теряют голову… и хвост", 
            "Съесть себя — новый тренд!", 
            "Проблемы с самоидентификацией?",
            "Сам себя победил",
            "Ты - не ты, когда голоден!"
        ]
        
        # --- Инициализация игровых переменных ---
        self.parent_window = parent_window  # Ссылка на главное окно
        self.on_game_end = on_game_end      # Функция обратного вызова
        
        self.snake = []          # Координаты сегментов змейки
        self.direction = None    # Текущее направление движения
        self.next_direction = None  # Следующее направление (для плавного управления)
        self.score = 0           # Текущий счет
        self.high_score = 0      # Рекордный счет
        self.game_started = False # Флаг начала игры
        self.game_over = False   # Флаг завершения игры
        self.food = None         # Текущая еда (x, y, тип)
        self.bonus_texts = deque(maxlen=10)  # Очередь бонусных сообщений
        self.mines = []          # Список мин (x, y, размер)
        self.food_counter = 0    # Счетчик созданной еды (для статистики)
        
        # --- Создание игрового интерфейса ---
        self.parent_window = parent_window  # Сохраняем ссылку на главное окно
        self.root = tk.Toplevel(parent_window)
        self.root.title("Snake")
        self.root.resizable(False, False)
        
        # Сворачиваем главное окно при запуске игры
        self.parent_window.iconify()
        
        # Холст для рисования игры
        self.canvas = tk.Canvas(
            self.root, 
            width=self.WIDTH, 
            height=self.HEIGHT, 
            bg=self.BG_COLOR, 
            highlightthickness=0
        )
        self.canvas.pack()
        
        # --- Инициализация игрового состояния ---
        self.snake = self.create_snake()
        self.food = self.create_food()
        
        # Стартовое сообщение
        self.canvas.create_text(
            self.WIDTH // 2, 
            self.HEIGHT // 2,
            text="Нажмите стрелку для старта (кроме ←)",
            fill=self.TEXT_COLOR,
            font=self.MAIN_FONT
        )
        
        # --- Настройка управления ---
        self.root.bind("<KeyPress>", self.on_key_press)
        
        # Первоначальная отрисовка
        self.draw_food()
        self.draw_snake()
        
        # Запуск игрового цикла
        self.game_loop()
        
        # Обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_close(self):
        """Обработчик закрытия окна игры"""
        self.root.destroy()
        self.parent_window.deiconify()  # Восстанавливаем главное окно
        self.on_game_end(self.score)    # Передаем счет в Game Center
    
    def create_snake(self):
        """
        Создает начальное положение змейки
        :return: Список координат сегментов змейки
        """
        # Вычисляем максимальные координаты для головы змейки
        max_x = (self.WIDTH // self.CELL_SIZE) - 3
        max_y = (self.HEIGHT // self.CELL_SIZE) - 1
        
        # Случайная позиция головы
        x = random.randint(3, max_x) * self.CELL_SIZE
        y = random.randint(0, max_y) * self.CELL_SIZE
        
        # Создаем змейку из INITIAL_SNAKE_LENGTH сегментов, идущих горизонтально вправо
        return [
            (x, y), 
            (x - self.CELL_SIZE, y), 
            (x - 2 * self.CELL_SIZE, y)
        ][:self.INITIAL_SNAKE_LENGTH]
    
    def is_far_from_snake(self, coord, min_distance=3):
        """
        Проверяет, что координата находится на достаточном расстоянии от змейки
        :param coord: Проверяемая координата (x, y)
        :param min_distance: Минимальное расстояние в клетках
        :return: True если координата безопасна
        """
        x, y = coord
        
        # Проверяем расстояние до каждого сегмента змейки
        for segment in self.snake:
            sx, sy = segment
            # Используем "чебышевское расстояние" (максимум по координатам)
            if max(abs(sx - x), abs(sy - y)) < min_distance * self.CELL_SIZE:
                return False
        
        # Дополнительная проверка направления движения змейки
        if len(self.snake) > 1:
            head_x, head_y = self.snake[0]
            second_x, second_y = self.snake[1]
            
            # Определяем направление движения
            if head_x == second_x:  # Движение по вертикали
                if self.direction == "Up":
                    # Проверяем область перед змейкой (выше головы)
                    if (head_x - self.CELL_SIZE <= x <= head_x + self.CELL_SIZE and 
                        head_y - min_distance*self.CELL_SIZE <= y <= head_y):
                        return False
                elif self.direction == "Down":
                    # Проверяем область перед змейкой (ниже головы)
                    if (head_x - self.CELL_SIZE <= x <= head_x + self.CELL_SIZE and 
                        head_y <= y <= head_y + min_distance*self.CELL_SIZE):
                        return False
            elif head_y == second_y:  # Движение по горизонтали
                if self.direction == "Left":
                    # Проверяем область перед змейкой (левее головы)
                    if (head_y - self.CELL_SIZE <= y <= head_y + self.CELL_SIZE and 
                        head_x - min_distance*self.CELL_SIZE <= x <= head_x):
                        return False
                elif self.direction == "Right":
                    # Проверяем область перед змейкой (правее головы)
                    if (head_y - self.CELL_SIZE <= y <= head_y + self.CELL_SIZE and 
                        head_x <= x <= head_x + min_distance*self.CELL_SIZE):
                        return False
        
        return True
    
    def is_far_from_mines(self, coord, min_distance=2):
        """
        Проверяет, что координата находится на достаточном расстоянии от всех мин
        :param coord: Проверяемая координата (x, y)
        :param min_distance: Минимальное расстояние в клетках
        :return: True если координата безопасна
        """
        x, y = coord
        
        for mine in self.mines:
            mx, my, size = mine
            # Проверяем расстояние до каждой клетки мины
            for i in range(size):
                for j in range(size):
                    mine_coord = (mx + i*self.CELL_SIZE, my + j*self.CELL_SIZE)
                    distance = max(abs(mine_coord[0] - x), abs(mine_coord[1] - y))
                    if distance < min_distance * self.CELL_SIZE:
                        return False
        return True
    
    def create_food(self):
        """
        Создает новую еду на поле с учетом вероятностей появления разных типов
        :return: Кортеж (x, y, тип_еды)
        """
        while True:  # Продолжаем попытки, пока не найдем валидную позицию
            # Выбираем тип еды на основе вероятностей
            rand = random.random()  # Случайное число от 0 до 1
            selected_type = None
            
            # Перебираем типы еды в порядке убывания вероятности
            for food_type, props in self.FOOD_TYPES.items():
                if rand <= props["spawn_chance"]:
                    selected_type = food_type
                    break
                rand -= props["spawn_chance"]  # Уменьшаем случайное число
            
            # Если ни один тип не выбран (из-за ошибок округления), выбираем синюю еду
            if selected_type is None:
                selected_type = "blue"
            
            props = self.FOOD_TYPES[selected_type]
            size = props["size"]  # Размер еды в клетках
            
            # Вычисляем максимальные координаты для размещения еды
            max_x = (self.WIDTH - (self.CELL_SIZE * size)) // self.CELL_SIZE
            max_y = (self.HEIGHT - (self.CELL_SIZE * size)) // self.CELL_SIZE
            
            # Случайные координаты
            x = random.randint(0, max_x) * self.CELL_SIZE
            y = random.randint(0, max_y) * self.CELL_SIZE
            
            # Проверяем, что все клетки еды свободны
            valid_position = True
            for i in range(size):
                for j in range(size):
                    coord = (x + i*self.CELL_SIZE, y + j*self.CELL_SIZE)
                    # Если клетка занята змейкой или миной - позиция невалидна
                    if coord in self.snake or self.is_coord_in_mines(coord):
                        valid_position = False
                        break
                if not valid_position:
                    break
            
            # Если позиция валидна - возвращаем еду
            if valid_position:
                self.food_counter += 1
                return (x, y, selected_type)
    
    def is_coord_in_mines(self, coord):
        """
        Проверяет, находится ли координата внутри любой мины
        :param coord: Проверяемая координата (x, y)
        :return: True если координата внутри мины
        """
        x, y = coord
        for mine in self.mines:
            mx, my, size = mine
            # Проверяем вхождение координаты в прямоугольник мины
            if (mx <= x < mx + size*self.CELL_SIZE and 
                my <= y < my + size*self.CELL_SIZE):
                return True
        return False
    
    def can_increase_mine(self, mine_index, new_size):
        """
        Проверяет возможность увеличения мины до нового размера
        :param mine_index: Индекс мины в списке mines
        :param new_size: Новый размер мины
        :return: True если увеличение возможно
        """
        x, y, old_size = self.mines[mine_index]
        
        # Проверяем все новые клетки, которые добавит увеличение
        for i in range(old_size, new_size):
            for j in range(old_size, new_size):
                new_x = x + i*self.CELL_SIZE
                new_y = y + j*self.CELL_SIZE
                
                # Проверка выхода за границы поля
                if new_x >= self.WIDTH or new_y >= self.HEIGHT:
                    return False
                
                # Проверка на другие объекты
                if ((new_x, new_y) in self.snake or 
                    self.is_coord_in_mines((new_x, new_y)) or 
                    (self.food is not None and 
                     self.is_coord_in_food((new_x, new_y), self.food))):
                    return False
                
                # Проверка расстояния до других мин
                for idx, other_mine in enumerate(self.mines):
                    if idx != mine_index:
                        ox, oy, osize = other_mine
                        # Проверяем расстояние до каждой клетки другой мины
                        for oi in range(osize):
                            for oj in range(osize):
                                distance = max(
                                    abs((ox + oi*self.CELL_SIZE) - new_x), 
                                    abs((oy + oj*self.CELL_SIZE) - new_y)
                                )
                                if distance < 2 * self.CELL_SIZE:  # Минимум 1 клетка промежутка
                                    return False
        return True
    
    def add_mine(self):
        """Добавляет новую мину на поле и увеличивает существующие, если возможно"""
        attempts = 0
        while attempts < 100:  # Ограничиваем количество попыток
            # Случайные координаты для мины размером 1x1
            x = random.randint(0, (self.WIDTH - self.CELL_SIZE) // self.CELL_SIZE) * self.CELL_SIZE
            y = random.randint(0, (self.HEIGHT - self.CELL_SIZE) // self.CELL_SIZE) * self.CELL_SIZE
            mine_size = 1
            
            # Проверяем расстояние до змейки
            if not self.is_far_from_snake((x, y), 3):
                attempts += 1
                continue
                
            # Проверяем другие условия
            valid_position = True
            for i in range(mine_size):
                for j in range(mine_size):
                    coord = (x + i*self.CELL_SIZE, y + j*self.CELL_SIZE)
                    if (coord in self.snake or 
                        self.is_coord_in_mines(coord) or
                        (self.food is not None and 
                         self.is_coord_in_food(coord, self.food))):
                        valid_position = False
                        break
                if not valid_position:
                    break
            
            # Если позиция валидна и далеко от других мин - добавляем мину
            if valid_position and self.is_far_from_mines((x, y), 2):
                self.mines.append((x, y, mine_size))
                
                # Пытаемся увеличить старые мины
                for i in range(len(self.mines) - 1):
                    x_old, y_old, size_old = self.mines[i]
                    if size_old < self.MAX_MINE_SIZE:
                        new_size = size_old + 1
                        if self.can_increase_mine(i, new_size):
                            self.mines[i] = (x_old, y_old, new_size)
                return
            attempts += 1
    
    def is_coord_in_food(self, coord, food_item):
        """
        Проверяет, находится ли координата внутри еды
        :param coord: Проверяемая координата (x, y)
        :param food_item: Объект еды (x, y, тип)
        :return: True если координата внутри еды
        """
        x, y, food_type = food_item
        size = self.FOOD_TYPES[food_type]["size"]
        # Проверяем все клетки, занимаемые едой
        for i in range(size):
            for j in range(size):
                if (x + i*self.CELL_SIZE, y + j*self.CELL_SIZE) == coord:
                    return True
        return False
    
    def draw_food(self):
        """Рисует еду на холсте"""
        if not self.food:
            return
            
        x, y, food_type = self.food
        props = self.FOOD_TYPES[food_type]
        color = props["color"]
        size = props["size"]
        
        # Рисуем каждую клетку еды
        for i in range(size):
            for j in range(size):
                self.canvas.create_rectangle(
                    x + i*self.CELL_SIZE, 
                    y + j*self.CELL_SIZE,
                    x + (i+1)*self.CELL_SIZE, 
                    y + (j+1)*self.CELL_SIZE,
                    fill=color, 
                    outline="black"
                )
    
    def draw_snake(self):
        """Рисует змейку на холсте"""
        for segment in self.snake:
            self.canvas.create_rectangle(
                segment[0], 
                segment[1],
                segment[0] + self.CELL_SIZE, 
                segment[1] + self.CELL_SIZE,
                fill=self.SNAKE_COLOR, 
                outline=self.SNAKE_OUTLINE
            )
    
    def draw_mines(self):
        """Рисует мины на холсте"""
        for mine in self.mines:
            x, y, size = mine
            # Рисуем каждую клетку мины
            for i in range(size):
                for j in range(size):
                    self.canvas.create_rectangle(
                        x + i*self.CELL_SIZE, 
                        y + j*self.CELL_SIZE,
                        x + (i+1)*self.CELL_SIZE, 
                        y + (j+1)*self.CELL_SIZE,
                        fill=self.MINE_COLOR, 
                        outline="black"
                    )
    
    def draw_bonus_texts(self):
        """Рисует тексты бонусов и обновляет их время жизни"""
        for text_info in self.bonus_texts:
            x, y, text, color, time_left = text_info
            if time_left > 0:
                self.canvas.create_text(
                    x, y, 
                    text=text, 
                    fill=color, 
                    font=self.BONUS_FONT
                )
                # Уменьшаем оставшееся время жизни текста
                text_info[4] = time_left - self.DELAY/1000
    
    def add_bonus_text(self, x, y, value):
        """
        Добавляет текст бонуса в очередь для отображения
        :param x: X-координата
        :param y: Y-координата
        :param value: Значение бонуса
        """
        colors = {
            1: "deep sky blue",
            4: "gold",
            9: "red",
            16: "purple"
        }
        color = colors.get(value, "white")  # Получаем цвет по значению
        text = f"+{value}"
        # Добавляем текст в очередь: координаты, текст, цвет и время жизни (1 секунда)
        self.bonus_texts.append([x + self.CELL_SIZE, y + self.CELL_SIZE, text, color, 1.0])
    
    def move_snake(self):
        """Обрабатывает движение змейки и столкновения"""
        if not self.game_started or self.game_over:
            return
        
        # Обновляем направление, если было изменение
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None
        
        # Получаем координаты головы
        head_x, head_y = self.snake[0]
        
        # Вычисляем новую позицию головы
        if self.direction == "Up":
            new_head = (head_x, head_y - self.CELL_SIZE)
        elif self.direction == "Down":
            new_head = (head_x, head_y + self.CELL_SIZE)
        elif self.direction == "Left":
            new_head = (head_x - self.CELL_SIZE, head_y)
        elif self.direction == "Right":
            new_head = (head_x + self.CELL_SIZE, head_y)
        else:
            return
        
        # Обеспечиваем "телепортацию" через границы
        new_head = (
            new_head[0] % self.WIDTH,
            new_head[1] % self.HEIGHT
        )
        
        # Добавляем новую голову
        self.snake.insert(0, new_head)
        
        # Проверяем столкновение с миной
        if self.is_coord_in_mines(new_head):
            self.game_over = True
            self.end_game(f"{random.choice(self.ATE_A_MINE)}\n")
            return
        
        # Проверяем столкновение с собой
        if new_head in self.snake[1:]:
            self.game_over = True
            self.end_game(f"{random.choice(self.ATE_HIMSELF)}\n")
            return
        
        # Проверяем съедание еды
        food_type = self.food[2]
        props = self.FOOD_TYPES[food_type]
        size = props["size"]
        
        # Получаем все координаты, занимаемые едой
        food_coords = [
            (self.food[0] + i*self.CELL_SIZE, self.food[1] + j*self.CELL_SIZE) 
            for i in range(size) for j in range(size)
        ]
        
        # Если голова попала в еду
        if (new_head[0], new_head[1]) in food_coords:
            points = props["value"]
            self.score += points
            
            # Обновляем рекорд
            if self.score > self.high_score:
                self.high_score = self.score
            
            # Добавляем мину каждые MINE_SPAWN_SCORE очков
            if self.score // self.MINE_SPAWN_SCORE > (len(self.mines) - 1):
                self.add_mine()
            
            # Добавляем бонусное сообщение
            self.add_bonus_text(self.food[0], self.food[1], points)
            
            # Увеличиваем змейку на (value - 1) сегментов
            for _ in range(props["value"] - 1):
                self.snake.append(self.snake[-1])
            
            # Создаем новую еду
            self.food = self.create_food()
        else:
            # Если не съели еду - удаляем хвост
            self.snake.pop()
    
    def end_game(self, message="Игра окончена!"):
        """
        Завершает игру с эффектом мигания
        :param message: Сообщение для показа в конце
        """
        self.game_over = True
        blink_counter = 0
        
        def blink_effect():
            nonlocal blink_counter
            
            if blink_counter < 6:  # 6 фаз мигания (3 полных цикла)
                if blink_counter % 2 == 0:
                    # Показываем черный экран
                    self.canvas.delete("all")
                    self.canvas.create_rectangle(0, 0, self.WIDTH, self.HEIGHT, fill=self.BG_COLOR)
                else:
                    # Показываем последний кадр игры
                    self.canvas.delete("all")
                    self.draw_food()
                    self.draw_snake()
                    self.draw_mines()
                    self.draw_bonus_texts()
                
                blink_counter += 1
                self.root.after(500, blink_effect)  # 0.5 секунды между сменами
            else:
                # После мигания показываем финальное сообщение
                self.canvas.delete("all")
                self.canvas.create_text(
                    self.WIDTH // 2, 
                    self.HEIGHT // 2,
                    text=f"{message} Результат: {self.score}",
                    fill=self.TEXT_COLOR,
                    font=self.MAIN_FONT,
                    justify="center"
                )
                # Закрываем окно через 3 секунды
                self.root.after(3000, self.on_close)
        
        # Начинаем мигание
        blink_effect()
    
    def update_title(self):
        """Обновляет заголовок окна с текущим счетом"""
        self.root.title(f"Snake | Результат: {self.score}")
    
    def on_key_press(self, event):
        """
        Обрабатывает нажатия клавиш
        :param event: Событие клавиши
        """
        key = event.keysym
        
        if key in self.DIRECTIONS:
            if not self.game_started and not self.game_over:
                # В начале игры запрещаем старт с движения влево
                if key == "Left":
                    return
                
                self.game_started = True
                self.direction = key
                self.canvas.delete("all")
            elif not self.game_over:
                # Запрещаем разворот на 180 градусов
                if (key == "Up" and self.direction != "Down" or
                    key == "Down" and self.direction != "Up" or
                    key == "Left" and self.direction != "Right" or
                    key == "Right" and self.direction != "Left"):
                    self.next_direction = key

    
    def game_loop(self):
        """Главный игровой цикл"""
        if not self.game_over:
            if self.game_started:
                self.move_snake()
                
                if not self.game_over:
                    self.canvas.delete("all")
                    self.draw_food()
                    self.draw_snake()
                    self.draw_mines()
                    self.draw_bonus_texts()
                    self.update_title()
            
            # Рекурсивный вызов через DELAY миллисекунд
            self.root.after(self.DELAY, self.game_loop)


# Пример использования (для теста)
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно
    
    def handle_game_end(score):
        print(f"Игра окончена! Счёт: {score}")
        root.destroy()
    
    # Запуск игры
    game = Snake(root, handle_game_end)
    root.mainloop()