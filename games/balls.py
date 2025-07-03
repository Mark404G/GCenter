import tkinter as tk
import random
import math
from tkinter import messagebox

class Balls:
    def __init__(self, root, callback=None):
        """Инициализация игры"""
        self.root = root
        self.callback = callback  # Сохраняем callback-функцию
        self.root.title("Balls")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # ===== ИГРОВЫЕ НАСТРОЙКИ =====
        # Основные параметры
        self.record = 0  # Рекордный уровень
        self.level = 0  # Текущий уровень
        self.money = 0  # Количество денег
        
        # Настройки снарядов
        self.max_ammo = 5  # Максимальное количество снарядов (начальное)
        self.ammo = self.max_ammo  # Текущее количество снарядов
        self.bonus_ammo = 1  # Количество бонусных снарядов за попадание в зеленую мишень
        self.projectile_size = 10  # Размер снаряда
        self.projectile_speed = 20  # Скорость снаряда
        
        # Настройки прицела
        self.sight_length = 200  # Длина линии прицела
        self.sight_x = 400  # Начальная позиция прицела по X
        self.sight_y = 550  # Начальная позиция прицела по Y
        self.sight_angle = 0  # Угол наклона прицела
        self.sight_speed = 3.0  # Базовая скорость поворота прицела
        self.slow_sight_speed = 0.5  # Медленная скорость при зажатом Shift
        
        # Настройки мишеней
        self.target_min_size = 20  # Минимальный размер мишени
        self.target_max_size = 60  # Максимальный размер мишени
        self.money_per_level = 5  # Базовое количество денег за уровень
        
        # Настройки магазина
        self.remove_random_obstacle_price = 5  # Цена удаления случайного препятствия
        self.remove_selected_obstacle_price = 10  # Цена удаления выбранного препятствия
        self.buy_ammo_price = 5  # Цена покупки одного снаряда
        
        # Улучшения бонусных снарядов (+2, +3, +4, +5)
        self.bonus_ammo_prices = [5, 10, 20, 40]
        self.bonus_ammo_values = [2, 3, 4, 5]
        self.bonus_ammo_level = 0  # Текущий уровень улучшения
        
        # Улучшения максимального количества снарядов (6-10)
        self.max_ammo_prices = [5, 10, 15, 20, 25]
        self.max_ammo_values = [6, 7, 8, 9, 10]
        self.max_ammo_level = 0  # Текущий уровень улучшения
        
        # Улучшения денег за уровень (6-10 руб)
        self.money_per_level_prices = [5, 10, 15, 20, 25]
        self.money_per_level_values = [6, 7, 8, 9, 10]
        self.money_per_level_upgrade_level = 0  # Текущий уровень улучшения
        self.money_per_level_upgrade = 0  # Бонус к деньгам за уровень
        
        # ===== ИНИЦИАЛИЗАЦИЯ ИНТЕРФЕЙСА =====
        self.canvas = tk.Canvas(root, bg="#cff7c7", width=800, height=600)
        self.canvas.pack()
        
        # Границы карты (коричневые)
        self.border_width = 10
        self.borders = [
            self.canvas.create_rectangle(0, 0, 800, self.border_width, fill='brown', outline='black'),
            self.canvas.create_rectangle(0, 0, self.border_width, 600, fill='brown', outline='black'),
            self.canvas.create_rectangle(800-self.border_width, 0, 800, 600, fill='brown', outline='black')
        ]
        
        # Прицел (линия и снаряд внизу)
        self.projectile_preview = self.canvas.create_oval(
            self.sight_x - 10, self.sight_y - 10,
            self.sight_x + 10, self.sight_y + 10,
            fill='blue', outline='black'
        )
        
        # Линия прицела
        self.sight_line = self.canvas.create_line(
            self.sight_x, self.sight_y,
            self.sight_x, self.sight_y - self.sight_length,
            width=1, fill='black'
        )
        
        # Элементы интерфейса
        self.level_text = self.canvas.create_text(100, 30, text=f"Уровень: {self.level}", font=('Arial', 14), fill='black')
        self.ammo_text = self.canvas.create_text(700, 30, text=f"Снаряды: {self.ammo}/{self.max_ammo}", font=('Arial', 14), fill='black')
        self.money_text = self.canvas.create_text(400, 30, text=f"Деньги: {self.money}", font=('Arial', 14), fill='black')
        self.money_change_text = None  # Текст изменения денег (появляется при изменении)
        
        # Кнопка магазина
        self.shop_button = tk.Button(
            root, 
            text="МАГАЗИН", 
            command=self.open_shop, 
            font=('Arial', 16, 'bold'),
            bg="#f5bc67",
            fg='black',
            relief=tk.RAISED,
            borderwidth=4,
            width=12,
            height=1,
            highlightbackground='brown',
            highlightthickness=3
        )
        self.shop_button.place(x=600, y=540)
        
        # Игровые объекты
        self.target = None  # Основная мишень (красная)
        self.bonus_target = None  # Бонусная мишень (зеленая)
        self.obstacles = []  # Список препятствий
        self.projectiles = []  # Список снарядов
        
        # ===== УПРАВЛЕНИЕ =====
        self.root.bind('<Left>', self.rotate_left)  # Поворот влево
        self.root.bind('<Right>', self.rotate_right)  # Поворот вправо
        self.root.bind('<Shift_L>', self.slow_aim)  # Замедление прицела
        self.root.bind('<KeyRelease-Shift_L>', self.normal_aim)  # Возврат скорости прицела
        self.root.bind('<space>', self.fire)  # Выстрел
        
        # Запуск игры
        self.game_active = True  # Флаг активности игры
        self.create_level()  # Создание уровня
        self.update_game()  # Запуск игрового цикла

    def rotate_left(self, event):
        """Поворот прицела влево"""
        if self.game_active:
            self.sight_angle -= self.sight_speed
            self.update_sight_position()

    def rotate_right(self, event):
        """Поворот прицела вправо"""
        if self.game_active:
            self.sight_angle += self.sight_speed
            self.update_sight_position()

    def slow_aim(self, event):
        """Замедление прицела при зажатом Shift"""
        self.sight_speed = self.slow_sight_speed

    def normal_aim(self, event):
        """Возврат нормальной скорости прицела"""
        self.sight_speed = 3.0

    def update_sight_position(self):
        """Обновление позиции прицела на основе текущего угла"""
        angle_rad = math.radians(self.sight_angle)  # Преобразуем угол в радианы
        # Вычисляем конечные координаты линии прицела
        end_x = self.sight_x + self.sight_length * math.sin(angle_rad)
        end_y = self.sight_y - self.sight_length * math.cos(angle_rad)
        
        # Обновляем координаты линии прицела
        self.canvas.coords(
            self.sight_line,
            self.sight_x, self.sight_y,
            end_x, end_y
        )

    def fire(self, event):
        """Выстрел снарядом"""
        if not self.game_active:
            return  # Не стреляем, если игра не активна
            
        # Проверяем, есть ли снаряды
        if self.ammo <= 0:
            # Если нет снарядов и денег на покупку, завершаем игру
            if self.money < self.buy_ammo_price:
                self.game_over()
            return
            
        self.ammo -= 1  # Уменьшаем количество снарядов
        self.update_ammo_text()  # Обновляем отображение
        
        angle_rad = math.radians(self.sight_angle)  # Угол в радианах
        
        # Создаем снаряд (синий круг)
        projectile = self.canvas.create_oval(
            self.sight_x - self.projectile_size/2, self.sight_y - self.projectile_size/2,
            self.sight_x + self.projectile_size/2, self.sight_y + self.projectile_size/2,
            fill='blue', outline='black'
        )
        
        # Добавляем снаряд в список с параметрами движения
        self.projectiles.append({
            'id': projectile,  # ID объекта на холсте
            'x': self.sight_x,  # Позиция X
            'y': self.sight_y,  # Позиция Y
            'dx': self.projectile_speed * math.sin(angle_rad),  # Скорость по X
            'dy': -self.projectile_speed * math.cos(angle_rad),  # Скорость по Y
            'speed': self.projectile_speed  # Общая скорость (не изменяется)
        })

    def create_level(self):
        """Создание нового уровня с мишенями и препятствиями"""
        # Удаляем старые мишени, если они есть
        if self.target:
            self.canvas.delete(self.target['id'])
        if self.bonus_target:
            self.canvas.delete(self.bonus_target['id'])
            self.canvas.delete(self.bonus_target['text'])
        
        # Размер мишени уменьшается с уровнем (но не меньше минимального)
        target_size = max(self.target_min_size, self.target_max_size - self.level * 2)
        
        # Создаем основную мишень (красную)
        target_created = False
        for _ in range(200):  # Делаем до 200 попыток разместить мишень
            x = random.randint(100, 700)
            y = random.randint(50, 150)  # Мишень в верхней части
            
            # Проверяем, чтобы мишень не пересекалась с препятствиями
            valid_position = True
            for obstacle in self.obstacles:
                if self.check_target_obstacle_collision(x, y, target_size, obstacle):
                    valid_position = False
                    break
            
            if valid_position:
                self.target = {
                    'id': self.canvas.create_oval(
                        x, y,
                        x + target_size, y + target_size,
                        fill='red', outline='black'
                    ),
                    'x': x,
                    'y': y,
                    'size': target_size
                }
                target_created = True
                break
        
        # Создаем бонусную мишень (зеленую)
        bonus_size = 30
        bonus_created = False
        for _ in range(200):  # Делаем до 200 попыток разместить мишень
            bx = random.randint(100, 700)
            by = random.randint(50, 150)  # Бонусная мишень тоже в верхней части
            
            # Проверяем расстояние до основной мишени
            if self.target and (abs(bx - self.target['x']) < 100 and abs(by - self.target['y']) < 100):
                continue
            
            # Проверяем, чтобы бонусная мишень не пересекалась с препятствиями
            valid_position = True
            for obstacle in self.obstacles:
                if self.check_target_obstacle_collision(bx, by, bonus_size, obstacle):
                    valid_position = False
                    break
            
            if valid_position:
                self.bonus_target = {
                    'id': self.canvas.create_oval(
                        bx, by,
                        bx + bonus_size, by + bonus_size,
                        fill='green', outline='black'
                    ),
                    'x': bx,
                    'y': by,
                    'size': bonus_size,
                    'text': self.canvas.create_text(
                        bx + bonus_size/2, by + bonus_size/2, 
                        text=f"+{self.bonus_ammo}", 
                        font=('Arial', 10)
                )}
                bonus_created = True
                break
        
        # Добавляем новое препятствие (если нужно)
        if len(self.obstacles) < self.level:
            self.add_new_obstacle()

    def check_target_obstacle_collision(self, x, y, size, obstacle):
        """Проверяет пересечение мишени с препятствием"""
        # Центры мишени и препятствия
        target_center_x = x + size/2
        target_center_y = y + size/2
        obstacle_center_x = obstacle['x'] + obstacle['size']/2
        obstacle_center_y = obstacle['y'] + obstacle['size']/2
        
        # Расстояние между центрами
        distance = math.sqrt(
            (target_center_x - obstacle_center_x)**2 +
            (target_center_y - obstacle_center_y)**2
        )
        # Проверяем пересечение (сумма радиусов больше расстояния)
        return distance < size/2 + obstacle['size']/2

    def add_new_obstacle(self):
        """Добавляет новое препятствие в центральной части экрана"""
        for _ in range(200):  # Делаем до 200 попыток разместить препятствие
            # Препятствия генерируются преимущественно в центре
            ox = random.randint(50, 750)
            oy = random.randint(100, 400)
            
            # Иногда добавляем случайные препятствия
            if random.random() < 0.3:
                ox = random.randint(50, 750)
                oy = random.randint(100, 400)
            
            osize = random.randint(30, 70)
            
            valid_position = True
            
            # Проверка с мишенями
            if self.target and self.check_target_obstacle_collision(
                self.target['x'], self.target['y'], self.target['size'], 
                {'x': ox, 'y': oy, 'size': osize}
            ):
                valid_position = False
            
            if self.bonus_target and self.check_target_obstacle_collision(
                self.bonus_target['x'], self.bonus_target['y'], self.bonus_target['size'], 
                {'x': ox, 'y': oy, 'size': osize}
            ):
                valid_position = False
            
            # Проверка с другими препятствиями
            if valid_position:
                for obstacle in self.obstacles:
                    if (abs(ox - obstacle['x']) < osize + obstacle['size'] and 
                        abs(oy - obstacle['y']) < osize + obstacle['size']):
                        valid_position = False
                        break
            
            if valid_position:
                # Создаем препятствие (коричневый квадрат)
                obstacle = {
                    'id': self.canvas.create_rectangle(
                        ox, oy,
                        ox + osize, oy + osize,
                        fill='brown', outline='black'
                    ),
                    'x': ox,
                    'y': oy,
                    'size': osize
                }
                self.obstacles.append(obstacle)
                break
    def update_game(self):
        """Основной игровой цикл с улучшенной физикой"""
        if not self.game_active:
            return
            
        # Константы физики
        FRICTION = 0.005  # Сопротивление воздуха
        GRAVITY = 0.1    # Гравитация
        
        for projectile in self.projectiles[:]:
            # Применяем гравитацию
            projectile['dy'] += GRAVITY
            
            # Применяем сопротивление воздуха
            speed = math.sqrt(projectile['dx']**2 + projectile['dy']**2)
            if speed > 0:
                projectile['dx'] -= FRICTION * projectile['dx'] / speed
                projectile['dy'] -= FRICTION * projectile['dy'] / speed
            
            # Сохраняем старую позицию для обработки коллизий
            old_x, old_y = projectile['x'], projectile['y']
            
            # Обновляем позицию
            projectile['x'] += projectile['dx']
            projectile['y'] += projectile['dy']
            
            # Обновляем отображение
            self.canvas.coords(
                projectile['id'],
                projectile['x'] - self.projectile_size/2, 
                projectile['y'] - self.projectile_size/2,
                projectile['x'] + self.projectile_size/2, 
                projectile['y'] + self.projectile_size/2
            )

            # Обработка коллизий с границами
            if projectile['x'] <= self.border_width + self.projectile_size/2:
                projectile['x'] = self.border_width + self.projectile_size/2
                projectile['dx'] = -projectile['dx'] * 0.95  # Небольшие потери при ударе
                
            elif projectile['x'] >= 800 - self.border_width - self.projectile_size/2:
                projectile['x'] = 800 - self.border_width - self.projectile_size/2
                projectile['dx'] = -projectile['dx'] * 0.95
                
            if projectile['y'] <= self.border_width + self.projectile_size/2:
                projectile['y'] = self.border_width + self.projectile_size/2
                projectile['dy'] = -projectile['dy'] * 0.95

            # Обработка коллизий с препятствиями
            for obstacle in self.obstacles:
                if self.check_collision(projectile, obstacle):
                    self.handle_obstacle_collision(projectile, obstacle, old_x, old_y)
                    break

            # Удаление снарядов за пределами экрана
            if projectile['y'] > 600 or abs(projectile['dx']) < 0.1 and abs(projectile['dy']) < 0.1:
                self.canvas.delete(projectile['id'])
                self.projectiles.remove(projectile)
                continue

            # Проверка попаданий в мишени
            self.check_target_hits(projectile)

        self.root.after(20, self.update_game)

    def handle_obstacle_collision(self, projectile, obstacle, old_x, old_y):
        """Обработка столкновения с препятствиями с учетом угла удара"""
        # Определяем стороны препятствия
        left = obstacle['x']
        right = obstacle['x'] + obstacle['size']
        top = obstacle['y']
        bottom = obstacle['y'] + obstacle['size']
        
        # Определяем, с какой стороны произошло столкновение
        if old_x < left and projectile['x'] >= left:  # Слева
            projectile['x'] = left - self.projectile_size/2
            projectile['dx'] = -abs(projectile['dx']) * 0.95
            
        elif old_x > right and projectile['x'] <= right:  # Справа
            projectile['x'] = right + self.projectile_size/2
            projectile['dx'] = abs(projectile['dx']) * 0.95
            
        if old_y < top and projectile['y'] >= top:  # Сверху
            projectile['y'] = top - self.projectile_size/2
            projectile['dy'] = -abs(projectile['dy']) * 0.95
            
        elif old_y > bottom and projectile['y'] <= bottom:  # Снизу
            projectile['y'] = bottom + self.projectile_size/2
            projectile['dy'] = abs(projectile['dy']) * 0.95

    def check_collision(self, projectile, obstacle):
        """Точная проверка столкновения круга с прямоугольником"""
        # Ближайшая точка на прямоугольнике к центру круга
        closest_x = max(obstacle['x'], min(projectile['x'], obstacle['x'] + obstacle['size']))
        closest_y = max(obstacle['y'], min(projectile['y'], obstacle['y'] + obstacle['size']))
        
        # Расстояние от центра круга до ближайшей точки
        distance = math.sqrt((projectile['x'] - closest_x)**2 + (projectile['y'] - closest_y)**2)
        
        return distance < self.projectile_size/2

    def check_target_hits(self, projectile):
        """Проверка попаданий в мишени"""
        if self.target and self.check_hit(projectile, self.target):
            earned_money = self.money_per_level + self.money_per_level_upgrade
            self.money += earned_money
            self.show_money_change(f"+{earned_money} руб")
            
            self.level += 1
            self.update_level_text()
            self.update_money_text()
            
            if self.level > self.record:
                self.record = self.level
                self.root.title(f"Gravity Balls - Рекорд: {self.record}")
            
            self.canvas.delete(self.target['id'])
            self.target = None
            self.canvas.delete(projectile['id'])
            self.projectiles.remove(projectile)
            self.root.after(300, self.create_level)
            
        elif self.bonus_target and self.check_hit(projectile, self.bonus_target):
            self.ammo = min(self.ammo + self.bonus_ammo, self.max_ammo)
            self.update_ammo_text()
            
            self.canvas.delete(self.bonus_target['id'])
            self.canvas.delete(self.bonus_target['text'])
            self.bonus_target = None
            self.canvas.delete(projectile['id'])
            self.projectiles.remove(projectile)

    def check_hit(self, projectile, target):
        """Проверяет попадание снаряда в мишень (круг в круг)"""
        # Центры мишени и снаряда
        target_center_x = target['x'] + target['size']/2
        target_center_y = target['y'] + target['size']/2
        
        # Расстояние между центрами
        distance = math.sqrt(
            (projectile['x'] - target_center_x)**2 +
            (projectile['y'] - target_center_y)**2
        )
        # Проверяем попадание (сумма радиусов больше расстояния)
        return distance < target['size']/2 + self.projectile_size/2

    def show_money_change(self, text):
        """Отображает изменение количества денег (зеленый - прибыль, красный - убыток)"""
        if self.money_change_text:
            self.canvas.delete(self.money_change_text)
        
        # Создаем текст с изменением денег
        self.money_change_text = self.canvas.create_text(
            400, 60, 
            text=text, 
            font=('Arial', 16, 'bold'),
            fill='green' if '+' in text else 'red'
        )
        # Удаляем текст через 3 секунды
        self.root.after(3000, self.clear_money_change)

    def clear_money_change(self):
        """Удаляет текст изменения денег"""
        if self.money_change_text:
            self.canvas.delete(self.money_change_text)
            self.money_change_text = None

    def open_shop(self):
        """Открывает окно магазина с улучшениями"""
        if not self.game_active:
            return
            
        shop_window = tk.Toplevel(self.root)
        shop_window.title("Магазин улучшений")
        shop_window.geometry("400x600")
        shop_window.resizable(False, False)
        
        # Основной фрейм для прокрутки
        main_frame = tk.Frame(shop_window)
        main_frame.pack(fill='both', expand=True)
        
        # Холст для скролла
        canvas = tk.Canvas(main_frame)
        canvas.pack(side='left', fill='both', expand=True)
        
        # Скроллбар
        scrollbar = tk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        # Фрейм для содержимого
        content_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor='nw')
        
        # Заголовок магазина
        tk.Label(content_frame, text="Магазин улучшений", font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        # ===== Удаление препятствий =====
        tk.Label(content_frame, text="Удаление препятствий", font=('Arial', 14, 'underline')).grid(row=1, column=0, columnspan=2, pady=5, padx=25, sticky='w')
        
        # Удаление случайного препятствия
        tk.Label(content_frame, text="Удалить случайное препятствие", font=('Arial', 12)).grid(row=2, column=0, sticky='w', padx=10)
        tk.Button(
            content_frame, 
            text=f"{self.remove_random_obstacle_price} руб", 
            command=lambda: self.buy_upgrade('remove_random_obstacle', shop_window),
            font=('Arial', 12),
            bg='#ffffa0',
            relief=tk.RAISED,
            borderwidth=2,
            width=10
        ).grid(row=2, column=1, padx=10, pady=5)
        
        # Удаление выбранного препятствия
        tk.Label(content_frame, text="Выбрать и удалить препятствие", font=('Arial', 12)).grid(row=3, column=0, sticky='w', padx=10)
        tk.Button(
            content_frame, 
            text=f"{self.remove_selected_obstacle_price} руб", 
            command=lambda: self.buy_upgrade('remove_selected_obstacle', shop_window),
            font=('Arial', 12),
            bg='#ffffa0',
            relief=tk.RAISED,
            borderwidth=2,
            width=10
        ).grid(row=3, column=1, padx=10, pady=5)
        
        # ===== Бонусные снаряды =====
        tk.Label(content_frame, text="Бонусные снаряды", font=('Arial', 14, 'underline')).grid(row=4, column=0, columnspan=2, pady=5, padx=40, sticky='w')
        
        # Текст с информацией о текущем и следующем уровне
        current_bonus = self.bonus_ammo_values[self.bonus_ammo_level-1] if self.bonus_ammo_level > 0 else 1
        if self.bonus_ammo_level < len(self.bonus_ammo_values):
            next_bonus = self.bonus_ammo_values[self.bonus_ammo_level]
            bonus_info = f"Текущий: +{current_bonus} | Следующий: +{next_bonus}"
        else:
            bonus_info = f"Максимальный уровень: +{current_bonus}"
        
        tk.Label(content_frame, text=bonus_info, font=('Arial', 12)).grid(row=5, column=0, sticky='w', padx=20)
        
        # Кнопка улучшения
        if self.bonus_ammo_level < len(self.bonus_ammo_values):
            tk.Button(
                content_frame, 
                text=f"{self.bonus_ammo_prices[self.bonus_ammo_level]} руб", 
                command=lambda: self.buy_upgrade('bonus_ammo', shop_window),
                font=('Arial', 12),
                bg='#ffffa0',
                relief=tk.RAISED,
                borderwidth=2,
                width=10
            ).grid(row=5, column=1, padx=10, pady=5)
        else:
            tk.Label(content_frame, text="Макс. уровень", font=('Arial', 12)).grid(row=5, column=1, padx=10)
        
        # ===== Максимум снарядов =====
        tk.Label(content_frame, text="Максимум снарядов", font=('Arial', 14, 'underline')).grid(row=6, column=0, columnspan=2, pady=5, padx=35, sticky='w')
        
        # Текст с информацией
        current_max = self.max_ammo_values[self.max_ammo_level-1] if self.max_ammo_level > 0 else 5
        if self.max_ammo_level < len(self.max_ammo_values):
            next_max = self.max_ammo_values[self.max_ammo_level]
            max_info = f"Текущий: {current_max} | Следующий: {next_max}"
        else:
            max_info = f"Максимальный уровень: {current_max}"
        
        tk.Label(content_frame, text=max_info, font=('Arial', 12)).grid(row=7, column=0, sticky='w', padx=25)
        
        # Кнопка улучшения
        if self.max_ammo_level < len(self.max_ammo_values):
            tk.Button(
                content_frame, 
                text=f"{self.max_ammo_prices[self.max_ammo_level]} руб", 
                command=lambda: self.buy_upgrade('max_ammo', shop_window),
                font=('Arial', 12),
                bg='#ffffa0',
                relief=tk.RAISED,
                borderwidth=2,
                width=10
            ).grid(row=7, column=1, padx=10, pady=5)
        else:
            tk.Label(content_frame, text="Макс. уровень", font=('Arial', 12)).grid(row=7, column=1, padx=10)
        
        # ===== Деньги за уровень =====
        tk.Label(content_frame, text="Деньги за уровень", font=('Arial', 14, 'underline')).grid(row=8, column=0, columnspan=2, pady=5, padx=40, sticky='w')
        
        # Текст с информацией
        current_money = self.money_per_level + (self.money_per_level_values[self.money_per_level_upgrade_level-1] if self.money_per_level_upgrade_level > 0 else 0)
        if self.money_per_level_upgrade_level < len(self.money_per_level_values):
            next_money = self.money_per_level_values[self.money_per_level_upgrade_level]
            money_info = f"Текущий: +{current_money} | Следующий: +{next_money}"
        else:
            money_info = f"Максимальный уровень: +{current_money}"
        
        tk.Label(content_frame, text=money_info, font=('Arial', 12)).grid(row=9, column=0, sticky='w', padx=15)
        
        # Кнопка улучшения
        if self.money_per_level_upgrade_level < len(self.money_per_level_values):
            tk.Button(
                content_frame, 
                text=f"{self.money_per_level_prices[self.money_per_level_upgrade_level]} руб", 
                command=lambda: self.buy_upgrade('money_per_level', shop_window),
                font=('Arial', 12),
                bg='#ffffa0',
                relief=tk.RAISED,
                borderwidth=2,
                width=10
            ).grid(row=9, column=1, padx=10, pady=5)
        else:
            tk.Label(content_frame, text="Макс. уровень", font=('Arial', 12)).grid(row=9, column=1, padx=10)
        
        # ===== Покупка снарядов =====
        tk.Label(content_frame, text="Покупка снарядов", font=('Arial', 14, 'underline')).grid(row=10, column=0, columnspan=2, pady=5, padx=45, sticky='w')
        
        tk.Label(content_frame, text="Купить 1 снаряд", font=('Arial', 12)).grid(row=11, column=0, sticky='w', padx=60)
        tk.Button(
            content_frame, 
            text=f"{self.buy_ammo_price} руб", 
            command=lambda: self.buy_upgrade('buy_ammo', shop_window),
            font=('Arial', 12),
            bg='#ffffa0',
            relief=tk.RAISED,
            borderwidth=2,
            width=10
        ).grid(row=11, column=1, padx=10, pady=5)
        
        # Кнопка закрытия магазина
        tk.Button(
            content_frame, 
            text="Закрыть магазин", 
            command=shop_window.destroy,
            font=('Arial', 12, 'bold'),
            bg='#ffffa0',
            fg='black',
            relief=tk.RAISED,
            borderwidth=3,
            width=15
        ).grid(row=12, column=0, columnspan=2, pady=20)
        
        # Обновление прокрутки
        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox('all'))

    def buy_upgrade(self, upgrade_type, window):
        """Покупка улучшения в магазине"""
        price = 0
        success = False
        message = ""
        
        if upgrade_type == 'remove_random_obstacle':
            if self.money >= self.remove_random_obstacle_price and len(self.obstacles) > 0:
                self.money -= self.remove_random_obstacle_price
                message = f"-{self.remove_random_obstacle_price} руб"
                obstacle = random.choice(self.obstacles)
                self.canvas.delete(obstacle['id'])
                self.obstacles.remove(obstacle)
                success = True
        elif upgrade_type == 'remove_selected_obstacle':
            if self.money >= self.remove_selected_obstacle_price and len(self.obstacles) > 0:
                self.money -= self.remove_selected_obstacle_price
                message = f"-{self.remove_selected_obstacle_price} руб"
                window.destroy()
                self.select_obstacle_to_remove()
                success = True
        elif upgrade_type == 'bonus_ammo' and self.bonus_ammo_level < len(self.bonus_ammo_prices):
            if self.money >= self.bonus_ammo_prices[self.bonus_ammo_level]:
                self.money -= self.bonus_ammo_prices[self.bonus_ammo_level]
                message = f"-{self.bonus_ammo_prices[self.bonus_ammo_level]} руб"
                self.bonus_ammo = self.bonus_ammo_values[self.bonus_ammo_level]
                self.bonus_ammo_level += 1
                if self.bonus_target:
                    self.canvas.itemconfig(self.bonus_target['text'], text=f"+{self.bonus_ammo}")
                success = True
        elif upgrade_type == 'max_ammo' and self.max_ammo_level < len(self.max_ammo_prices):
            if self.money >= self.max_ammo_prices[self.max_ammo_level]:
                self.money -= self.max_ammo_prices[self.max_ammo_level]
                message = f"-{self.max_ammo_prices[self.max_ammo_level]} руб"
                self.max_ammo = self.max_ammo_values[self.max_ammo_level]
                self.max_ammo_level += 1
                success = True
        elif upgrade_type == 'money_per_level' and self.money_per_level_upgrade_level < len(self.money_per_level_prices):
            if self.money >= self.money_per_level_prices[self.money_per_level_upgrade_level]:
                self.money -= self.money_per_level_prices[self.money_per_level_upgrade_level]
                message = f"-{self.money_per_level_prices[self.money_per_level_upgrade_level]} руб"
                self.money_per_level_upgrade = self.money_per_level_values[self.money_per_level_upgrade_level] - self.money_per_level
                self.money_per_level_upgrade_level += 1
                success = True
        elif upgrade_type == 'buy_ammo':
            if self.money >= self.buy_ammo_price and self.ammo < self.max_ammo:
                self.money -= self.buy_ammo_price
                message = f"-{self.buy_ammo_price} руб"
                self.ammo += 1
                success = True
        
        if success:
            self.update_money_text()
            self.update_ammo_text()
            self.show_money_change(message)
            window.destroy()
        else:
            messagebox.showerror("Ошибка", "Недостаточно денег или невозможно применить улучшение")

    def select_obstacle_to_remove(self):
        """Режим выбора препятствия для удаления"""
        if not self.obstacles:
            messagebox.showinfo("Информация", "Нет препятствий для удаления")
            return
            
        # Включаем обработку кликов по препятствиям
        self.canvas.bind('<Button-1>', self.handle_obstacle_selection)
        # Показываем подсказку
        self.canvas.create_text(400, 580, text="Выберите препятствие для удаления", font=('Arial', 14), fill='red', tags="select_text")

    def handle_obstacle_selection(self, event):
        """Обработка выбора препятствия для удаления"""
        x, y = event.x, event.y
        obstacle_removed = False

        for obstacle in self.obstacles[:]:
            if (obstacle['x'] <= x <= obstacle['x'] + obstacle['size'] and
                obstacle['y'] <= y <= obstacle['y'] + obstacle['size']):
                self.canvas.delete(obstacle['id'])
                self.obstacles.remove(obstacle)
                obstacle_removed = True
                break

        if not obstacle_removed:
            self.money += self.remove_selected_obstacle_price
            self.update_money_text()
            self.canvas.create_text(400, 580, text="Вы не попали по препятствию. Деньги возвращены", font=('Arial', 12), fill='red', tags="miss_text")
            self.show_money_change(f"+{self.remove_selected_obstacle_price} руб")
        
        self.canvas.unbind('<Button-1>')
        self.canvas.delete("select_text")
        self.canvas.after(2000, lambda: self.canvas.delete("miss_text"))

    def update_level_text(self):
        """Обновляет отображение текущего уровня"""
        self.canvas.itemconfig(self.level_text, text=f"Уровень: {self.level}")

    def update_ammo_text(self):
        """Обновляет отображение количества снарядов"""
        self.canvas.itemconfig(self.ammo_text, text=f"Снаряды: {self.ammo}/{self.max_ammo}")

    def update_money_text(self):
        """Обновляет отображение количества денег"""
        self.canvas.itemconfig(self.money_text, text=f"Деньги: {self.money}")

    def game_over(self):
        """Завершение игры и вывод статистики"""
        self.game_active = False
        
        # Отображаем текст завершения
        self.canvas.create_text(400, 250, text="ИГРА ОКОНЧЕНА!", font=('Arial', 24), fill='red')
        self.canvas.create_text(400, 300, text=f"Уровень: {self.level}", font=('Arial', 18), fill='black')
        
        # Принудительно обновляем холст
        self.canvas.update()
        
        # Задержка 3 секунды перед вызовом callback
        self.root.after(3000, self.execute_callback)

    def execute_callback(self):
        """Выполняет callback после задержки"""
        if self.callback is not None:
            self.callback(self.level)

    def restart_game(self, event=None):
        """Перезапуск игры с полным сбросом состояния"""
        # Останавливаем игровой цикл
        self.game_active = False
        
        # Полностью очищаем холст
        self.canvas.delete("all")
        
        # Сбрасываем все игровые параметры
        self.level = 0
        self.money = 0
        self.max_ammo = 5  # Начальное значение
        self.ammo = self.max_ammo
        self.bonus_ammo = 1
        self.bonus_ammo_level = 0
        self.max_ammo_level = 0
        self.money_per_level_upgrade = 0
        self.money_per_level_upgrade_level = 0
        
        # Очищаем списки объектов
        self.projectiles = []
        self.obstacles = []
        self.target = None
        self.bonus_target = None
        
        # Восстанавливаем границы
        self.border_width = 10
        self.borders = [
            self.canvas.create_rectangle(0, 0, 800, self.border_width, fill='brown', outline='black'),
            self.canvas.create_rectangle(0, 0, self.border_width, 600, fill='brown', outline='black'),
            self.canvas.create_rectangle(800-self.border_width, 0, 800, 600, fill='brown', outline='black')
        ]
        
        # Воссоздаем прицел
        self.sight_x = 400
        self.sight_y = 550
        self.sight_angle = 0
        self.sight_speed = 3.0
        
        self.projectile_preview = self.canvas.create_oval(
            self.sight_x - 10, self.sight_y - 10,
            self.sight_x + 10, self.sight_y + 10,
            fill='blue', outline='black'
        )
        
        self.sight_line = self.canvas.create_line(
            self.sight_x, self.sight_y,
            self.sight_x, self.sight_y - self.sight_length,
            width=1, fill='black'
        )
        
        # Воссоздаем элементы интерфейса
        self.level_text = self.canvas.create_text(100, 30, text=f"Уровень: {self.level}", font=('Arial', 14), fill='black')
        self.ammo_text = self.canvas.create_text(700, 30, text=f"Снаряды: {self.ammo}/{self.max_ammo}", font=('Arial', 14), fill='black')
        self.money_text = self.canvas.create_text(400, 30, text=f"Деньги: {self.money}", font=('Arial', 14), fill='black')
        self.money_change_text = None
        
        # Воссоздаем кнопку магазина
        self.shop_button = tk.Button(
            self.root, 
            text="МАГАЗИН", 
            command=self.open_shop, 
            font=('Arial', 16, 'bold'),
            bg="#f5bc67",
            fg='black',
            relief=tk.RAISED,
            borderwidth=4,
            width=12,
            height=1,
            highlightbackground='brown',
            highlightthickness=3
        )
        self.shop_button.place(x=600, y=540)
        
        # Запускаем игру заново
        self.game_active = True
        self.create_level()
        self.update_game()
        
if __name__ == "__main__":
    root = tk.Tk()
    game = Balls(root)
    root.mainloop()