import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import os
from datetime import datetime

class GameCenter:
    def __init__(self, root):
        """Инициализация игрового центра"""
        self.root = root
        self.root.title("GCenter")
        self.root.geometry("600x650")
        
        # Константы для расчета рейтинга
        self.RATING_PER_GAME = 1.25  # Максимальный рейтинг за одну игру (1.25 для 4 игр)
        self.GAME_NAMES = ["snake", "balls", "letters", "digits"]  # Список игр
        
        # Загружаем иконку
        try:
            self.root.iconbitmap("GC.ico")  # Для Windows
        except:
            try:
                icon = tk.PhotoImage(file="GC.ico")
                self.root.iconphoto(False, icon)
            except:
                pass  # Если иконка вообще не найдена, оставляем стандартную
            
        # Инициализация данных
        self.current_user = None  # Текущий авторизованный пользователь
        self.data_dir = "data"  # Папка для хранения данных
        self.accounts_dir = os.path.join(self.data_dir, "accounts")  # Папка с аккаунтами
        self.logs_file = os.path.join(self.data_dir, "logs.json")  # Файл с логами игр
        os.makedirs(self.accounts_dir, exist_ok=True)  # Создаем директории, если их нет
        
        # Инициализация логов
        self.game_logs = []  # Список для хранения истории игр
        self.load_logs()  # Загружаем логи из файла
        
        # Создание интерфейса авторизации
        self.create_auth_interface()

    def load_logs(self):
        """Загрузка истории игр из файла"""
        try:
            if os.path.exists(self.logs_file):
                with open(self.logs_file, 'r', encoding='utf-8') as f:
                    self.game_logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.game_logs = []

    def create_auth_interface(self):
        """Создание интерфейса авторизации"""
        self.clear_window()
        
        auth_frame = tk.Frame(self.root)
        auth_frame.pack(pady=100, padx=50, fill=tk.BOTH, expand=True)
        
        tk.Label(
            auth_frame, 
            text="Привет🖐️\nЧтобы продолжить, необходимо авторизоваться",
            font=('Arial', 14)
        ).pack(pady=150)
        
        btn_frame = tk.Frame(auth_frame)
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame, 
            text="👤 Войти", 
            command=self.login_user,
            width=15,
            height=2,
            font=('Arial', 12)
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame, 
            text="✨ Регистрация", 
            command=self.create_user,
            width=15,
            height=2,
            font=('Arial', 12)
        ).pack(side=tk.LEFT, padx=10)

    def create_main_interface(self):
        """Создание основного интерфейса"""
        self.clear_window()
        
        # Основные фреймы
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.middle_frame = tk.Frame(self.root)
        self.middle_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(pady=10, fill=tk.X)
        
        # Таблица лидеров
        tk.Label(self.top_frame, text="🏆 Топ игроков", font=('Arial', 14, 'bold')).pack()
        
        self.top_tree = ttk.Treeview(self.top_frame, height=6)
        self.top_tree['columns'] = ('Rating', 'Snake', 'Balls', 'Letters', 'Digits')
        self.top_tree.column('#0', width=100, anchor='w')
        self.top_tree.column('Rating', width=80, anchor='center')
        self.top_tree.column('Snake', width=80, anchor='center')
        self.top_tree.column('Balls', width=80, anchor='center')
        self.top_tree.column('Letters', width=80, anchor='center')
        self.top_tree.column('Digits', width=80, anchor='center')
        
        self.top_tree.heading('#0', text='Игрок')
        self.top_tree.heading('Rating', text='Рейтинг')
        self.top_tree.heading('Snake', text='Snake')
        self.top_tree.heading('Balls', text='Balls')
        self.top_tree.heading('Letters', text='Letters')
        self.top_tree.heading('Digits', text='Digits')
        
        self.top_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # История игр с прокруткой
        logs_frame = tk.Frame(self.middle_frame)
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(logs_frame, text="🕒 История игр", font=('Arial', 12)).pack()
        
        # Создаем Scrollbar и Text для логов
        scrollbar = tk.Scrollbar(logs_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.logs_text = tk.Text(
            logs_frame, 
            height=10, 
            state='disabled', 
            font=('Arial', 10),
            yscrollcommand=scrollbar.set
        )
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar.config(command=self.logs_text.yview)
        
        # Информация о пользователе
        self.user_frame = tk.Frame(self.bottom_frame)
        self.user_frame.pack(pady=5)
        self.user_label = tk.Label(self.user_frame, text=f"Пользователь: {self.current_user}", font=('Arial', 12))
        self.user_label.pack()
        
        # Кнопки игр
        self.games_frame = tk.Frame(self.bottom_frame)
        self.games_frame.pack()
        
        games = [
            ("Snake", "snake"),
            ("Balls", "balls"),
            ("Letters", "letters"),
            ("Digits", "digits")
        ]
        
        for name, game_id in games:
            btn = tk.Button(
                self.games_frame, 
                text=name, 
                command=lambda g=game_id: self.start_game(g),
                width=12, 
                height=2
            )
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Кнопка выхода
        tk.Button(
            self.bottom_frame,
            text="Выйти",
            command=self.logout,
            width=12,
            height=2
        ).pack(pady=10)
        
        # Обновление данных
        self.update_logs_display()
        self.update_top_players()

    def start_game(self, game_name):
        """Запуск выбранной игры"""
        if not self.current_user:
            messagebox.showerror("Ошибка", "Сначала войдите в аккаунт")
            return
        
        # Создаем новое окно для игры
        game_window = tk.Toplevel(self.root)
        game_window.protocol("WM_DELETE_WINDOW", lambda: self.on_game_close(game_window))

        # Создаем иконку для отдельных окон с играми
        try:
            game_window.iconbitmap("GameCenter.ico")  # Для Windows
        except:
            try:
                icon = tk.PhotoImage(file="GameCenter.ico")
                game_window.iconphoto(False, icon)
            except:
                pass
        
        def universal_callback(score):
            """Универсальный обработчик завершения игры"""
            if score is not None:
                self.update_score(game_name, score)
                self.update_top_players()
                self.add_game_log(game_name, score)
            
            # Задержка перед закрытием
            game_window.after(100, lambda: self.final_close(game_window))
        
        # Сворачиваем главное окно
        self.root.iconify()
        
        try:
            if game_name == "snake":
                from games.snake import Snake
                Snake(game_window, universal_callback)
                
            elif game_name == "balls":
                from games.balls import Balls
                Balls(game_window, universal_callback)
                
            elif game_name == "letters":
                from games.letters import Letters
                Letters(game_window, universal_callback)
                
            elif game_name == "digits":
                from games.digits import Digits
                Digits(game_window, universal_callback)
                
        except ImportError as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить игру: {e}")
            self.root.deiconify()

    def final_close(self, game_window):
        """Финальное закрытие игры"""
        if game_window.winfo_exists():
            game_window.destroy()
        self.root.deiconify()

    def on_game_close(self, game_window):
        """Обработчик закрытия окна игры"""
        self.final_close(game_window)

    def add_game_log(self, game_name, score):
        """Добавление записи в историю игр"""
        log_entry = {
            "date": datetime.now().strftime("%d.%m.%Y %H:%M:%S"), 
            "player": self.current_user,
            "game": game_name.capitalize(),
            "score": score
        }
        self.game_logs.append(log_entry)
        self.save_logs()
        self.update_logs_display()

    def save_logs(self):
        """Сохранение истории игр"""
        try:
            with open(self.logs_file, 'w', encoding='utf-8') as f:
                json.dump(self.game_logs[-100:], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения логов: {e}")

    def update_logs_display(self):
        """Обновление отображения истории игр с прокруткой"""
        self.logs_text.config(state='normal')
        self.logs_text.delete(1.0, tk.END)
        
        try:
            # Сортируем логи по полной дате (с годом)
            sorted_logs = sorted(
                self.game_logs,
                key=lambda x: datetime.strptime(x['date'], "%d.%m.%Y %H:%M:%S"),
                reverse=True
            )
            
            # Отображаем без года (как было раньше)
            for log in sorted_logs:
                # Извлекаем только день, месяц и время для отображения
                self.logs_text.insert(
                    tk.END,
                    f"{log['date']} ({log.get('player', 'unknown')}) "
                    f"{log.get('game', 'Unknown')}: {log.get('score', '?')}\n"
                )
                
        except (KeyError, ValueError) as e:
            print(f"Ошибка при обработке логов: {e}")
            # Фолбэк: отображаем как есть, если возникли проблемы с датами
            for log in reversed(self.game_logs[-20:]):  # Последние 20 записей
                self.logs_text.insert(
                    tk.END,
                    f"{log.get('date', '??.?? ??:??:??')} ({log.get('player', 'unknown')}) "
                    f"{log.get('game', 'Unknown')}: {log.get('score', '?')}\n"
                )
        
        self.logs_text.config(state='disabled')
        self.logs_text.yview_moveto(0)  # Прокрутка к началу

    def calculate_player_ratings(self):
        """Рассчитывает рейтинги игроков для всех игр"""
        # Собираем данные обо всех игроках
        players_data = {}
        for filename in os.listdir(self.accounts_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.accounts_dir, filename), 'r', encoding='utf-8') as f:
                    account = json.load(f)
                    username = account["username"]
                    games_data = account["games"]
                    
                    players_data[username] = {
                        "scores": {
                            "snake": games_data["snake"]["high_score"],
                            "balls": games_data["balls"]["high_score"],
                            "letters": games_data["letters"]["high_score"],
                            "digits": games_data["digits"]["high_score"]
                        }
                    }
        
        # Если нет игроков, возвращаем пустой словарь
        if not players_data:
            return {}
        
        # Для каждой игры рассчитываем позиции игроков и распределяем рейтинг
        for game in self.GAME_NAMES:
            # Собираем всех игроков, которые играли в эту игру (даже с 0 очками)
            game_scores = [(player, data["scores"][game]) for player, data in players_data.items()]
            
            # Сортируем по убыванию очков
            sorted_scores = sorted(game_scores, key=lambda x: (-x[1], x[0]))
            
            # Количество игроков в этой игре
            num_players = len(sorted_scores)
            
            # Распределяем рейтинг
            for i, (player, score) in enumerate(sorted_scores):
                if num_players == 1:
                    # Если игрок один, он получает максимальный рейтинг
                    rating = self.RATING_PER_GAME
                else:
                    # Линейное распределение рейтинга от max до 0
                    rating = self.RATING_PER_GAME * (1 - i / (num_players - 1))
                
                # Добавляем рейтинг в данные игрока
                if "ratings" not in players_data[player]:
                    players_data[player]["ratings"] = {}
                players_data[player]["ratings"][game] = rating
        
        # Рассчитываем общий рейтинг для каждого игрока
        for player, data in players_data.items():
            total_rating = sum(data.get("ratings", {}).values())
            players_data[player]["total_rating"] = total_rating
        
        return players_data

    def update_top_players(self):
        """Обновление таблицы лидеров с новой системой рейтинга"""
        for item in self.top_tree.get_children():
            self.top_tree.delete(item)
        
        # Получаем данные с рассчитанными рейтингами
        players_data = self.calculate_player_ratings()
        
        # Сортируем игроков по общему рейтингу (по убыванию)
        sorted_players = sorted(players_data.items(),
                              key=lambda x: -x[1]['total_rating'])
        
        # Добавляем игроков в таблицу
        for player, data in sorted_players[:10]:  # Только топ-10
            scores = data['scores']
            self.top_tree.insert('', 'end', text=player, values=(
                f"{data['total_rating']:.2f}",  # Рейтинг с округлением до сотых
                scores["snake"],
                scores["balls"],
                scores["letters"],
                scores["digits"]
            ))

    def clear_window(self):
        """Очистка окна"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def logout(self):
        """Выход из аккаунта"""
        self.current_user = None
        self.create_auth_interface()

    def login_user(self):
        """Авторизация пользователя"""
        user = simpledialog.askstring("Вход", "Введите имя пользователя:", parent=self.root)
        
        if user and os.path.exists(os.path.join(self.accounts_dir, f"{user}.json")):
            self.current_user = user
            self.create_main_interface()
        else:
            messagebox.showerror("Ошибка", "Неверное имя пользователя")

    def create_user(self):
        """Регистрация нового пользователя"""
        user = simpledialog.askstring("Регистрация", "Придумайте имя пользователя:", parent=self.root)
        
        if not user:
            return
            
        if os.path.exists(os.path.join(self.accounts_dir, f"{user}.json")):
            messagebox.showerror("Ошибка", "Имя пользователя уже занято")
            return
            
        account = {
            "username": user,
            "games": {
                "snake": {"high_score": 0, "last_score": 0},
                "balls": {"high_score": 0, "last_score": 0},
                "letters": {"high_score": 0, "last_score": 0},
                "digits": {"high_score": 0, "last_score": 0}
            }
        }
        
        with open(os.path.join(self.accounts_dir, f"{user}.json"), 'w', encoding='utf-8') as f:
            json.dump(account, f, ensure_ascii=False, indent=4)
            
        self.current_user = user
        messagebox.showinfo("Успех", "Регистрация прошла успешно!")
        self.create_main_interface()

    def update_score(self, game_name, new_score):
        """Обновление результатов игрока"""
        if not self.current_user:
            return
            
        account_path = os.path.join(self.accounts_dir, f"{self.current_user}.json")
        
        with open(account_path, 'r', encoding='utf-8') as f:
            account = json.load(f)
        
        game_stats = account["games"][game_name]
        
        if new_score > game_stats["high_score"]:
            game_stats["high_score"] = new_score
        game_stats["last_score"] = new_score
        
        with open(account_path, 'w', encoding='utf-8') as f:
            json.dump(account, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = GameCenter(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Программа завершена из-за ошибки: {str(e)}")
        root.destroy()