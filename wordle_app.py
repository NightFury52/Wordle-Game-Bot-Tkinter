import time
import json
import numpy as np
import pandas as pd
from PIL import Image
from random import choice
import customtkinter as ctk
from threading import Thread
import matplotlib.pyplot as plt
from multiprocessing import Process
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Wordle(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Wordle')
        self.resizable(False, False)
        self.configure(fg_color = 'white')

        # display parameters
        self.window_width = 1000
        self.window_height = 600
        self.display_width = self.winfo_screenwidth()
        self.display_height = self.winfo_screenheight()
        self.left = int(self.display_width/2 - self.window_width/2)
        self.top = int(self.display_height/2 - self.window_height/2)
        self.geometry(f'{self.window_width}x{self.window_height}+{self.left}+{self.top}')
        self.iconbitmap('Assets/logo.ico')

        # Loading Screen
        bg_image = ctk.CTkImage(dark_image = Image.open('Assets/bg.jpg'), size = (1000,600))
        self.bg_label = ctk.CTkLabel(self, image = bg_image, text = '')
        self.bg_label.place(x = 0,y = 0)
        
        self.loading_var = ctk.DoubleVar(value = 0)
        self.loading_progress = ctk.CTkProgressBar(self,
            variable = self.loading_var, 
            corner_radius = 0, 
            width = 300, 
            height = 30, 
            progress_color = '#FFC900', 
            fg_color = '#973F0D', 
            border_width = 2, 
            border_color = 'white')
        self.loading_progress.place(x = 500, y = 540, anchor = 'center')

        main_thread = Thread(target = self.setup)
        main_thread.start()

        # run
        self.mainloop()

    def setup(self):
        # Word List & Target Word
        self.short_word_list = self.create_word_list(short = True)
        self.long_word_list = self.create_word_list(short = False)
        self.target_word = choice(self.short_word_list)
        # print(self.target_word)

        # Json Data
        with open('data.json') as f:
            self.json_data = json.load(f)
        # print(self.json_data)

        # Creating Widgets
        create_widgets_thread = Thread(target = self.create_widgets)
        create_widgets_thread.start()

        # Data Frames
        self.hint_df = self.generate_hint_dataframe()
        # print(self.hint_df.head())
        self.updated_hint_df = self.hint_df.copy()
        # print(f'Hint DataFrame Created. Time: {time.perf_counter()}')

        create_widgets_thread.join()

        # Expected Info
        # print(f'Creating Expected Info. Time: {time.perf_counter()}')
        self.expected_info = {}
        self.button.configure(state = 'disabled')
        self.restart.configure(state = 'disabled')
        self.generate_expected_info() # uncomment this!
        self.button.configure(state = 'normal')
        self.restart.configure(state = 'normal')
        # print(f'Expected Info Created. Time: {time.perf_counter()}')

        # Destroy Loading Screen
        self.bg_label.destroy()
        self.loading_progress.destroy()

        # Placing Widegets
        self.hint_frame.place(x = 670, y = 30)
        self.blank_frame.place(x = 670, y = 30)
        # self.stats_frame.place(x = 670, y = 30)
        self.word_grid.place(x = 50, y = 50)
        self.key_board.place(x = 50, y = 450)
        self.word_entry.pack()
        self.button.pack()
        self.restart.pack()
        self.switch_widgets_button.place(x = 670, y = 30, anchor = 'ne')

    def create_widgets(self):
        # Hint Frame
        self.hint_frame = Hint_Frame(self)

        # Blank Frame
        self.blank_frame = ctk.CTkFrame(self, width = 302, height = 550, fg_color = 'white', corner_radius = 10, border_width = 3, border_color = 'black')
        self.blank_frame.grid_propagate(0)
        self.blank_frame.rowconfigure(0, weight = 1)
        self.blank_frame.columnconfigure(0, weight = 1)
        ctk.CTkLabel(self.blank_frame, image = ctk.CTkImage(dark_image = Image.open('Assets/blank.jpg'), size = (250,334)), text = '').grid(row = 0, column = 0)

        # Stats Frame
        self.selected_widget = 'blank'
        self.stats_frame = Stats_Frame(self, self.json_data)

        # Word Grid
        self.word_grid = Word_Grid(self)

        # Word Entry
        self.selected_word = 'Word-1'
        self.word_var = ctk.StringVar(value = '')
        self.word_var.trace_add('write',lambda *args: self.word_validate(selected_word = self.selected_word))
        self.word_entry = ctk.CTkEntry(self, fg_color = '#3A3A3C', text_color = 'White', textvariable = self.word_var, font = ctk.CTkFont(size = 20), width = 95, border_color = 'black')
        self.bind('<Return>', lambda event: self.apply_word())
        self.bind('<Alt-KeyPress-a>', lambda event: self.restart_app())

        # Buttons
        self.button = ctk.CTkButton(self, text = 'Apply', text_color = 'black', font = ctk.CTkFont(size = 15), command = self.apply_word, width = 80, fg_color = '#77A76B', hover_color = '#52734A')
        self.restart = ctk.CTkButton(self, text = 'Restart', text_color = 'black', font = ctk.CTkFont(size = 15), command = self.restart_app, width = 80, fg_color = '#DE4F11', hover_color = '#94350B')

        menu_image = ctk.CTkImage(dark_image = Image.open('Assets/menu.png'), size = (20,20))
        self.switch_widgets_button = ctk.CTkButton(self, image = menu_image, text = '', font = ctk.CTkFont(size = 15), fg_color = 'white', hover_color = 'grey', command = self.switch_widgets, width = 30)

        # Key Board
        self.key_board = Key_Board(self)
        # print(f'Widgets Created. Time: {time.perf_counter()}')

    # Switching widgets. Need to work here
    def switch_widgets(self):
        self.switch_widgets_button.configure(state = 'disabled')
        match self.selected_widget:
            case 'stats':
                # print('stats->hint')
                self.blank_frame.place_forget()
                self.stats_frame.place_forget()
                self.selected_widget = 'hint'
            case 'blank':
                # print('blank->stats')
                # self.blank_frame.place_forget()
                self.stats_frame.place(x = 670, y = 30)
                self.selected_widget = 'stats'
            case 'hint':
                # print('hint->blank')
                self.blank_frame.place(x = 670, y = 30)
                self.selected_widget = 'blank'
        self.switch_widgets_button.configure(state = 'normal')

    def create_word_list(self, short):
        short_file = "possible_words.txt"
        long_file = "allowed_words.txt"
        if short:    
            with open(short_file) as fp:
                word_list = [word.strip() for word in fp.readlines()]
        else:
            with open(long_file) as fp:
                word_list = [word.strip() for word in fp.readlines()]

        return word_list

    def generate_hint_dataframe(self):
        dataframe = pd.DataFrame({'target': self.short_word_list}, index = self.short_word_list)
        hint_dict = {}
        increment = 1/2309

        for guess in self.short_word_list:
            temp_dict = {}
            for target in self.short_word_list:
                temp_dict[target] = self.generate_hint(guess, target)

            self.loading_var.set(self.loading_var.get() + increment)
            hint_dict[guess] = temp_dict

        temp_df = pd.DataFrame(hint_dict)
        dataframe = pd.concat([dataframe, temp_df], axis = 1, join = 'inner')
        return dataframe

    def generate_hint(self, guess, target):
        # print(f'Guess: {guess}, Target: {target}')
        guess = guess.lower()
        hint = ['-','-','-','-','-']
        for i in range(5):
            if guess[i] == target[i]:
                hint[i] = 'X'
            elif guess[i] in target:
                hint[i] = 'O'

        return ''.join(hint)

    # for words in long_word_list, but outside short_word_list
    def check_hint(self, x, guess, hint):
        if self.generate_hint(guess, x) == hint:
            return True
        else:
            return False

    def word_validate(self, *args, selected_word):
        # print(f'var: {var}, index: {index}, mode: {mode}')
        self.word_entry.configure(state = 'disabled')
        word = self.word_var.get()
        if len(word) != 0:
            if (ord(word[-1]) < 65) or (ord(word[-1]) > 90 and ord(word[-1]) < 97) or (ord(word[-1]) > 122):
                word = word[:-1]

            else:
                word = word.upper()
                if len(word) > 5:
                    word = word[:-1]

        self.word_var.set(word)
        self.word_grid.update_labels(word, selected_word)
        self.word_entry.configure(state = 'normal')

    def apply_word(self):
        self.restart.configure(state = 'disabled')
        if self.button.cget('state') == 'normal' or self.button.cget('state') == 'active':
            # print(f"button state in apply word: {self.button.cget('state')}, time: {time.perf_counter()}")
            self.button.configure(state = 'disabled')
            if (len(self.word_var.get()) == 5) and (self.word_var.get().lower() in self.long_word_list):
                guess = self.word_var.get()
                word_number = int(self.selected_word[-1])
                                
                if word_number != 6:
                    # backend part
                    hint = self.generate_hint(guess, self.target_word)

                    # guess in short_word_list or not
                    if guess.lower() in self.short_word_list:
                        self.updated_hint_df = (self.updated_hint_df[self.updated_hint_df[guess.lower()] == hint])
                    else:
                        self.updated_hint_df = self.updated_hint_df.loc[self.updated_hint_df['target'].apply(self.check_hint, guess = guess.lower(), hint = hint)]

                    # print(self.updated_hint_df.shape)
                    # show progress
                    self.hint_frame.update_progress((2309 - self.updated_hint_df.shape[0])/2308)

                    # Thread
                    self.generate_expected_info()

                    # frontend part
                    self.key_board.update_colors(guess, hint)
                    self.word_grid.update_colors(hint, self.selected_word)
                    word_number += 1
                    self.selected_word = f'{self.selected_word[ :-1]}{str(word_number)}'
                    self.word_var.set('')

                    # Win
                    # print(f'Hint: {hint}')
                    if hint == 'XXXXX':
                        # print(f'You Win. Guess Number: {word_number - 1}')
                        self.do_if_win(word_number - 1)
                        self.word_entry.configure(state = 'disabled')
                else:
                    # backend part
                    hint = self.generate_hint(guess, self.target_word)

                    # guess in short_word_list or not
                    if guess in self.short_word_list:
                        self.updated_hint_df = (self.updated_hint_df[self.updated_hint_df[guess.lower()] == hint])
                    else:
                        self.updated_hint_df = self.updated_hint_df.loc[self.updated_hint_df['target'].apply(self.check_hint, guess = guess, hint = hint)]

                    # print(self.updated_hint_df.shape)
                    # show progress
                    self.hint_frame.update_progress((2309 - self.updated_hint_df.shape[0])/2308)

                    # Thread
                    self.generate_expected_info()

                    # frontend part
                    self.key_board.update_colors(guess, hint)
                    self.word_grid.update_colors(self.generate_hint(guess, self.target_word), self.selected_word)
                    self.selected_word = ''
                    self.word_var.set('')

                    # Win
                    # print(f'Hint: {hint}')
                    if hint == 'XXXXX':
                        # print(f'You Win. Guess Number: {word_number}')
                        self.do_if_win(word_number)
                    else:
                        self.word_var.set(self.target_word.upper())
                        self.json_data['matches_played'] += 1
                        self.json_data['matches_lost'] += 1
                        with open("data.json", 'w') as fp:
                            json.dump(self.json_data, fp, indent = 4)
                        self.stats_frame.update_labels()
                        
                    self.word_entry.configure(state = 'disabled')
                    
            else:
                self.word_entry.configure(text_color = 'Red')
                self.after(100, lambda: self.word_entry.configure(text_color = 'White'))
                
            self.button.configure(state = 'normal')
        self.restart.configure(state = 'normal')

    def do_if_win(self, word_number):
        self.json_data['matches_played'] += 1
        self.json_data['matches_won'] += 1
        self.json_data['win_indeces'][str(word_number)] += 1
        with open("data.json", 'w') as fp:
            json.dump(self.json_data, fp, indent = 4)

        self.stats_frame.update_labels()
        self.stats_frame.update_bar_plot()

    def generate_expected_info(self):
        # self.button.configure(state = 'disabled')
        # self.restart.configure(state = 'disabled')
        self.expected_info = {}
        if self.updated_hint_df.shape[0] != 1:
            for word in self.short_word_list:
                vector = self.updated_hint_df[word].value_counts(normalize = True)
                self.expected_info[word] = (vector.multiply(1 - vector)).sum()

            self.hint_frame.update_scrollable_frame(self.expected_info)

        else:
            self.hint_frame.reset_scrollable_frame()
            self.hint_frame.update_scrollable_frame({self.updated_hint_df.index[0]: 1})

        self.expected_info = {}
        # self.button.configure(state = 'normal')
        # self.restart.configure(state = 'normal')

    def restart_app(self):
        self.button.configure(state = 'disabled')
        if self.restart.cget('state') == 'normal' or self.restart.cget('state') == 'active':
            self.restart.configure(state = 'disabled')
            self.word_entry.configure(state = 'normal')

            # New Target
            self.word_var.set('')
            self.selected_word = 'Word-1'
            self.target_word = choice(self.short_word_list)
            # print(self.target_word)

            # Data Frame
            self.updated_hint_df = self.hint_df.copy()
            self.hint_frame.update_progress(0)

            # Reset Labels
            self.key_board.reset_colors()
            self.word_grid.reset_labels()

            # Expected Info
            # print(f"button state in restart-1: {self.button.cget('state')}, time: {time.perf_counter()}")
            self.generate_expected_info()
            # print(f"button state in restart-2: {self.button.cget('state')}, time: {time.perf_counter()}")
            self.restart.configure(state = 'normal')
        self.button.configure(state = 'normal')


class Word_Grid(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master = parent, fg_color = 'black', height = 330, width = 275, corner_radius = 5)
        self.columnconfigure(0, weight = 1, uniform = 'a')
        self.columnconfigure((1,2,3,4,5), weight = 20, uniform = 'a')
        self.columnconfigure(6, weight = 1, uniform = 'a')
        self.rowconfigure(0, weight = 1, uniform = 'a')
        self.rowconfigure((1,2,3,4,5,6), weight = 20, uniform = 'a')
        self.rowconfigure(7, weight = 1, uniform = 'a')
        self.labels = self.create_labels()
        # self.pack_propagate(0)
        # self.grid_propagate(0)

    def create_labels(self):
        label_dict = {}
        for word in ['Word-1', 'Word-2', 'Word-3', 'Word-4', 'Word-5', 'Word-6']:
            label_dict[word] = {}
            for index in range(5):
                label_dict[word][index] = Letter_Square(self)
                label_dict[word][index].grid(row = int(word[-1]), column = index+1, sticky = 'nsew', padx = 1.5, pady = 1.5)

        return label_dict

    def update_labels(self, word, selected_word):
        if selected_word:
            for index in self.labels[selected_word].keys():
                if index < len(word):
                    self.labels[selected_word][index].configure_square(label_text = word[index], frame_color = 'white')
                else:
                    self.labels[selected_word][index].configure_square(label_text = '')

    def update_colors(self, hint, selected_word):
        # print(hint)
        for i in range(5):
            match hint[i]:
                case '-':
                    self.labels[selected_word][i].configure_square(label_color = '#3A3A3C', frame_color = '#3A3A3C')
                case 'O':
                    self.labels[selected_word][i].configure_square(label_color = '#B59F3A', frame_color = '#B59F3A')
                case 'X':
                    self.labels[selected_word][i].configure_square(label_color = '#528D4D', frame_color = '#528D4D')

    def reset_labels(self):
        for word in self.labels.keys():
            for i in range(5):
                self.labels[word][i].configure_square(label_color = '#121212', frame_color = '#333333', label_text = '')


class Letter_Square(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master = parent, fg_color = '#333333', corner_radius = 2, width = 53, height = 53)
        self.pack_propagate(0)
        # self.grid_propagate(0)
        self.label = ctk.CTkLabel(self, text = '', corner_radius = 2, text_color = 'white', fg_color = '#121212', font = ctk.CTkFont(size = 35))
        self.label.pack(expand = True, fill = 'both', padx = 2, pady = 2)

    def configure_square(self, label_text = None, label_color = '#121212', frame_color = '#333333'):
        if label_text != None:
            self.label.configure(text = label_text)
        self.label.configure(fg_color = label_color)
        self.configure(fg_color = frame_color)


class Hint_Frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master = parent, width = 302, height = 550, fg_color = 'white', corner_radius = 10)
        self.rowconfigure((0,1), weight = 1, uniform = 'a')
        self.rowconfigure(2, weight = 8, uniform = 'a')
        self.pack_propagate(0)
        self.grid_propagate(0)

        # Game Progress Bar
        self.game_progress_frame = ctk.CTkFrame(self, corner_radius = 10, fg_color = '#7ABFAA', border_width = 3, border_color = 'black')
        self.game_progress_frame.grid(row = 0, column = 0, sticky = 'nsew', padx = 2, pady = 2)
        self.game_progress_var = ctk.DoubleVar(value = 0)
        self.game_progress = ctk.CTkProgressBar(self.game_progress_frame, variable = self.game_progress_var, corner_radius = 0, height = 15, progress_color = '#0D952F', fg_color = 'white', border_width = 2, border_color = '#243BEF')
        self.game_progress.pack(side = 'bottom', pady = 10)

        # Game Progress Label
        self.game_progress_label = ctk.CTkLabel(self.game_progress_frame, text = '0.00%', width = 50, font = ctk.CTkFont(slant = 'italic', weight = 'bold'), height = 16, text_color = 'black', fg_color = '#7ABFAA')
        self.game_progress_label.place(x = 145, y = 15, anchor = 'center')

        # Label
        self.label_frame = ctk.CTkFrame(self, corner_radius = 10, fg_color = '#7ABFAA', border_width = 3, border_color = 'black')
        self.label_frame.grid(row = 1, column = 0, sticky = 'nsew', padx = 2, pady = 2)
        ctk.CTkLabel(self.label_frame, text  = 'Best Guess\tInfo', font = ctk.CTkFont(size = 20, weight = 'bold'), corner_radius = 10, text_color = 'black', fg_color = '#7ABFAA').pack(expand = True, fill = 'both', padx = 10, pady = 10)

        # Scrollable Frame
        self.scrollableframe = ctk.CTkScrollableFrame(master = self, width = 271, fg_color = '#7ABFAA', border_width = 3, border_color = 'black', scrollbar_fg_color = 'black')
        self.scrollableframe.grid(row = 2, column = 0, sticky = 'ns', padx = 2, pady = 4)
        # print(self.scrollableframe.config())

        # Best Guess Widgets
        self.best_guess_widgets = {}
        self.create_best_guess_widgets()
        # print(self.best_guess_widgets)

    def update_progress(self, progress):
        self.game_progress_var.set(progress)
        self.game_progress_label.configure(text = f'{(progress*100):.2f}%')

    def create_best_guess_widgets(self):
        for i in range(20):
            self.best_guess_widgets[i] = Hint_widget(parent = self.scrollableframe)

    def update_scrollable_frame(self, expected_info):
        # self.reset_scrollable_frame()
        index = 0
        for hint, info in sorted(expected_info.items(), key = lambda x: x[1], reverse = True):
            # print(info)
            self.best_guess_widgets[index].update_widgets(hint = hint, info = info)
            index += 1
            if index >= 20:
                break

    def reset_scrollable_frame(self):
        for widget in self.best_guess_widgets.values():
            widget.update_widgets(hint = '', info = 0)


class Hint_widget(ctk.CTkFrame):
    def __init__(self, parent, hint = '', info = 0):
        super().__init__(master = parent, width = 260, height = 37, fg_color = '#40413F', corner_radius = 0, border_width = 3, border_color = 'black')
        # self.columnconfigure((0,1), weight = 1, uniform = 'a')
        self.var = ctk.DoubleVar(value = info)
        self.pack_propagate(0)

        self.label = ctk.CTkLabel(self, text = hint, text_color = 'white', width = 80, height = 24, corner_radius = 0, font = ctk.CTkFont(size = 20))
        self.label.pack(side = 'left', padx = 4, pady = 4)
        ctk.CTkProgressBar(self, variable = self.var, corner_radius = 0, height = 29, progress_color = '#FFA229', fg_color = '#F5E7D1', border_width = 2, border_color = 'black').pack(side = 'right', padx = 4, pady = 4)
        self.progress_label = ctk.CTkLabel(self, text = '', font = ctk.CTkFont(slant = 'italic', weight = 'bold'), height = 16, text_color = 'black')
        self.progress_label.place(x = 122, y = 20, anchor = 'center')

        self.pack(pady = 2)

    def update_widgets(self, hint = '', info = 0):
        # print(self.label)
        self.label.configure(text = hint)
        if info != 0:
            self.progress_label.configure(text = f'{info*100:.2f}%', fg_color = '#FFA229')
        else:
            self.progress_label.configure(text = '', fg_color = 'white')
        self.var.set(info)


class Stats_Frame(ctk.CTkFrame):
    def __init__(self, parent, json_data = None):
        super().__init__(master = parent, width = 302, height = 550, corner_radius = 10, border_width = 3, border_color = 'black')
        self.rowconfigure(0, weight = 1, uniform = 'a')
        self.rowconfigure((1,2), weight = 2, uniform = 'a')
        self.grid_propagate(0)
        self.data = json_data

        # Stats Widgets
        self.stats_info_labels = {}
        self.stats_widget = self.create_stats_widget(['matches\nwon', 'matches\nplayed', 'matches\nlost'], [self.data['matches_won'], self.data['matches_played'], self.data['matches_lost']])
        self.stats_widget.grid(row = 0, column = 0, padx = 5, pady = 5)

        # Bar Plot
        self.bar_frame = None
        self.update_bar_plot()

        # History Label
        ctk.CTkLabel(self, text = 'Josh Wardle, a software engineer in Brooklyn, \nknew his partner loved word games, so he \ncreated a guessing game for just the two \nof them. As a play on his last name, he named \nit Wordle. But after they played for months,\nand after it rapidly became an obsession in his \nfamily\'s WhatsApp group once he introduced \nit to relatives, Mr. Wardle thought he \nmight be on to something and released it \nto the rest of the world in October. \nOn Nov 1, 90 people played. On a Sunday, \njust over two months later, \nmore than 300,000 people played.').grid(row = 2, column = 0, padx = 5, pady = 7, sticky = 'nsew')

    def create_stats_widget(self, label_text_list, number_list):
        match_stats_frame = ctk.CTkFrame(self, width = 292)
        match_stats_frame.columnconfigure((0,1,2), weight = 1, uniform = 'a')
        match_stats_frame.rowconfigure(0, weight = 3, uniform = 'a')
        match_stats_frame.rowconfigure(1, weight = 2, uniform = 'a')
        match_stats_frame.grid_propagate(0)

        for index, (text, info) in enumerate(zip(label_text_list, number_list)):
            info_label = ctk.CTkLabel(match_stats_frame, text = info, fg_color = 'white', font = ctk.CTkFont(size = 40), text_color = 'black', corner_radius = 5)
            info_label.grid(row = 0, column = index, sticky = 'nsew', padx = 2, pady = 2)
            self.stats_info_labels['_'.join(text.split())] = info_label
            ctk.CTkLabel(match_stats_frame, text = text, fg_color = 'white', font = ctk.CTkFont(size = 12), text_color = 'black', corner_radius = 5).grid(row = 1, column = index, sticky = 'nsew', padx = 2)

        return match_stats_frame

    def update_labels(self):
        for title, label in self.stats_info_labels.items():
            label.configure(text = str(self.data[title]))

    def update_bar_plot(self):
        # Frame
        if self.bar_frame: self.bar_frame.pack_forget()
        self.bar_frame = ctk.CTkFrame(self)
        self.bar_frame.grid(row = 1, column = 0, sticky = 'nsew', padx = 7)

        # Figure
        figure = plt.Figure()
        figure.subplots_adjust(left = 0.08, bottom = 0.01, top = 1, right = 0.88)
        figure.set_facecolor('#3A3A3C')
        
        # Graph
        ax = figure.add_subplot(111)
        ax.set_facecolor('#3A3A3C')
        # print(*zip(*self.data['win_indeces'].items()))
        bars = ax.barh(*zip(*self.data['win_indeces'].items()), color = 'white')
        ax.set_xlim(0,max(self.data['win_indeces'].values()))
        for side in ['top', 'bottom', 'left', 'right']:
            ax.spines[side].set_color('#3A3A3C')

        # Configuring the Axes
        ax.xaxis.set_visible(False)
        ax.yaxis.set_ticks_position('none')
        ax.tick_params(colors = 'white', which = 'major')

        # Bar Label
        for i, v in enumerate(self.data['win_indeces'].values()):
            ax.text(v + 0.05, i - 0.13, str(v), color = 'grey')
        # ax.bar_label(bars, padding = 2, color = 'grey')

        # widget
        figure_widget = FigureCanvasTkAgg(figure, master = self.bar_frame)
        figure_widget.get_tk_widget().place(x = 5, y = 5, width = 348, height = 265)


class Key_Board(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master = parent, fg_color = 'transparent', height = 100, width = 330, corner_radius = 5)
        self.key_list = {}
        self.create_key_list()

        for key in self.key_list.values():
            key.pack(side = 'left', padx = 1)

    def create_key_list(self):
        frame_1 = ctk.CTkFrame(self, fg_color = 'white', width = 320, height = 32, corner_radius = 2)
        for letter in ['Q','W','E','R','T','Y','U','I','O','P']:
            self.key_list[letter] = ctk.CTkLabel(frame_1, text = letter, text_color = 'white', font = ctk.CTkFont(size = 18), corner_radius = 2, fg_color = '#121212', width = 30, height = 30)
        frame_1.place(x = 4, y = 2)
        frame_1.pack_propagate(0)
        # frame_1.grid_propagate(0)

        frame_2 = ctk.CTkFrame(self, fg_color = 'white', width = 288, height = 32, corner_radius = 2)
        for letter in ['A','S','D','F','G','H','J','K','L']:
            self.key_list[letter] = ctk.CTkLabel(frame_2, text = letter, text_color = 'white', font = ctk.CTkFont(size = 18), corner_radius = 2, fg_color = '#121212', width = 30, height = 30)
        frame_2.place(x = 20, y = 34)
        frame_2.pack_propagate(0)

        frame_3 = ctk.CTkFrame(self, fg_color = 'white', width = 224, height = 32, corner_radius = 0)
        for letter in ['Z','X','C','V','B','N','M']:
            self.key_list[letter] = ctk.CTkLabel(frame_3, text = letter, text_color = 'white', font = ctk.CTkFont(size = 18), corner_radius = 2, fg_color = '#121212', width = 30, height = 30)
        frame_3.place(x = 40, y = 66)
        frame_3.pack_propagate(0)

    def reset_colors(self):
        for key in self.key_list.values():
            key.configure(fg_color = '#121212')

    def update_colors(self, guess, hint):
        matched_indices = []
        for i in range(5):
            match hint[i]:
                case '-':
                    self.key_list[guess[i]].configure(fg_color = '#3A3A3C')
                case 'O':
                    if self.key_list[guess[i]].cget('fg_color') != '#528D4D':
                        self.key_list[guess[i]].configure(fg_color = '#B59F3A')
                case 'X':
                    matched_indices.append(i)
        for index in matched_indices:
            self.key_list[guess[index]].configure(fg_color = '#528D4D')            




if __name__ == '__main__':
    ctk.set_appearance_mode('light')
    Wordle()


