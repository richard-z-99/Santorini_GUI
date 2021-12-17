from constants import *

from santorini_classes import*
from board import Board
import copy
import sys
import tkinter as tk


class Memento:
    def __init__(self, kind1, kind2, playgame):
        #initialize default board
        board = Board(kind1, kind2, "white", playgame)
        board.get_square(3,1).update_occupant(board.white_player.worker1)
        board.get_square(1,3).update_occupant(board.white_player.worker2)
        board.get_square(1,1).update_occupant(board.blue_player.worker1)
        board.get_square(3,3).update_occupant(board.blue_player.worker2)

        self.history = [board]
        self.cur_board = 0
        self.playgame = playgame
    
    def undo(self):
        if(self.cur_board > 0):
            self.cur_board -= 1

    def redo(self):
        if(self.cur_board < len(self.history)-1):
            self.cur_board += 1

    def next(self, new_board):
        self.history = self.history[:self.cur_board+1]
        self.history.append(new_board)
        self.cur_board += 1

class PlayGame(tk.Frame):
    def __init__(self, kind1, kind2):
        self.game_state = "choose_worker"
        self.window = tk.Tk()
        self.memento = Memento(kind1, kind2, self)
        self.kind1 = kind1
        self.kind2 = kind2

        self.selected_worker = None

        #keeps track of current board
        self.board = self.memento.history[self.memento.cur_board]
        
        self.score_frame = tk.Frame(self.window)
        
        self.score_str = tk.StringVar()
        self.score_str.set(self.board.display_score())
        self.score_label = tk.Label(self.score_frame, textvariable=self.score_str)

        self.player_str = tk.StringVar()
        self.player_str.set(self.board.curr_player.color)
        self.player_label = tk.Label(self.score_frame, textvariable=self.player_str)

        #keep track of current frame
        self.curr_frame = self.board.board_frame

    def prompt(self):
        options = input("undo, redo, or next\n")
        while options != "next":
            output = "Turn: {}, {} ({}{})".format(self.memento.cur_board+1, self.board.curr_player.color, self.board.curr_player.worker1.name, self.board.curr_player.worker2.name)
            if sys.argv[4] == "on":
                output += ", {}".format(self.board.display_score())
            if options == "undo":
                self.undo()
                self.board.print_board()
                output = "Turn: {}, {} ({}{})".format(self.memento.cur_board+1, self.board.curr_player.color, self.board.curr_player.worker1.name, self.board.curr_player.worker2.name)
                if sys.argv[4] == "on":
                    output += ", {}".format(self.board.display_score())
                print(output)

            elif options == "redo":
                self.redo()
                self.board.print_board()
                output = "Turn: {}, {} ({}{})".format(self.memento.cur_board+1, self.board.curr_player.color, self.board.curr_player.worker1.name, self.board.curr_player.worker2.name)
                if sys.argv[4] == "on":
                    output += ", {}".format(self.board.display_score())
                print(output)

            options = input("undo, redo, or next\n")

    def print_curr_board(self):
        self.board.print_board()
        #print("TODO: print turn/player information")


    def undo(self):
        self.memento.undo()
        self.update_board()

    def redo(self):
        self.memento.redo()
        self.update_board()

    
    def run(self):
        self.print_curr_board()
        if sys.argv[4] == "on":
            self.player_label.pack()
            self.score_label.pack()
            self.score_frame.pack()
        self.window.mainloop()

        while False:
            output2 = "Turn: {}, {} ({}{})".format(self.memento.cur_board+1, self.board.curr_player.color, self.board.curr_player.worker1.name, self.board.curr_player.worker2.name)

            if sys.argv[4] == "on":
                output2 += ", {}".format(self.board.display_score())
            
            if not (self.board.check_won(self.board.curr_player) is None and self.board.check_won(self.board.get_opponent(self.board.curr_player)) is None):
                break

            print(output2)
            
            if sys.argv[3] == "on":
                self.prompt()

            if isinstance(self.board.curr_player, HumanPlayer):
                # print("Turn: {}, {} ({}{})".format(self.memento.cur_board+1, self.board.curr_player.color, self.board.curr_player.worker1.name, self.board.curr_player.worker2.name))
                curr_worker = self.board.curr_player.choose_worker()
                legal_moves = self.board.get_legal_moves(self.board.curr_player)
                move = self.board.curr_player.choose_move(legal_moves, curr_worker)
                self.execute_move(move)
                legal_builds = self.board.get_legal_builds(self.board.curr_player, move.worker)
                build = self.board.curr_player.choose_build(legal_builds, curr_worker)
                self.execute_build(build)
                self.print_curr_board()
                

        #if bot
            elif isinstance(self.board.curr_player, RandomPlayer):
                # print("Turn: {}, {} ({}{})".format(self.memento.cur_board+1, self.board.curr_player.color, self.board.curr_player.worker1.name, self.board.curr_player.worker2.name))
                legal_moves = self.board.get_legal_moves(self.board.curr_player)
                move = self.board.curr_player.choose_move(legal_moves)
                # print(move.worker.name)
                # print(move.direction)
                self.execute_move(move)
                legal_builds = self.board.get_legal_builds(self.board.curr_player, move.worker)
                build = self.board.curr_player.choose_build(legal_builds)
                # print(build.worker.name)
                # print(build.direction)
                self.execute_build(build)
                print("{},{},{}".format(move.worker.name, move.direction, build.direction))
                self.print_curr_board()
                #self.board.switch_player()
                # print("NEW TURN")
            #bot choose move will not have curr worker. also choose_build. Curr_worker is just a property of the legal_move that was chosen by the algo
        #change curr_player, iterate turn =+1. Can implement in execute_build

            elif isinstance(self.board.curr_player, HeuristicPlayer):
                legal_moves = self.board.get_legal_moves(self.board.curr_player)
                move = self.board.get_best_move(legal_moves)
                self.execute_move(move)

                # print(move.direction)
                # print(move.worker.name)

                legal_builds = self.board.get_legal_builds(self.board.curr_player, move.worker)
                build = self.board.get_best_build(legal_builds)
                self.execute_build(build)
                print("{},{},{}".format(move.worker.name, move.direction, build.direction))
                self.print_curr_board()
                #self.board.switch_player()
                # print("NEW TURN")

            else:
                print("ERROR: Invalid player type!")

            self.board.switch_player()
            # print(self.board.curr_player.color)


    def execute_move(self, move):
        #make copy of old board and put into memento
        #print("output2: {}".format(output2))
        # if(len(self.memento.history) > 1):
        #     print("move: {}".format(self.memento.history[1].curr_player.color))

        self.update_board()
        old_board_copy = copy.copy(self.board)
        self.memento.history[self.memento.cur_board] = old_board_copy

        self.board.execute_move(move)



    def execute_build(self, build):
        #print("output2: {}".format(output2))


        self.board.execute_build(build)
        self.board.switch_player()
        self.player_str.set(self.board.curr_player.color)
        self.score_str.set(self.board.display_score())

        #update memento
        self.memento.next(self.board)
        self.update_board()
        # if(len(self.memento.history) > 1):
        #     print("build: {}".format(self.memento.history[1].curr_player.color))



    def update_board(self):
        self.board = self.memento.history[self.memento.cur_board]
        
if __name__ == "__main__":
    kind1 = sys.argv[1]
    kind2 = sys.argv[2]

    # memory = sys.argv[3]
    # score_display = sys.argv[4]

    # if sys.argv[3] == "on":
    #     pass
    #     #turn on undo/redo/next functionality
    # if sys.argv[4] == "on":
    #     pass
        #turn on score display

    game1 = PlayGame(kind1, kind2)
    # game1.board.get_square(3, 0).level = 3
    # game1.board.get_square(3,1).level = 2
    game1.run()
