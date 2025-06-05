import tkinter as tk
import random
import math
import time
from tkinter import messagebox

class DrawGame:
    def __init__(self, master):
        self.master = master
        master.title("Обведи, не отрывая пера")
        master.configure(bg="white")  # Устанавливаем белый фон для главного окна

        self.canvas_width = 400
        self.canvas_height = 300
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=0)  # Убираем рамку

        self.figure_types = ["square", "triangle","rectangle","pentagon","circle", "boat", "hexagon", "star","infinity","spiral"]
        self.level_figures = {}
        self.current_figure_index = 0
        self.current_level_figures = []
        self.points = []
        self.start_point = None
        self.current_point = 0
        self.drawing = False
        self.completed = False
        self.lines_drawn = []
        self.level = 1
        self.figures_completed = 0
        self.create_menu()
        self.level_window = None
        self.game_window = None
        self.level_label = None  # Добавляем атрибут для хранения метки уровня
        self.game_elements_created = False # Флаг для контроля создания элементов игры
        self.prev_level_button = None  # Добавляем атрибуты для кнопок
        self.next_level_button = None

        # Атрибуты таймера
        self.timer_running = False
        self.remaining_time = 8
        self.timer_id = None
        
        self.canvas.bind("<ButtonRelease-1>", self.reset_drawing)
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<Motion>", self.draw)

        self.load_level(self.level)
        self.new_figure()
        self.canvas.pack_forget()  

        self.create_main_menu()  
        
        self.center_window(master, 400, 400, vertikal_offset=-50)
        
        master.resizable(False, False)


    def create_main_menu(self):
        """Создает главное меню с кнопками: Играть, Правила, Уровни."""
        # Скрываем основное окно игры
        self.master.withdraw()

        # Создаем главное меню
        main_menu = tk.Toplevel(self.master)
        main_menu.title("Главное меню")
        main_menu.geometry("300x250")
        main_menu.configure(bg="white")  # Белый фон для главного меню

        # Заголовок окна
        label = tk.Label(main_menu, text="Добро пожаловать в игру!", font=("Arial", 14), bg="white")
        label.pack(pady=20)

        # Общие параметры для кнопок
        button_width = 22  # Увеличиваем ширину
        button_padx = 20
        button_pady = 10

        # Кнопка "Играть"
        btn_play = tk.Button(main_menu, text="Играть", width=button_width, command=lambda: self.start_game(), padx=button_padx, pady=button_pady)
        btn_play.pack(pady=5)

        # Кнопка "Правила"
        btn_rules = tk.Button(main_menu, text="Правила", width=button_width, command=self.show_rules, padx=button_padx, pady=button_pady)
        btn_rules.pack(pady=5)

        # Кнопка "Уровни"
        btn_levels = tk.Button(main_menu, text="Уровни", width=button_width, command=self.show_level_selection, padx=button_padx, pady=button_pady)
        btn_levels.pack(pady=5)

        self.main_menu = main_menu  # Сохраняем ссылку на главное меню
        
        # Центрируем окно с небольшим смещением по горизонтали
        self.center_window(main_menu, 300, 250, vertikal_offset=-50)
        
        main_menu.resizable(False, False)
        
        

    def create_menu(self):
        """Создает выпадающее меню с пунктами: выбор уровня и выход в главное меню."""
        menubar = tk.Menu(self.master)
        levelmenu = tk.Menu(menubar, tearoff=0)
        levelmenu.add_command(label="Выбрать уровень", command=self.show_level_selection)
        menubar.add_cascade(label="Уровни", menu=levelmenu)
        self.master.config(menu=menubar)
        
        exitmenu = tk.Menu(menubar, tearoff=0)
        exitmenu.add_command(label="Выйти в главное меню", command=self.return_to_main_menu)
        menubar.add_cascade(label="Выход", menu=exitmenu)

    def show_level_selection(self):
        """Открывает окно выбора уровня с миниатюрными изображениями фигур для каждого уровня."""
        # Если окно выбора уровня уже существует и не закрыто, то закрываем его,
        if self.level_window and self.level_window.winfo_exists():
            self.level_window.destroy()
        # Создаем окно с фоном
        self.level_window = tk.Toplevel(self.master)
        self.level_window.configure(bg="white")
        # Создаём контейнер Frame для каждого уровня, чтобы группировать
        # миниатюру, подпись и обрабатывать клики вместе.
        for level in range(1, 11):
            level_frame = tk.Frame(self.level_window, bg="white")
            level_frame.pack(padx=10, pady=5)
            level_canvas = tk.Canvas(level_frame, width=50, height=50, bg="white", highlightthickness=0)
            level_canvas.pack(side=tk.LEFT)
            level_label = tk.Label(level_frame, text=f"Уровень {level}", bg="white")
            level_label.pack(side=tk.LEFT)
            self.draw_level_preview(level_canvas, level)
            # При клике вызывается метод select_level с аргументом текущего уровня.
            level_frame.bind("<Button-1>", lambda event, lvl=level: self.select_level(lvl))
            level_canvas.bind("<Button-1>", lambda event, lvl=level: self.select_level(lvl))
            level_label.bind("<Button-1>", lambda event, lvl=level: self.select_level(lvl))
            
        self.center_window(self.level_window, 150, 600, vertikal_offset=-50, horizontal_offset=-300 )
        
        self.level_window.resizable(False, False)

    def draw_level_preview(self, canvas, level):
        """Рисует миниатюру фигуры соответствующего уровня."""
        if level <= len(self.figure_types):
            figure_type = self.figure_types[level - 1]
        else:
            figure_type = self.figure_types[-1]
        points = self.generate_preview_points(figure_type, level)
        canvas.create_polygon(points, width=1, outline="black", fill="")
        start_point = points[0]
        canvas.create_oval(start_point[0] - 2, start_point[1] - 2, start_point[0] + 2, start_point[1] + 2, fill="green")

    def generate_preview_points(self, ftype, level):
        """Генерирует координаты точек для отображения миниатюр фигур в окне выбора уровня."""
        if ftype == "square":
            points = [(5, 5), (45, 5), (45, 45), (5, 45), (5, 5)]
            return points
        elif ftype == "triangle":
            points = [(25, 5), (5, 40), (45, 40), (25, 5)]
            return points
        elif ftype == "rectangle":
            points = [(5, 10), (45, 10), (45, 40), (5, 40), (5, 10)]
            return points
        elif ftype == "hexagon":
            points = []
            center_x = 25
            center_y = 25
            radius = 20
            for i in range(6):
                angle = (i * 2 * math.pi / 6) - (math.pi / 2)
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                points.append((x, y))
            return points
        elif ftype == "star":
            num_points = 5
            center_x = 25
            center_y = 25
            inner_radius = 7
            outer_radius = 15
            points = []
            for i in range(2 * num_points):
                angle = math.pi * i / num_points
                radius = outer_radius if i % 2 == 0 else inner_radius
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                points.append((x, y))
            return points
        elif ftype == "spiral":
            points = []
            for i in range(30):
                angle = i * math.pi / 10
                radius = i / 3
                x = 25 + int(radius * math.cos(angle))
                y = 25 + int(radius * math.sin(angle))
                points.append((x, y))
            return points
        elif ftype == "circle":
            center_x = 25
            center_y = 25
            radius = 20
            points = []
            for i in range(30):
                angle = 2 * math.pi * i / 30
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                points.append((x, y))
            return points
        elif ftype == "infinity":
            points = []
            for i in range(20):
                angle = i * math.pi / 10
                x = 25 + 15 * math.cos(angle)
                y = 25 + 15 * math.sin(angle) * math.cos(angle)
                points.append((x, y))
            return points
        elif ftype == "pentagon":
            points = []
            center_x = 25
            center_y = 25
            radius = 20
            for i in range(5):
                angle = (i * 2 * math.pi / 5) - (math.pi / 2)
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                points.append((x, y))
            return points
        elif ftype == "boat":
            points = [(17, 18+10), (25, 0+10), (33, 18+10), (30, 22+16), (20, 22+16), (17, 18+10)]
            return points

    def load_level(self, level):
        """Загружает данные текущего уровня: тип фигуры и число сторон, и сохраняет их."""
        # Связываем уровни с конкретными фигурами вручную
        level_mapping = {
            1: "square",
            2: "triangle",
            3: "rectangle",
            4: "pentagon",
            5: "circle",
            6: "boat",
            7: "hexagon",
            8: "star",
            9: "infinity",
            10: "spiral",
        }

        figure_type = level_mapping.get(level, "square")  # По умолчанию "square"
        
        num_sides = 5 if figure_type == "star" else random.randint(3, 12) if figure_type in ["square", "triangle", "rectangle", "hexagon", "pentagon"] else 0

        self.level_figures[level] = {"type": figure_type, "num_sides": num_sides}
        self.current_level_figures = [self.level_figures[level]] * 10

    def new_figure(self, reset_timer=True):
        """Подготавливает и отображает новую фигуру для обведения.При необходимости сбрасывает таймер."""
        self.canvas.delete("all")
        if reset_timer and hasattr(self, "timer_label"):
            self.timer_label.config(text="Время: 8")
            self.drawing = False
        current_figure_data = self.current_level_figures[self.current_figure_index]
        self.figure_type = current_figure_data["type"]
        self.num_sides = current_figure_data["num_sides"] if current_figure_data["num_sides"] > 0 else 0
        self.points = self.generate_points()
        self.start_point = self.points[0]
        self.current_point = 0
        self.completed = False
        self.lines_drawn = []
        self.draw_figure()  # Рисует саму фигуру.
        self.draw_start_point()  # Отмечает начальную точку.
        self.draw_points()  # Отображает все точки фигуры.

    def generate_points(self):
        """Генерирует координаты точек фигуры в зависимости от ее типа для текущего уровня."""
        """Для каждой фигуры вычисляется координаты центра, задаем размер и координаты точек фигуры"""
        if self.figure_type == "square":
            #координаты центра
            center_x = self.canvas_width // 2
            center_y = self.canvas_height // 2
            #размер
            size = min(center_x, center_y) // 2 - 20
            #точки
            points = [(center_x - size, center_y - size),
                      (center_x + size, center_y - size),
                      (center_x + size, center_y + size),
                      (center_x - size, center_y + size),
                      (center_x - size, center_y - size)]
            return points
        elif self.figure_type == "triangle":
            center_x = self.canvas_width // 2
            center_y = self.canvas_height // 2
            size = min(center_x, center_y) // 2 - 20
            points = [(center_x, center_y - size),
                    (center_x - size, center_y + size),
                    (center_x + size, center_y + size),
                    (center_x, center_y - size)]
            return points
        elif self.figure_type == "rectangle":
            center_x = self.canvas_width // 2
            center_y = self.canvas_height // 2
            size_x = min(center_x, center_y) // 2 - 20
            size_y = min(center_x, center_y) // 3 - 20
            points = [(center_x - size_x, center_y - size_y),
                     (center_x + size_x, center_y - size_y),
                     (center_x + size_x, center_y + size_y),
                     (center_x - size_x, center_y + size_y),
                     (center_x - size_x, center_y - size_y)]
            return points
        elif self.figure_type == "hexagon":
            num_sides = 6
            center_x = self.canvas_width // 2
            center_y = self.canvas_height // 2
            radius = min(center_x, center_y) // 2 - 20
            points = []
            for i in range(num_sides):
                #Рассчитать угол поворота для каждой вершины многоугольника, чтобы они располагались равномерно по окружности.
                angle = (i * 2 * math.pi / num_sides) - (math.pi / 2) 
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                points.append((x, y))
            points.append(points[0])
            return points
        elif self.figure_type == "star":
            num_points = 5
            center_x = self.canvas_width // 2
            center_y = self.canvas_height // 2
            inner_radius = min(center_x, center_y) // 3 - 20
            outer_radius = min(center_x, center_y) // 2 - 20
            points = []
            for i in range(2 * num_points):
                angle = math.pi * i / num_points
                radius = outer_radius if i % 2 == 0 else inner_radius
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                points.append((x, y))
            points.append(points[0])
            return points
        elif self.figure_type == "spiral":
            points = []
            center_x = self.canvas_width // 2
            center_y = self.canvas_height // 2
            for i in range(100):
                angle = i * math.pi / 20
                radius = i / 4
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                points.append((x, y))
            points.append(points[0])
            return points
        elif self.figure_type == "circle":
            center_x = self.canvas_width // 2
            center_y = self.canvas_height // 2
            radius = min(center_x, center_y) // 2 - 20
            points = []
            for i in range(100):
                angle = 2 * math.pi * i / 100
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                points.append((x, y))
            points.append(points[0])
            return points
        elif self.figure_type == "infinity":
            points = []
            center_x = self.canvas_width // 2
            center_y = self.canvas_height // 2
            size = min(center_x, center_y) // 2 - 20
            for i in range(100):
                angle = i * math.pi / 50
                x = center_x + size * math.cos(angle)
                y = center_y + size * math.sin(angle) * math.cos(angle)
                points.append((x, y))
            points.append(points[0])
            return points
        elif self.figure_type == "pentagon":
            num_sides = 5
            center_x = self.canvas_width // 2
            center_y = self.canvas_height // 2
            radius = min(center_x, center_y) // 2 - 20
            points = []
            for i in range(num_sides):
                angle = (i * 2 * math.pi / num_sides) - (math.pi / 2)
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                points.append((x, y))
            points.append(points[0])
            return points
        elif self.figure_type == "boat":
            center_x = self.canvas_width // 2
            center_y = self.canvas_height // 2
            size = min(center_x, center_y) // 2 - 20
            points = [(center_x - size // 2, center_y + size // 2),
                      (center_x, center_y - size // 2),
                      (center_x + size // 2, center_y + size // 2),
                      (center_x + size // 3, center_y + size),
                      (center_x - size // 3, center_y + size),
                      (center_x - size // 2, center_y + size // 2)]
            points.append(points[0])
            return points

    def draw_figure(self):
        """Рисует фигуру на canvas, включая стрелку направления."""
        #рисует многоугольник, соединяя список точек по порядку линиями.
        self.canvas.create_polygon(self.points, width=2, outline="black", fill="")

        if len(self.points) > 1:
            x1, y1 = self.points[0]
            x2, y2 = self.points[1]

            # Вычисляем вектор направления
            dx = x2 - x1
            dy = y2 - y1
            length = (dx**2 + dy**2) ** 0.5  # Длина отрезка
            if length == 0:
                return  

            # Нормируем вектор
            dx /= length
            dy /= length

            if self.level == 2:  # Вычисляем перпендикулярный вектор (смещение вверх)
                offset = 20  # Насколько поднимаем стрелку
                perp_x = -dy * offset
                perp_y = dx * offset
            else:
                offset = -20  # Насколько поднимаем стрелку
                perp_x = -dy * offset
                perp_y = dx * offset

            # Новые координаты линии со стрелкой
            new_x1, new_y1 = x1 + perp_x, y1 + perp_y
            new_x2, new_y2 = x2 + perp_x, y2 + perp_y

            # Рисуем линию со стрелкой выше оригинальной линии
            self.canvas.create_line(new_x1, new_y1, new_x2, new_y2, width=1, fill="lightskyblue", arrow=tk.LAST)

    def draw_start_point(self):
        """Отображает начальную точку фигуры, с которой должно начинаться обведение."""
        x, y = self.start_point
        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="blue")

    def draw_points(self):
        """Рисует вспомогательные точки вдоль контура фигуры."""
        for x, y in self.points:
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="blue")

    def start_draw(self, event):
        """Обрабатывает начало рисования при клике мыши возле начальной точки фигуры.Запускает таймер."""
        # Проверяем расстояние от курсора до первой и последней точки
        distance_to_start = self.distance(event.x, event.y, self.start_point[0], self.start_point[1])
        

        # Если курсор близко к начальной точке, начинаем рисовать от нее
        if distance_to_start < 10:
            self.drawing = True
            self.last_x = event.x
            self.last_y = event.y
            self.current_point = 0
            self.start_time = time.time()
            if not self.timer_running:
                self.remaining_time = 8
                self.timer_running = True
                self.update_timer()

    def update_timer(self):
        """Обновляет таймер каждую секунду. При истечении времени завершает попытку."""
        if self.remaining_time > 0:
            self.timer_label.config(text=f"Время: {self.remaining_time}")
            self.remaining_time -= 1
            self.timer_id = self.master.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="Время: 0")
            self.timer_running = False
            if not self.completed:
                self.show_result_window(False)

    def draw(self, event):
        """Отслеживает движение мыши. Проверяет, проходит ли пользователь по контуру фигуры.Завершает попытку при успешном обведении или ошибке."""
        if self.drawing:
            if self.current_point < len(self.points):
                curr_x, curr_y = self.points[self.current_point] # Текущая целевая точка
                if self.current_point > 0:
                    prev_x, prev_y = self.points[self.current_point - 1] # Предыдущая точка
                else:
                    prev_x, prev_y = self.points[0]  # Если это первая точка, берём первую

                # Проверка расстояния от курсора до отрезка
                max_allowed_distance = 50  # отклонение от точек
                distance_to_segment = self.distance_to_segment((prev_x, prev_y), (curr_x, curr_y), (event.x, event.y))
                if distance_to_segment > max_allowed_distance: 
                    self.drawing = False
                    self.reset_drawing(event)
                    return

                # Если курсор рядом с нужной точкой, то соединяем линией
                if self.distance(event.x, event.y, curr_x, curr_y) < 10:
                    self.canvas.create_line(prev_x, prev_y, curr_x, curr_y, width=2, fill="red")
                    self.lines_drawn.append((prev_x, prev_y, curr_x, curr_y))
                    self.last_x = curr_x
                    self.last_y = curr_y
                    self.current_point += 1

            if self.current_point == len(self.points):
                self.completed = True
                if self.timer_running:
                    self.master.after_cancel(self.timer_id)
                    self.timer_running = False
                self.drawing = False
                self.figures_completed += 1
                # Подсчёт времени выполнения
                time_taken = time.time() - self.start_time if self.start_time is not None else 0
                self.show_result_window(True, time_taken)

                
    def distance_to_segment(self, p1, p2, p):
        """Вычисляет расстояние от точки до отрезка.Используется для определения, насколько близко пользователь к контуру."""
        x, y = p
        x1, y1 = p1
        x2, y2 = p2

        dx = x2 - x1
        dy = y2 - y1
        if dx == dy == 0:  # p1 и p2 совпадают
            return self.distance(x, y, x1, y1)

        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return self.distance(x, y, proj_x, proj_y)



    def next_figure(self):
        """Загружает следующую фигуру. Если завершены все фигуры — перезапускает уровень."""
        if self.figures_completed >= 10:
            self.figures_completed = 0
            self.current_figure_index = 0
            self.load_level(self.level)
        else:
            self.current_figure_index += 1
        self.new_figure()

    def distance(self, x1, y1, x2, y2):
        """Вычисляет расстояние между двумя точками."""
        return math.dist((x1, y1), (x2, y2))

    def set_level(self, level):
        """Устанавливает указанный уровень и сбрасывает параметры игры без сброса таймера."""
    
        self.level = level
        self.figures_completed = 0
        self.current_figure_index = 0
        self.load_level(level)

        
        if self.timer_running:
            self.master.after_cancel(self.timer_id)
            self.timer_running = False
        self.remaining_time = 8
        if hasattr(self, "timer_label"):
            self.timer_label.config(text="Время: 8")

        self.new_figure(reset_timer=False)  # Не трогаем таймер внутри
        self.update_level_label()
        self.update_navigation_buttons()

    def show_rules(self):
        """Показывает окно с правилами игры."""
        messagebox.showinfo("Правила", "Правила игры: \n\n1. Начните рисовать, нажав на большую точку. \n2. Следуйте направлению указанной стрелки. \n3. Успей обвести все фигуры, не отрывая пера.")

    def start_game(self):
        """Запускает игру, уничтожает главное меню и инициализирует игровой интерфейс."""
        # Уничтожаем главное меню
        if self.main_menu:
             self.main_menu.destroy()

        # Показываем canvas и начинаем игру
        self.master.deiconify()  # Показываем основное окно
        self.create_game_elements()  # создаем элементы управления только 1 раз
        self.canvas.pack()
        self.load_level(self.level)
        self.new_figure()
        self.update_navigation_buttons()

    def create_game_elements(self):
        """Создает элементы игрового интерфейса: метки, кнопки, таймер, canvas."""
        #Создаем элементы управления игрой
        if not self.game_elements_created:
            game_frame = tk.Frame(self.master, bg="white")
            game_frame.pack(pady=10, padx=10)
            # Метка уровня: показывает текущий уровень игры
            self.level_label = tk.Label(game_frame, text=f"Уровень: {self.level}", font=("Arial", 12), bg="white")
            self.level_label.pack(pady=5)
            #Отдельный фрейм для размещения кнопок Предыдущий уровень и Следующий уровень
            button_frame = tk.Frame(game_frame, bg="white")
            button_frame.pack(pady=5)

            self.prev_level_button = tk.Button(button_frame, text="Предыдущий уровень", command=self.prev_level)
            self.next_level_button = tk.Button(button_frame, text="Следующий уровень", command=self.next_level)

            self.timer_label = tk.Label(game_frame, text="Время: 8", font=("Arial", 14), bg="white")
            self.timer_label.pack(pady=(10, 0))

            #canvas уже создан, нужно только изменить его master
            self.canvas.master = game_frame
            self.canvas.configure(bg="white", highlightthickness=0)  # Белый фон и убираем обводку
            self.canvas.pack(pady=5)

            self.game_elements_created = True  # Устанавливаем флаг в True

        self.update_navigation_buttons()  # Обновляем кнопки после создания элементов

    def update_navigation_buttons(self):
        """Обновляет состояние кнопок перехода между уровнями в зависимости от текущего уровня."""
        # Обновляем видимость кнопок
        if self.level == 1:
            if self.prev_level_button:
                 self.prev_level_button.pack_forget()
            if self.next_level_button and self.level < 10:
                 self.next_level_button.pack(side=tk.RIGHT, padx=5)
        elif self.level == 10:
            if self.next_level_button:
                self.next_level_button.pack_forget()
            if self.prev_level_button and self.level > 1:
                self.prev_level_button.pack(side=tk.LEFT, padx=5)
        else:
            if self.prev_level_button:
                self.prev_level_button.pack(side=tk.LEFT, padx=5)
            if self.next_level_button:
                self.next_level_button.pack(side=tk.RIGHT, padx=5)

        self.update_level_label()  # Обновляем метку уровня при переключении

    def select_level(self, level):
        """Выбирает указанный уровень из окна выбора и запускает игру."""
        self.level = level
        self.start_game()
        if self.level_window:
            self.level_window.destroy()

    def prev_level(self):
        """Переходит к предыдущему уровню."""
        if self.level > 1:
            self.set_level(self.level - 1)

    def next_level(self):
        """Переходит к следующему уровню."""
        if self.level < 10:
            self.set_level(self.level + 1)

    def update_level_label(self):
        """Обновляет текст метки с номером текущего уровня."""
        if self.level_label:
            self.level_label.config(text=f"Уровень: {self.level}")

    def center_window(self, window, width, height, horizontal_offset=0, vertikal_offset=0):
        """Центрирует окно на экране с возможным смещением."""
        # Получаем размеры экрана
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Вычисляем координаты для центрирования окна
        x = (screen_width - width) // 2 + horizontal_offset
        y = (screen_height - height) // 2 + vertikal_offset

        # Устанавливаем геометрию окна
        window.geometry(f"{width}x{height}+{x}+{y}")

    def reset_drawing(self, event):
        """Сбрасывает текущее рисование. Перерисовывает фигуру без сброса таймера."""
        # При отпускании ЛКМ больше не отменяем таймер и не сбрасываем фигуру
        self.drawing = False
        self.new_figure(reset_timer=False)

    def return_to_main_menu(self):
        """Возвращает пользователя в главное меню, скрывая игровое окно."""
        self.master.withdraw()  # Скрываем игровое окно
        self.create_main_menu()  # Показываем главное меню

    # Новый метод для показа окна результата с кнопками "Заново" и "Следующий"
    def show_result_window(self, victory, time_taken=None):
        """Показывает окно результата после завершения попытки с вариантами продолжения."""
        result_window = tk.Toplevel(self.master)
        result_window.title("Результат")
        result_window.configure(bg="white")
        self.center_window(result_window, 450, 250)
        if victory:
            message_text = "Молодец, вы можете попробовать пройти этот уровень быстрее или перейти на следующий."
            # Добавляем информацию о времени, затраченном на обведение фигуры
            if time_taken is not None:
                message_text += f"\n\nВремя: {time_taken:.2f} секунд."
        else:
            message_text = "Увы, время закончилось. Вы можете попробовать пройти этот уровень еще раз или перейти на следующий."
            
        label = tk.Label(result_window, text=message_text, bg="white", wraplength=400, font=("Arial", 16))
        label.pack(pady=20)
        
        btn_frame = tk.Frame(result_window, bg="white")
        btn_frame.pack(pady=10)
        
        btn_again = tk.Button(btn_frame, text="Заново", command=lambda: self.restart_level(result_window), width=12, font=("Arial", 12))
        btn_next = tk.Button(btn_frame, text="Следующий", command=lambda: self.go_next_level(result_window), width=12, font=("Arial", 12))
        btn_again.pack(side=tk.LEFT, padx=10)
        btn_next.pack(side=tk.RIGHT, padx=10)
        
        result_window.resizable(False, False)

    def restart_level(self, window):
        """Закрывает окно результата и перезапускает текущую фигуру."""
        window.destroy()
        self.new_figure()

    def go_next_level(self, window):
        """Закрывает окно результата и переходит к следующему уровню."""
        window.destroy()
        self.next_level()
        
root = tk.Tk()
root.configure(bg="white")  # Устанавливаем белый фон для главного окна
game = DrawGame(root)
root.mainloop()