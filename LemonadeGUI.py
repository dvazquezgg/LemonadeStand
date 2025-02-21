import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from PIL import Image, ImageTk
import random
from LemonadeStand import Player, Game

# Weather Images Mapping
weather_images = {
    "Sunny": "sunny.png",
    "Cloudy": "cloudy.png",
    "Rainy": "rainy.png",
    "Stormy": "stormy.png",
    "Windy": "windy.png"
}

# Sample Data for the Table
lemonade_data = [
                    ["Alice", 5, 2, "$2.50", 10],
                    ["Bob", 8, 3, "$3.00", 15],
                    ["Charlie", 10, 4, "$3.50", 20]
                ] + [["", "", "", "", ""] for _ in range(17)]

MAIN_TITLE_SIZE = 24
PRICES_TITLE_SIZE = 20
PRICES_LABEL_SIZE = 20
TABLE_HEADER_SIZE = 20
TABLE_CONTENT_SIZE = 20

class LemonadeStandApp:
    def __init__(self, root, Game):
        self.game = Game
        self.day = 0
        self.root = root
        self.root.title("Lemonade Stand")
        self.root.geometry("1280x800")  # 1280 pixels wide, 800 pixels tall
        self.root.configure(bg="#FFFACD")  # Lemon Yellow Background

        # Title Label
        self.title_label = tk.Label(root, text="Lemonade Stand", font=("Arial", MAIN_TITLE_SIZE, "bold"), bg="#FFFACD", fg="#32CD32")  # Lemon Green Text
        self.title_label.grid(row=0, column=0, columnspan=1, pady=10)

        # Weather Frame
        self.weather_frame = tk.Frame(root, bg="#FFFACD")
        self.weather_frame.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.weather_label = tk.Label(self.weather_frame, text="Weather:", font=("Arial", PRICES_TITLE_SIZE, "bold"), bg="#FFFACD", fg="#32CD32")
        self.weather_label.pack()

        #self.weather = random.choice(list(weather_images.keys()))
        self.weather = self.game.get_random_weather()
        self.weather_image = Image.open(weather_images[self.weather[0]])
        self.weather_image = self.weather_image.resize((100, 100), Image.LANCZOS)
        self.weather_photo = ImageTk.PhotoImage(self.weather_image)

        self.weather_display = tk.Label(self.weather_frame, image=self.weather_photo, bg="#FFFACD")
        self.weather_display.pack()

        # Ingredient Prices Table
        self.prices_frame = tk.Frame(root, bg="#FFFACD")
        self.prices_frame.grid(row=1, column=1, columnspan=1, pady=10, sticky="ew")

        self.prices_label = tk.Label(self.prices_frame, text=f"Day {self.day}", font=("Arial", PRICES_TITLE_SIZE, "bold"), bg="#FFFACD", fg="#32CD32")
        self.prices_label.grid(row=0, column=0, columnspan=3)

        self.prices_label = tk.Label(self.prices_frame, text="Ingredient Prices", font=("Arial", PRICES_TITLE_SIZE, "bold"), bg="#FFFACD", fg="#32CD32")
        self.prices_label.grid(row=0, column=0, columnspan=3)

        self.sugar_label = tk.Label(self.prices_frame, text="Sugar Price (tbsp):", bg="#FFFACD", fg="#32CD32", font=("Arial", PRICES_LABEL_SIZE))
        self.sugar_label.grid(row=1, column=0)
        self.sugar_price = tk.Label(self.prices_frame, text="$0.00", bg="#FFFACD", fg="#32CD32", font=("Arial", PRICES_LABEL_SIZE))
        self.sugar_price.grid(row=1, column=1, columnspan=2)

        self.lemons_label = tk.Label(self.prices_frame, text="Lemons Price (pc):", bg="#FFFACD", fg="#32CD32", font=("Arial", PRICES_LABEL_SIZE))
        self.lemons_label.grid(row=2, column=0)
        self.lemons_price = tk.Label(self.prices_frame, text="$0.00", bg="#FFFACD", fg="#32CD32", font=("Arial", PRICES_LABEL_SIZE))
        self.lemons_price.grid(row=2, column=1, columnspan=2)

        self.cups_label = tk.Label(self.prices_frame, text="Cups Price (pc):", bg="#FFFACD", fg="#32CD32", font=("Arial", PRICES_LABEL_SIZE))
        self.cups_label.grid(row=3, column=0)
        self.cups_price = tk.Label(self.prices_frame, text="$0.00", bg="#FFFACD", fg="#32CD32", font=("Arial", PRICES_LABEL_SIZE))
        self.cups_price.grid(row=3, column=1, columnspan=2)

        self.update_prices()

        # Lemonade Stand Table
        # Create a style
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", TABLE_CONTENT_SIZE))  # Adjusts the font for table content
        style.configure("Treeview.Heading", font=("Arial", TABLE_HEADER_SIZE, "bold"))  # Adjusts the font for headers

        self.tree = ttk.Treeview(root, columns=("Name", "Money","Lemons", "Sugar", "Price", "Lemonades"), show="headings",
                                 height=24)

        for col in ["Name", "Money", "Lemons", "Sugar", "Price", "Lemonades"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        self.set_table_data()

        self.tree.grid(row=2, column=0, columnspan=6, pady=10, sticky="nsew")

        # Buttons
        self.buttons_frame = tk.Frame(root, bg="#FFFACD")
        self.buttons_frame.grid(row=3, column=0, columnspan=5, pady=10)

        self.change_button = tk.Button(self.buttons_frame, text="Set Recipe", command=self.open_recipe_window, bg="#32CD32",
                                       fg="black")
        self.change_button.pack(side="left", padx=5)

        self.change_button = tk.Button(self.buttons_frame, text="Make Lemonades", command=self.open_making_window, bg="#32CD32",
                                       fg="black")
        self.change_button.pack(side="left", padx=5)

        self.next_button = tk.Button(self.buttons_frame, text="Next Day", command=self.next_day, bg="#32CD32", fg="black")
        self.next_button.pack(side="left", padx=5)

        self.restart_button = tk.Button(self.buttons_frame, text="Restart", command=self.restart, bg="#32CD32",
                                        fg="black")
        self.restart_button.pack(side="left", padx=5)

        # Make Treeview expand properly
        self.root.grid_rowconfigure(2, weight=1)  # Allows row to expand
        self.root.grid_columnconfigure(0, weight=1)  # Allows column to expand

    def set_table_data(self):
        # Clear the table
        for row in self.tree.get_children():
            self.tree.delete(row)

        for player in self.game.players:
            row = [player.name, player.money, player.recipe['lemons'], player.recipe['sugar'], player.price, player.lemonade]
            self.tree.insert("", "end", values=row)

    def next_day(self):
        self.day += 1
        self.prices_label.config(text=f"Day {self.day}")
        self.change_weather()
        self.game.simulate_day(self.day) # Simulate the day with selling lemonades
        self.show_results()
        self.game.updating_prices()
        prices = self.game.get_current_prices()
        self.sugar_price.config(text=f"${prices['sugar']:.2f}")
        self.lemons_price.config(text=f"${prices['lemons']:.2f}")
        self.cups_price.config(text=f"${prices['cups']:.2f}")
        self.set_table_data()

    def show_results(self):
        # Create the modal window
        modal = tk.Toplevel(root)
        modal.title("Results for the day")
        modal.geometry("800x600")
        modal.resizable(False, False)  # Prevent resizing

        # Block interactions with the main window
        modal.grab_set()

        # Weather Label
        weather_message = f'The weather was {self.game.weather[0]} and the percentage was {self.game.weather[1]}'
        tk.Label(modal, text=weather_message, font=("Arial", PRICES_TITLE_SIZE)).pack(pady=5)

        # Create a Frame for Treeview to add padding
        frame = tk.Frame(modal)
        frame.pack(pady=5)

        # Create Treeview
        columns = ("Player", "Money", "Lemons", "Sugar", "Cups", "Lemonade", "Sales")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)

        # Define column headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80, anchor="center")  # Adjust width as needed

        # Insert Data
        for player in self.game.players:
            row = [player.name, player.money, player.lemons, player.sugar, player.cups, player.lemonade, player.sales]
            tree.insert("", "end", values=row)

        # Add Treeview to Frame
        tree.pack()

        # OK Button to Close Modal
        ok_button = tk.Button(modal, text="OK", command=modal.destroy)
        ok_button.pack(pady=10)


    def change_weather(self):
        self.weather = self.game.get_random_weather()
        self.weather_image = Image.open(weather_images[self.weather[0]])
        self.weather_image = self.weather_image.resize((100, 100), Image.LANCZOS)
        self.weather_photo = ImageTk.PhotoImage(self.weather_image)
        self.weather_display.config(image=self.weather_photo)

    def update_prices(self):
        self.game.simulate_day(self.day)
        self.day += 1
        self.prices_label.config(text=f"Day {self.day}")
        self.change_weather()
        self.game.updating_prices()
        prices = self.game.get_current_prices()
        self.sugar_price.config(text=f"${prices['sugar']:.2f}")
        self.lemons_price.config(text=f"${prices['lemons']:.2f}")
        self.cups_price.config(text=f"${prices['cups']:.2f}")

    def open_making_window(self):
        self.player_index = 0
        self.make_lemonades()

    def make_lemonades(self):
        if self.player_index >= len(self.game.players):
            return

        player = self.game.players[self.player_index]

        self.make_window = tk.Toplevel(self.root)
        self.make_window.title("Make Lemonades")

        tk.Label(self.make_window, text=f"Player: {player.name}", font=("Arial", 12, "bold")).grid(row=0, column=0,
                                                                                                    columnspan=2)

        tk.Label(self.make_window, text="Lemonades:").grid(row=1, column=0)
        self.lemonades_var = tk.StringVar()
        self.lemonades_var.set(str(player.lemonade))
        self.lemonades_entry = tk.Entry(self.make_window, textvariable=self.lemonades_var, validate="key",
                                        validatecommand=(self.make_window.register(self.validate_integer), "%P"))
        self.lemonades_entry.grid(row=1, column=1)


        # Price Entry
        tk.Label(self.make_window, text="Price per cup:").grid(row=2, column=0)
        self.price_var = tk.StringVar()
        self.price_var.set(f"{player.price:.2f}")
        self.price_entry = tk.Entry(self.make_window, textvariable=self.price_var, validate="key",
                                    validatecommand=(self.make_window.register(self.validate_float), "%P"))
        self.price_entry.grid(row=2, column=1)

        submit_button = tk.Button(self.make_window, text="Submit", command=self.update_lemonades)
        submit_button.grid(row=3, column=0, columnspan=2)

    def update_lemonades(self):
        try:
            lemonades = int(self.lemonades_var.get())
            price = float(self.price_var.get())

            if lemonades < 0 or price < 0:
                raise ValueError

            player = self.game.players[self.player_index]
            player.lemonade = lemonades
            player.price = round(price, 2)

            message = self.game.purchase_ingredients(player)

            messagebox.showinfo("Success", message)
            self.make_window.destroy()


            self.player_index += 1
            if self.player_index == len(self.game.players):
                self.set_table_data()
            self.make_lemonades()
            # self.game.simulate_day(self.day)

        except ValueError:
            messagebox.showerror("Input Error",
                                 "Invalid input. Ensure lemonade is an integer and price is a valid amount.")

    def open_recipe_window(self):
        self.player_index = 0
        self.change_recipe_values()

    def change_recipe_values(self):
        if self.player_index >= len(self.game.players):
            return

        player = self.game.players[self.player_index]

        self.change_window = tk.Toplevel(self.root)
        self.change_window.title("Change Recipe")

        tk.Label(self.change_window, text=f"Player: {player.name}", font=("Arial", 12, "bold")).grid(row=0, column=0,
                                                                                                        columnspan=2)

        tk.Label(self.change_window, text="Lemons per cup:").grid(row=1, column=0)
        self.lemons_entry = tk.Entry(self.change_window)
        self.lemons_entry.insert(0, str(player.recipe['lemons']))
        self.lemons_entry.grid(row=1, column=1)

        tk.Label(self.change_window, text="Sugar per cup:").grid(row=2, column=0)
        self.sugar_entry = tk.Entry(self.change_window)
        self.sugar_entry.insert(0, str(player.recipe['sugar']))
        self.sugar_entry.grid(row=2, column=1)

        submit_button = tk.Button(self.change_window, text="Submit", command=self.update_player_recipe)
        submit_button.grid(row=3, column=0, columnspan=2)

    def update_player_recipe(self):
        player = self.game.players[self.player_index]
        player.recipe['lemons'] = int(self.lemons_entry.get())
        player.recipe['sugar'] = int(self.sugar_entry.get())

        self.change_window.destroy()
        self.player_index += 1
        # when finished, the player_index will be equal to the number of players
        # so we can use it to know when to stop and update the table
        if self.player_index == len(self.game.players):
            self.set_table_data()
        self.change_recipe_values()

    def restart(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in lemonade_data:
            self.tree.insert("", "end", values=row)

    def validate_integer(self, value):
        """Allows only positive integers or empty string for deletion."""
        if value.isdigit() or value == "":
            return True
        messagebox.showerror("Input Error", "Please enter a valid whole number for lemonades.")
        return False

    def validate_float(self, value):
        """Allows only floating point numbers with up to 2 decimal places or empty string for deletion."""
        try:
            if value == "":
                return True
            float_value = float(value)
            if float_value >= 0 and len(value.split(".")[-1]) <= 2:
                return True
        except ValueError:
            pass
        messagebox.showerror("Input Error", "Please enter a valid price (e.g., 2.50).")
        return False

if __name__ == "__main__":
    root = tk.Tk()
    game = Game([], 0)
    game.enter_players("players.txt")
    game.enter_number_of_days()
    app = LemonadeStandApp(root, game)
    root.mainloop()
