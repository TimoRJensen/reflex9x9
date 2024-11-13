# main.py

import reflex as rx
import random

# Konstanten definieren
GRID_SIZE = 9  # 9x9 Raster
SECTOR_SIZE = 3  # Größe der 3x3 Sektoren
FORM_SIZES = [1, 2, 3, 4, 5]  # Mögliche Größen der Formen


class BlockPuzzle(rx.Component):
    def __init__(self):
        super().__init__()
        # Spielzustand initialisieren
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.current_forms = self.generate_forms()
        self.selected_form = None
        self.game_over = False

    def generate_forms(self):
        forms = []
        for _ in range(3):
            size = random.choice(FORM_SIZES)
            form = self.create_random_form(size)
            forms.append(form)
        return forms

    def create_random_form(self, size):
        # Erstelle eine leere Matrix für die Form
        form = [[0 for _ in range(5)] for _ in range(5)]
        blocks = 0
        while blocks < size:
            x, y = random.randint(0, 4), random.randint(0, 4)
            if form[x][y] == 0:
                form[x][y] = 1
                blocks += 1
        return form

    def can_place_form(self, form, x, y):
        for i in range(5):
            for j in range(5):
                if form[i][j] == 1:
                    grid_x = x + i
                    grid_y = y + j
                    if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                        if self.grid[grid_x][grid_y] == 0:
                            continue
                        else:
                            return False
                    else:
                        return False
        return True

    def place_form(self, form, x, y):
        if not self.can_place_form(form, x, y):
            return False  # Platzierung nicht möglich
        # Platzierung durchführen
        for i in range(5):
            for j in range(5):
                if form[i][j] == 1:
                    self.grid[x + i][y + j] = 1
        self.check_lines()
        return True

    def check_lines(self):
        lines_cleared = 0
        # Reihen überprüfen
        rows_to_clear = []
        for i in range(GRID_SIZE):
            if all(self.grid[i][j] == 1 for j in range(GRID_SIZE)):
                rows_to_clear.append(i)
        for i in rows_to_clear:
            for j in range(GRID_SIZE):
                self.grid[i][j] = 0
            lines_cleared += 1

        # Spalten überprüfen
        cols_to_clear = []
        for j in range(GRID_SIZE):
            if all(self.grid[i][j] == 1 for i in range(GRID_SIZE)):
                cols_to_clear.append(j)
        for j in cols_to_clear:
            for i in range(GRID_SIZE):
                self.grid[i][j] = 0
            lines_cleared += 1

        # Sektoren überprüfen
        sectors_to_clear = []
        for x in range(0, GRID_SIZE, SECTOR_SIZE):
            for y in range(0, GRID_SIZE, SECTOR_SIZE):
                if all(
                    self.grid[i][j] == 1
                    for i in range(x, x + SECTOR_SIZE)
                    for j in range(y, y + SECTOR_SIZE)
                ):
                    sectors_to_clear.append((x, y))
        for x, y in sectors_to_clear:
            for i in range(x, x + SECTOR_SIZE):
                for j in range(y, y + SECTOR_SIZE):
                    self.grid[i][j] = 0
            lines_cleared += 1

        # Punktestand aktualisieren
        self.score += lines_cleared * 10

    def check_game_over(self):
        for form in self.current_forms:
            if self.can_place_form_anywhere(form):
                return False
        self.game_over = True
        return True

    def can_place_form_anywhere(self, form):
        for x in range(GRID_SIZE - 4):
            for y in range(GRID_SIZE - 4):
                if self.can_place_form(form, x, y):
                    return True
        return False

    def select_form(self, idx):
        if idx < len(self.current_forms):
            self.selected_form = self.current_forms[idx]

    def on_grid_click(self, i, j):
        if self.selected_form and not self.game_over:
            if self.place_form(self.selected_form, i - 2, j - 2):
                self.current_forms.remove(self.selected_form)
                self.selected_form = None
                if len(self.current_forms) == 0:
                    self.current_forms = self.generate_forms()
                if self.check_game_over():
                    print("Spiel beendet!")
            else:
                print("Platzierung nicht möglich!")

    def render(self):
        if self.game_over:
            return rx.center(
                rx.vstack(
                    rx.text("Spiel beendet!", font_size="2em", color="red"),
                    rx.text(f"Dein Punktestand: {self.score}", font_size="1.5em"),
                    rx.button(
                        "Neues Spiel", on_click=self.restart_game, margin_top="20px"
                    ),
                )
            )

        return rx.center(
            rx.vstack(
                rx.text(f"Punkte: {self.score}", font_size="1.5em"),
                self.render_grid(),
                rx.text("Wähle eine Form aus:", font_size="1.2em", margin_top="20px"),
                rx.hstack(
                    *[
                        self.render_form(form, idx)
                        for idx, form in enumerate(self.current_forms)
                    ]
                ),
            )
        )

    def render_grid(self):
        return rx.grid(
            *[
                self.render_cell(i, j)
                for i in range(GRID_SIZE)
                for j in range(GRID_SIZE)
            ],
            template_columns=f"repeat({GRID_SIZE}, 40px)",
            template_rows=f"repeat({GRID_SIZE}, 40px)",
            gap="2px",
            margin_top="20px",
        )

    def render_cell(self, i, j):
        color = "lightgray" if self.grid[i][j] == 0 else "blue"
        return rx.box(
            width="40px",
            height="40px",
            background_color=color,
            border="1px solid black",
            on_click=lambda i=i, j=j: self.on_grid_click(i, j),
        )

    def render_form(self, form, idx):
        border_color = "red" if self.selected_form == form else "black"
        return rx.box(
            rx.grid(
                *[
                    self.render_form_cell(form, i, j)
                    for i in range(5)
                    for j in range(5)
                ],
                template_columns="repeat(5, 20px)",
                template_rows="repeat(5, 20px)",
                gap="1px",
            ),
            border=f"2px solid {border_color}",
            padding="5px",
            margin="5px",
            on_click=lambda idx=idx: self.select_form(idx),
        )

    def render_form_cell(self, form, i, j):
        color = "lightgray" if form[i][j] == 0 else "green"
        return rx.box(
            width="20px",
            height="20px",
            background_color=color,
            border="1px solid black",
        )

    def restart_game(self):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.current_forms = self.generate_forms()
        self.selected_form = None
        self.game_over = False


# App initialisieren und ausführen
app = rx.App(BlockPuzzle)
app.run()
