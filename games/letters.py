import tkinter as tk
import random
import string
import time

class Letters:
    def __init__(self, parent_window, callback=None):
        """
        Игра Letters с буквами, оптимизированная для интеграции с Game Center.
        """
        self.parent_window = parent_window  # Ссылка на главное окно
        self.callback = callback           # Функция для возврата результата
        
        # ========== НАСТРОЙКИ ИГРЫ ==========
        self.WIDTH = 800                   # Ширина игрового поля
        self.HEIGHT = 600                  # Высота игрового поля
        self.LINE_Y = 500                  # Y-координата линии поражения
        self.BG_COLOR = 'black'            # Цвет фона
        
        # Настройки букв
        self.LETTER_RADIUS = 28            # Радиус круга с буквой
        self.LETTER_FONT = ('Arial', 22, 'bold')  # Шрифт букв
        self.REAL_COLOR = '#4682B4'        # Цвет настоящих букв
        self.FAKE_COLOR = '#FF6347'        # Цвет фальшивых букв
        self.FAKE_CHANCE = 0.10            # Вероятность фальшивой буквы
        
        # Настройки скорости
        self.BASE_SPEED = 1.00             # Начальная скорость падения
        self.SPEED_INCREASE = 0.05         # Увеличение скорости за попадание
        self.MAX_SPEED = 6.00              # Максимальная скорость
        
        # Настройки появления букв
        self.MIN_SPAWN_DELAY = 700         # Минимальная задержка (мс)
        self.MAX_SPAWN_DELAY = 2000        # Максимальная задержка (мс)
        self.SPAWN_ACCEL = 0.98            # Коэф. ускорения появления букв
        self.TARGET_LETTERS = 6            # Целевое количество букв
        
        # Настройки анимации
        self.HIT_ANIM_DURATION = 30        # Длительность анимации попадания
        self.HIT_ANIM_SPEED = 2            # Скорость анимации попадания
        self.REAL_HIT_COLOR = '#7CFC00'    # Цвет анимации для настоящих букв
        self.FAKE_HIT_COLOR = '#FFA500'    # Цвет анимации для фальшивых
        
        # Соответствие английских и русских букв (QWERTY -> ЙЦУКЕН)
        self.KEYBOARD_LAYOUT = {
            'Q': 'Й', 'W': 'Ц', 'E': 'У', 'R': 'К', 'T': 'Е', 'Y': 'Н',
            'U': 'Г', 'I': 'Ш', 'O': 'Щ', 'P': 'З', 'A': 'Ф', 'S': 'Ы',
            'D': 'В', 'F': 'А', 'G': 'П', 'H': 'Р', 'J': 'О', 'K': 'Л',
            'L': 'Д', 'Z': 'Я', 'X': 'Ч', 'C': 'С', 'V': 'М', 'B': 'И',
            'N': 'Т', 'M': 'Ь'
        }
        
        # ========== ИГРОВЫЕ ПЕРЕМЕННЫЕ ==========
        self.score = 0                      # Текущий счет
        self.current_speed = self.BASE_SPEED
        self.spawn_delay = self.MAX_SPAWN_DELAY
        self.game_active = False
        self.letters = []                   # Список активных букв
        self.animations = []                # Список активных анимаций
        self.active_letters = set()         # Множество букв на экране
        
        # ========== СОЗДАНИЕ ИНТЕРФЕЙСА ==========
        self.root = tk.Toplevel(parent_window)
        self.root.title("Letters")
        self.root.resizable(False, False)
        
        # Сворачиваем главное окно
        self.parent_window.iconify()
        
        self.canvas = tk.Canvas(self.root, width=self.WIDTH, height=self.HEIGHT, 
                               bg=self.BG_COLOR)
        self.canvas.pack()
        
        # Линия поражения
        self.canvas.create_line(0, self.LINE_Y, self.WIDTH, self.LINE_Y, 
                              fill='red', width=1)
        
        # Элементы интерфейса
        self.score_text = self.canvas.create_text(
            80, 30, text="Счёт: 0", fill='white', 
            font=('Arial', 20, 'bold'))
        
        self.speed_text = self.canvas.create_text(
            self.WIDTH//2, 30, text=f"Скорость: {self.BASE_SPEED:.2f}x", 
            fill='silver', font=('Arial', 16))
        
        self.instruction = self.canvas.create_text(
            self.WIDTH//2, self.HEIGHT//2, 
            text="Нажмите ENTER чтобы начать", 
            fill='white', font=('Arial', 24, 'bold'))
        
        # ========== НАСТРОЙКА УПРАВЛЕНИЯ ==========
        self.root.bind('<Key>', self.handle_key_press)
        self.root.bind('<Return>', lambda e: self.start_game())
        
        # Обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Обработчик закрытия окна игры"""
        self.root.destroy()
        self.parent_window.deiconify()  # Восстанавливаем главное окно
        if self.callback:
            self.callback(self.score)   # Передаем счет в Game Center

    def start_game(self, event=None):
        """Начинает новую игру"""
        if self.game_active:
            return
            
        self.clear_canvas()
        self.game_active = True
        self.score = 0
        self.current_speed = self.BASE_SPEED
        self.spawn_delay = self.MAX_SPAWN_DELAY
        self.active_letters = set()
        
        # Обновляем интерфейс
        self.canvas.itemconfig(self.instruction, state='hidden')
        self.update_score()
        
        # Запускаем игровые процессы
        self.spawn_letter()
        self.fall_letters()

    def clear_canvas(self):
        """Очищает холст от всех объектов кроме статичных элементов"""
        for item in self.canvas.find_all():
            if item not in [self.score_text, self.speed_text, self.instruction]:
                self.canvas.delete(item)
        
        self.letters = []
        self.animations = []
        self.active_letters = set()
        
        # Восстанавливаем линию
        self.canvas.create_line(0, self.LINE_Y, self.WIDTH, self.LINE_Y, 
                              fill='red', width=1)

    def spawn_letter(self):
        """Создает новую падающую букву"""
        if not self.game_active:
            return
            
        # Выбираем случайную букву (английскую)
        letter = random.choice(string.ascii_uppercase)
        
        # Проверяем, нет ли уже такой буквы на экране
        while letter in self.active_letters:
            letter = random.choice(string.ascii_uppercase)
            
        self.active_letters.add(letter)
        
        # Определяем тип буквы (10% chance для фальшивой)
        is_fake = random.random() < self.FAKE_CHANCE
        
        # Случайная позиция по X
        x = random.randint(self.LETTER_RADIUS, self.WIDTH-self.LETTER_RADIUS)
        
        # Создаем графические элементы
        circle_id = self.canvas.create_oval(
            x-self.LETTER_RADIUS, -self.LETTER_RADIUS*2,
            x+self.LETTER_RADIUS, 0,
            fill=self.FAKE_COLOR if is_fake else self.REAL_COLOR,
            outline='white',
            width=2
        )
        
        text_id = self.canvas.create_text(
            x, -self.LETTER_RADIUS,
            text=letter, 
            fill='white', 
            font=self.LETTER_FONT
        )
        
        # Добавляем букву в список активных
        self.letters.append({
            'circle': circle_id,
            'text': text_id,
            'letter': letter,
            'x': x,
            'y': -self.LETTER_RADIUS,
            'speed': self.current_speed,
            'hit': False,
            'fake': is_fake,
            'spawn_time': time.time()
        })
        
        # Регулируем скорость спавна
        letters_count = len(self.letters)
        if letters_count < self.TARGET_LETTERS:
            self.spawn_delay = max(self.MIN_SPAWN_DELAY, self.spawn_delay * self.SPAWN_ACCEL)
        else:
            self.spawn_delay = min(self.MAX_SPAWN_DELAY, self.spawn_delay / self.SPAWN_ACCEL)
        
        # Планируем следующую букву
        self.root.after(int(self.spawn_delay), self.spawn_letter)

    def fall_letters(self):
        """Обновляет позиции всех падающих букв"""
        if not self.game_active:
            return
            
        for letter in self.letters[:]:
            # Увеличиваем скорость со временем
            time_alive = time.time() - letter['spawn_time']
            speed_mult = 1.0 + min(4.0, (time_alive / 8.0) ** 1.5)
            letter['y'] += letter['speed'] * speed_mult
            
            # Обновляем позицию
            self.canvas.coords(
                letter['circle'],
                letter['x']-self.LETTER_RADIUS, letter['y']-self.LETTER_RADIUS,
                letter['x']+self.LETTER_RADIUS, letter['y']+self.LETTER_RADIUS
            )
            self.canvas.coords(letter['text'], letter['x'], letter['y'])
            
            # Проверка достижения линии
            if letter['y'] - self.LETTER_RADIUS > self.LINE_Y and not letter['hit']:
                if letter['fake']:
                    # Фальшивая буква прошла линию — +1 очко
                    self.score += 1
                    self.update_score()
                    self.show_hit_animation(letter['x'], letter['y'], is_fake=True)
                else:
                    # Настоящая буква прошла линию — проигрыш
                    self.game_over()
                    return
                
                self.remove_letter(letter)
        
        # Обновляем скорость в интерфейсе
        self.canvas.itemconfig(self.speed_text, text=f"Скорость: {self.current_speed:.2f}x")
        
        # Следующий кадр
        self.animations.append(self.root.after(16, self.fall_letters))

    def handle_key_press(self, event):
        """Обрабатывает нажатия клавиш с поддержкой русской раскладки"""
        if event.keysym == 'Return':
            self.start_game()
            return
            
        if not self.game_active:
            return
            
        # Получаем символ в верхнем регистре
        key = event.char.upper() if event.char else ''
        
        # Преобразуем русскую букву в английскую (если нужно)
        if key in self.KEYBOARD_LAYOUT.values():
            key = next(k for k, v in self.KEYBOARD_LAYOUT.items() if v == key)
        
        # Игнорируем не-буквы
        if not key.isalpha():
            return
            
        hit_any = False
        
        # Проверяем все буквы на экране
        for letter in self.letters[:]:
            if letter['letter'] == key and not letter['hit']:
                if letter['fake']:
                    # Нажали фальшивую — проигрыш
                    self.game_over()
                    return
                else:
                    # Нажали настоящую — +1 очко
                    letter['hit'] = True
                    hit_any = True
                    self.score += 1
                    self.update_score()
                    self.show_hit_animation(letter['x'], letter['y'])
                    self.current_speed = min(self.MAX_SPEED, self.current_speed + self.SPEED_INCREASE)
        
        if hit_any:
            for letter in self.letters[:]:
                if letter['hit']:
                    self.remove_letter(letter)

    def remove_letter(self, letter):
        """Удаляет букву с экрана"""
        self.canvas.delete(letter['circle'])
        self.canvas.delete(letter['text'])
        self.letters.remove(letter)
        self.active_letters.discard(letter['letter'])

    def show_hit_animation(self, x, y, is_fake=False):
        """Анимация попадания"""
        text = "+1"
        color = self.FAKE_HIT_COLOR if is_fake else self.REAL_HIT_COLOR
        
        anim_id = self.canvas.create_text(
            x, y-30, 
            text=text, 
            fill=color,
            font=('Arial', 24, 'bold')
        )
        
        def move_animation(step=0):
            if step < self.HIT_ANIM_DURATION:
                self.canvas.move(anim_id, 0, -self.HIT_ANIM_SPEED)
                self.root.after(16, lambda: move_animation(step+1))
            else:
                self.canvas.delete(anim_id)
                
        move_animation()

    def update_score(self):
        """Обновляет счет на экране"""
        self.canvas.itemconfig(self.score_text, text=f"Счёт: {self.score}")

    def game_over(self):
        """Завершает игру с задержкой"""
        self.game_active = False
        
        for anim in self.animations:
            self.root.after_cancel(anim)
        self.animations = []
        
        # Показываем финальное сообщение
        self.canvas.create_text(
            self.WIDTH//2, self.HEIGHT//2,
            text=f"Игра окончена!\nСчёт: {self.score}",
            fill='white',
            font=('Arial', 24, 'bold'),
            justify='center'
        )
        
        # Закрываем окно через 3 секунды
        self.root.after(3000, self.on_close)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    def test_callback(score):
        print(f"Игра завершена! Счёт: {score}")
        root.destroy()
    
    game = Letters(root, test_callback)
    root.mainloop()