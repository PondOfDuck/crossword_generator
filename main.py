import numpy as np
import copy
import json
import jsonpickle


# 1. Heuristik: möglichst kleines Rechteck -> Graph: hier wirds schwierig
# 2. Heuristik: möglichst viele Überschneidungen -> Graph: Anzahl der Knoten


class Position:
    __row: int
    __col: int

    def __init__(self, row: int = -1, col: int = -1):
        self.__row = row
        self.__col = col

    def get_row(self):
        return self.__row

    def get_col(self):
        return self.__col

    def set_row(self, row):
        self.__row = row

    def set_col(self, col):
        self.__col = col


class Board:
    __size: int
    grid: np.chararray

    def __init__(self, size: int):
        self.__size = size
        self.__create_grid()

    def __create_grid(self):
        self.grid = np.chararray((self.__size, self.__size), unicode=True)

    def print_board(self):
        for row in self.grid:
            print(row)

    def get_size(self):
        return self.__size

    def put(self, x, y, char):
        pass


class CandidatePlacement:
    __word: str
    __position: Position
    __direction: str
    __hits: list

    def __init__(self, word: str = "", position: Position = Position(), direction: str = "", hits = []):
        self.__word = word
        self.__position = position
        self.__direction = direction
        self.__hits = hits

    def get_word(self):
        return self.__word

    def set_word(self, new_word: str):
        self.__word = new_word

    def get_position(self):
        return self.__position

    def set_position(self, pos: Position):
        self.__position = pos

    def get_direction(self):
        return self.__direction

    def set_direction(self, direction: str):
        self.__direction = direction

    def get_hits(self):
        return self.__hits

    def set_hits(self, hits: []):
        self.__hits = hits


class CrosswordGenerator:
    __board: Board
    __word_list: []
    __tracker = {}

    def __init__(self, board: Board, word_list: []):
        # Option: zufällig sortieren
        self.__board = board
        self.__word_list = word_list
        self.__set_start_word_position(word_list[0])

    @staticmethod
    def __pretty_print(obj):
        serialized = jsonpickle.encode(obj)
        print(json.dumps(json.loads(serialized), indent=2))

    def __set_start_word_position(self, first_word: str):
        col = (self.__board.get_size() - len(first_word)) // 2
        row = self.__board.get_size() // 2
        # self.__tracker[first_word] = (Position(row, col), "right")
        self.__tracker[first_word] = CandidatePlacement(word=first_word, position=Position(row, col), direction="right")

        for char in first_word:
            self.__board.grid[row][col] = char
            col = col + 1

        self.generate_crossword()

    def generate_crossword(self):
        for word_index in range(len(listOfWords) - 1):
            options_dict = self.__find_options(listOfWords[word_index + 1])
            # print(len(options_list))
            for (new_word, candidate_placement) in options_dict.items():
                for letter in candidate_placement.get_hits():
                    self.__validate_option(new_word, candidate_placement, letter)

    # neues Objekt:
    # Dict{ key = new_word,
    #       value = {
    #               old_word,
    #               old_position,
    #               old_direction,
    #               list[] hits
    #               }

    def __find_options(self, new_word: str):
        result = {}

        for set_word in self.__tracker.keys():
            letter_list = list(set_word)
            for letter_index in range(len(letter_list)):
                for char in list(new_word):
                    if char == letter_list[letter_index]:
                        if new_word in result:
                            result[new_word].get_hits().append(letter_list[letter_index])
                        else:
                            old_word = copy.deepcopy(self.__tracker.get(set_word))
                            candidate_placement = CandidatePlacement(set_word, old_word.get_position(), "", [])
                            if old_word.get_direction() == "right":
                                old_word.get_position().set_col(old_word.get_position().get_col() + letter_index)
                            else:
                                old_word.get_position().set_row(old_word.get_position().get_row() + letter_index)
                            candidate_placement.set_direction(old_word.get_direction())
                            candidate_placement.get_hits().append(letter_list[letter_index])
                            result[new_word] = candidate_placement

        for (k, v) in result.items():
            CrosswordGenerator.__pretty_print(k)
            CrosswordGenerator.__pretty_print(v)
        return result

    def __validate_option(self, new_word: str, candidate: CandidatePlacement, letter: str):
        # TODO: Doppelte Buchstaben ?!

        prefix: int = new_word.index(letter)  # Länge des Teilworts VOR dem kollidierenden Buchstaben
        suffix: int = len(new_word) - new_word.index(letter) - 1  # Länge des Teilworts NACH dem kollidierenden Buchstaben
        print("prefix: ", prefix)
        print("suffix: ", suffix)

        # Fall 1: Neues Wort sprengt das Board
        if candidate.get_direction() == "right":  # hier wird die Richtung des "alten" Wortes geprüft, hier ist das neue Wort down ausgerichtet
            if (candidate.get_position().get_row() + suffix) > self.__board.get_size() - 1 or (
                    candidate.get_position().get_row() - prefix) < 0:
                print("Out of board! RIGHT Row: ", candidate.get_position().get_row() - prefix, " Column: ", candidate.get_position().get_col() - suffix)
                return False
            new_word_placement = CandidatePlacement(
                new_word,
                Position(candidate.get_position().get_row() - prefix, candidate.get_position().get_col()),
                "down", [])

        elif candidate.get_direction() == "down":
            if (candidate.get_position().get_col() - suffix) > self.__board.get_size() - 1 or (
                    candidate.get_position().get_col() - prefix) < 0:
                print("Out of board! DOWN Row: " + str(candidate.get_position().get_row()) + " Column: " + str(candidate.get_position().get_col()))
                return False
            new_word_placement = CandidatePlacement(
                new_word,
                Position(candidate.get_position().get_col() - prefix, candidate.get_position().get_row()),
                "right", [])

        CrosswordGenerator.__pretty_print(new_word_placement)

        # self.__board.print_board()

        # Fall 2&3: Neues Wort überschneidet sich mit einem bestehenden Wort oder ist "zu nah" an einem anderen Wort
        if new_word_placement.get_direction() == "down":
            letter_position = new_word_placement.get_position()  # 1, 2
            # überprüft den ersten und letzten Buchstaben des zu setzenden Wortes, ob "davor" oder "danach" schon ein
            # Buchstabe steht (je nach Schreibrichtung) TODO: ungetestet
            if new_word_placement.get_position().get_row() - 1 >= 0:
                if self.__board.grid[new_word_placement.get_position().get_row() - 1][new_word_placement.get_position().get_col()] != "":
                    print("Abbruch wegen out of Board: vertikal am Anfang")
                    return False

            if new_word_placement.get_position().get_row() + len(new_word) <= self.__board.get_size():
                if self.__board.grid[new_word_placement.get_position().get_row() + len(new_word_placement.get_word()) - 1][new_word_placement.get_position().get_col()] != "":
                    print("Abbruch wegen out of Board: vertikal am Ende")
                    return False

            # überprüft alle Buchstaben zu setzenden Wort orthogonal zur Schreibrichtung
            for i in range(len(new_word_placement.get_word())):
                # Fall an der zu untersuchenden Position befindet sich der korrekte Buchstabe
                if new_word_placement.get_word()[i] == self.__board.grid[letter_position.get_row()][letter_position.get_col()]:
                    letter_position.set_row(letter_position.get_row() + 1)  # nächsten Buchstaben anschauen, aber per print signalisieren, dass hier ein Schnittpunkt war
                    print("Duckduck")
                    continue
                # Fall an der zu untersuchenden Position befindet sich ein anderer Buchstabe
                elif self.__board.grid[letter_position.get_row()][letter_position.get_col()] != "":
                    print("Überschneidung mit schon gesetztem Wort vorhanden")
                    return False
                # else: Feld ist noch leer

                # Nachbarfelder des zu untersuchenden Buchstaben überprüfen
                if \
                    letter_position.get_col() + 1 > self.__board.get_size() \
                    or letter_position.get_col() - 1 < 0 \
                    or self.__board.grid[letter_position.get_row()][letter_position.get_col() + 1] != "" \
                    or self.__board.grid[letter_position.get_row()][letter_position.get_col() - 1] != "":
                    print("Words too close! ")
                    break

                # Zeile von letter_position um 1 vergrößern (da wir im "down"-Fall sind)
                letter_position.set_row(letter_position.get_row() + 1)

        # TODO: ungetestet
        elif new_word_placement.get_direction() == "right":
            letter_position = new_word_placement.get_position()  # 1, 2
            # überprüft den ersten und letzten Buchstaben des zu setzenden Wortes, ob "davor" oder "danach" schon ein
            # Buchstabe steht (je nach Schreibrichtung) TODO: ungetestet
            if new_word_placement.get_position().get_col() - 1 > 0:
                if self.__board.grid[new_word_placement.get_position().get_row()][new_word_placement.get_position().get_col() - 1] != "":
                    print("Abbruch wegen out of Board 3")
                    return False

            if new_word_placement.get_position().get_col() + 1 < self.__board.get_size():
                if self.__board.grid[new_word_placement.get_position().get_row()][new_word_placement.get_position().get_col() + len(new_word_placement.get_word())] != "":
                    print("Abbruch wegen out of Board 4")
                    return False

            # überprüft alle Buchstaben zu setzenden Wort orthogonal zur Schreibrichtung
            for i in range(len(new_word_placement.get_word())):
                # CrosswordGenerator.__pretty_print(letter_position)
                if new_word_placement.get_word()[i] == self.__board.grid[letter_position.get_row()][
                    letter_position.get_col()]:
                    letter_position.set_row(letter_position.get_col() + 1)
                    print("Duckduck")
                    continue
                elif self.__board.grid[letter_position.get_row()][letter_position.get_col()] != "":
                    print("Überschneidung mit schon gesetztem Wort vorhanden")
                    return False
                if \
                    letter_position.get_row() + 1 > self.__board.get_size() \
                    or letter_position.get_row() - 1 < 0 \
                    or self.__board.grid[letter_position.get_row() + 1][letter_position.get_col()] != "" \
                    or self.__board.grid[letter_position.get_row() - 1][letter_position.get_col()] != "":
                    print("Words too close! ")
                    break

                # Zeile von letter_position um 1 vergrößern (da wir im "down"-Fall sind)
                letter_position.set_row(letter_position.get_col() + 1)


if __name__ == '__main__':
    listOfWords = ["amulett", "zebra"]
    listOfWords2 = ["amulett", "zebra", "filter", "hymen", "rudern", "burger", "karosserie", "dinge", "hilfe",
                    "vermuten"]

    ducky = Board(7)
    duckys_brother = CrosswordGenerator(ducky, listOfWords)
    # ducky.print_board()
