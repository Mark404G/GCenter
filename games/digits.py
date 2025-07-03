import tkinter as tk
import random
import time

class Digits:
    def __init__(self, parent_window, callback=None):
        """
        Игра Digits с цифрами, оптимизированная для интеграции с Game Center.
        """
        self.parent_window = parent_window  # Ссылка на главное окно
        self.callback = callback           # Функция для возврата результата
        
        # ========== НАСТРОЙКИ ИГРЫ ==========
        self.WIDTH = 800                   # Ширина игрового поля
        self.HEIGHT = 600                  # Высота игрового поля
        self.LINE_Y = 500                  # Y-координата линии поражения
        self.BG_COLOR = 'black'            # Цвет фона
        
        # Настройки цифр
        self.DIGIT_RADIUS = 28             # Радиус круга с цифрой
        self.DIGIT_FONT = ('Arial', 22, 'bold')  # Шрифт цифр
        self.REAL_COLOR = '#4682B4'        # Цвет настоящих цифр
        self.FAKE_COLOR = '#FF6347'        # Цвет фальшивых цифр
        self.FAKE_CHANCE = 0.10            # Вероятность фальшивой цифры
        
        # Настройки скорости
        self.BASE_SPEED = 1.00             # Начальная скорость падения
        self.SPEED_INCREASE = 0.05         # Увеличение скорости за попадание
        self.MAX_SPEED = 6.00              # Максимальная скорость
        
        # Настройки появления цифр
        self.MIN_SPAWN_DELAY = 700         # Минимальная задержка (мс)
        self.MAX_SPAWN_DELAY = 2000        # Максимальная задержка (мс)
        self.SPAWN_ACCEL = 0.98            # Коэф. ускорения появления цифр
        self.TARGET_DIGITS = 6             # Целевое количество цифр
        
        # Настройки анимации
        self.HIT_ANIM_DURATION = 30        # Длительность анимации попадания
        self.HIT_ANIM_SPEED = 2            # Скорость анимации попадания
        self.REAL_HIT_COLOR = '#7CFC00'    # Цвет анимации для настоящих цифр
        self.FAKE_HIT_COLOR = '#FFA500'    # Цвет анимации для фальшивых
        
        # ========== ИГРОВЫЕ ПЕРЕМЕННЫЕ ==========
        self.score = 0                      # Текущий счет
        self.current_speed = self.BASE_SPEED
        self.spawn_delay = self.MAX_SPAWN_DELAY
        self.game_active = False
        self.digits = []                   # Список активных цифр
        self.animations = []               # Список активных анимаций
        self.active_digits = set()         # Множество цифр на экране
        
        # ========== СОЗДАНИЕ ИНТЕРФЕЙСА ==========
        self.root = tk.Toplevel(parent_window)
        self.root.title("Digits")
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
        self.active_digits = set()
        
        # Обновляем интерфейс
        self.canvas.itemconfig(self.instruction, state='hidden')
        self.update_score()
        
        # Запускаем игровые процессы
        self.spawn_digit()
        self.fall_digits()

    def clear_canvas(self):
        """Очищает холст от всех объектов кроме статичных элементов"""
        for item in self.canvas.find_all():
            if item not in [self.score_text, self.speed_text, self.instruction]:
                self.canvas.delete(item)
        
        self.digits = []
        self.animations = []
        self.active_digits = set()
        
        # Восстанавливаем линию
        self.canvas.create_line(0, self.LINE_Y, self.WIDTH, self.LINE_Y, 
                              fill='red', width=1)

    def spawn_digit(self):
        """Создает новую падающую цифру"""
        if not self.game_active:
            return
            
        # Выбираем случайную цифру (0-9)
        digit = str(random.randint(0, 9))
        
        # Проверяем, нет ли уже такой цифры на экране
        while digit in self.active_digits:
            digit = str(random.randint(0, 9))
            
        self.active_digits.add(digit)
        
        # Определяем тип цифры (10% chance для фальшивой)
        is_fake = random.random() < self.FAKE_CHANCE
        
        # Случайная позиция по X
        x = random.randint(self.DIGIT_RADIUS, self.WIDTH-self.DIGIT_RADIUS)
        
        # Создаем графические элементы
        circle_id = self.canvas.create_oval(
            x-self.DIGIT_RADIUS, -self.DIGIT_RADIUS*2,
            x+self.DIGIT_RADIUS, 0,
            fill=self.FAKE_COLOR if is_fake else self.REAL_COLOR,
            outline='white',
            width=2
        )
        
        text_id = self.canvas.create_text(
            x, -self.DIGIT_RADIUS,
            text=digit, 
            fill='white', 
            font=self.DIGIT_FONT
        )
        
        # Добавляем цифру в список активных
        self.digits.append({
            'circle': circle_id,
            'text': text_id,
            'digit': digit,
            'x': x,
            'y': -self.DIGIT_RADIUS,
            'speed': self.current_speed,
            'hit': False,
            'fake': is_fake,
            'spawn_time': time.time()
        })
        
        # Регулируем скорость спавна
        digits_count = len(self.digits)
        if digits_count < self.TARGET_DIGITS:
            self.spawn_delay = max(self.MIN_SPAWN_DELAY, self.spawn_delay * self.SPAWN_ACCEL)
        else:
            self.spawn_delay = min(self.MAX_SPAWN_DELAY, self.spawn_delay / self.SPAWN_ACCEL)
        
        # Планируем следующую цифру
        self.root.after(int(self.spawn_delay), self.spawn_digit)

    def fall_digits(self):
        """Обновляет позиции всех падающих цифр"""
        if not self.game_active:
            return
            
        for digit in self.digits[:]:
            # Увеличиваем скорость со временем
            time_alive = time.time() - digit['spawn_time']
            speed_mult = 1.0 + min(4.0, (time_alive / 8.0) ** 1.5)
            digit['y'] += digit['speed'] * speed_mult
            
            # Обновляем позицию
            self.canvas.coords(
                digit['circle'],
                digit['x']-self.DIGIT_RADIUS, digit['y']-self.DIGIT_RADIUS,
                digit['x']+self.DIGIT_RADIUS, digit['y']+self.DIGIT_RADIUS
            )
            self.canvas.coords(digit['text'], digit['x'], digit['y'])
            
            # Проверка достижения линии
            if digit['y'] - self.DIGIT_RADIUS > self.LINE_Y and not digit['hit']:
                if digit['fake']:
                    # Фальшивая цифра прошла линию — +1 очко
                    self.score += 1
                    self.update_score()
                    self.show_hit_animation(digit['x'], digit['y'], is_fake=True)
                else:
                    # Настоящая цифра прошла линию — проигрыш
                    self.game_over()
                    return
                
                self.remove_digit(digit)
        
        # Обновляем скорость в интерфейсе
        self.canvas.itemconfig(self.speed_text, text=f"Скорость: {self.current_speed:.2f}x")
        
        # Следующий кадр
        self.animations.append(self.root.after(16, self.fall_digits))

    def handle_key_press(self, event):
        """Обрабатывает нажатия цифровых клавиш"""
        if event.keysym == 'Return':
            self.start_game()
            return
            
        if not self.game_active:
            return
            
        # Получаем нажатую цифру
        key = event.char if event.char else ''
        
        # Игнорируем не-цифры
        if not key.isdigit():
            return
            
        hit_any = False
        
        # Проверяем все цифры на экране
        for digit in self.digits[:]:
            if digit['digit'] == key and not digit['hit']:
                if digit['fake']:
                    # Нажали фальшивую — проигрыш
                    self.game_over()
                    return
                else:
                    # Нажали настоящую — +1 очко
                    digit['hit'] = True
                    hit_any = True
                    self.score += 1
                    self.update_score()
                    self.show_hit_animation(digit['x'], digit['y'])
                    self.current_speed = min(self.MAX_SPEED, self.current_speed + self.SPEED_INCREASE)
        
        if hit_any:
            for digit in self.digits[:]:
                if digit['hit']:
                    self.remove_digit(digit)

    def remove_digit(self, digit):
        """Удаляет цифру с экрана"""
        self.canvas.delete(digit['circle'])
        self.canvas.delete(digit['text'])
        self.digits.remove(digit)
        self.active_digits.discard(digit['digit'])

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
    
    game = Digits(root, test_callback)
    root.mainloop()