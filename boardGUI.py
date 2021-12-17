from constants import *

from santorini_classes import*



class Board:
    def __init__(self, kind1, kind2, color, playgame):
        #pass in PlayGame object, access window. Pack buttons onto board_frame.
        self.playgame = playgame
        self.board_frame = tk.Frame(self.playgame.window)

        self.player_factory = PlayerFactory()
        self.white_player = self.player_factory.create_player(kind1, "white")
        self.blue_player = self.player_factory.create_player(kind2, "blue")
        self.color = color
        if self.color == "white":
            self.curr_player = self.white_player
        if self.color == "blue":
            self.curr_player = self.blue_player

        self.squares = self.create_board()

    def create_board(self):
        #create 2d array board w/o borders
        board = []
        for row in range(5):
            new_row = []
            for col in range(5):
                new_row.append(Square(row, col, self))
            board.append(new_row)
        #print("hello")
        return board


    def get_legal_moves(self, player):
        workers = [player.worker1, player.worker2]
        legal_moves = []

        for d in directions.keys():
            for w in workers:
                move = Move(d, w)
                if self.check_move(move):
                    legal_moves.append(move)

        return legal_moves


    def get_legal_builds(self, player, worker):
        workers = [player.worker1, player.worker2]
        legal_builds = []
        
        #print("worker location: {}, {}".format(worker.row, worker.col))

        for d in directions.keys():
            for w in workers:
                build = Build(d, w)
                if self.check_build(build) and w == worker:
                    #print("bop")
                    legal_builds.append(build)

        return legal_builds



    #returns true if action stays on board, new square is unoccupied, and not moving to level 4 square.
    def check_board(self, action):
        #self.update_board()
        new_row = action.get_new_coords()[0]
        new_col = action.get_new_coords()[1]

        if (0 <= new_row < 5 and 0 <= new_col < 5):
            occupant = self.get_square(new_row, new_col).occupant
            level = self.get_square(new_row, new_col).level
            
            if (occupant is None and level < 4):
                return True
            else:
                #print("Cannot move {}".format(action.direction))
                return False
        else:
            #print("Cannot move {}".format(action.direction))
            return False



    #returns true if action stays on board, new square is unoccupied, and not building on level 4 square.
    def check_build(self, build):
        return self.check_board(build)



    #checks if move is valid
    def check_move(self, move):
        #self.update_board()
        if(not self.check_board(move)):
            return False

        new_row = move.get_new_coords()[0]
        new_col = move.get_new_coords()[1]
        old_row = move.worker.row
        old_col = move.worker.col
        
        old_level = self.get_square(old_row, old_col).level
        new_level = self.get_square(new_row, new_col).level
        return (new_level < 4 and new_level-old_level <= 1)


    def check_won(self, player):
        level1 = self.get_square(player.worker1.row, player.worker1.col).level
        level2 = self.get_square(player.worker2.row, player.worker2.col).level

        #if curr_player's opponent has no legal moves, curr_player wins
        #but rather, want to check curr_player has no move, then return opponent win. want this one but above line.
        opponent = self.get_opponent(player)
        # print(opponent.color)
        legal_moves = self.get_legal_moves(player)
        if len(legal_moves) == 0:
            print("no moves")
            print("{} has won".format(opponent.color))
            return opponent
        if level1 ==3 or level2 == 3:
            #print("poop")
            print("{} has won".format(player.color))
            return player

        return None
        # return (level1 == 3 or level2 == 3)




    #calculate distance between two squares
    def square_dist(self, square1, square2):
        row_dist = abs(square1.row - square2.row)
        col_dist = abs(square1.col - square2.col)
        return min(row_dist, col_dist) + abs(row_dist - col_dist)


    #calculate distance between two workers
    def worker_dist(self, worker1, worker2):
        square1 = self.get_square(worker1.row, worker1.col)
        square2 = self.get_square(worker2.row, worker2.col)
        return self.square_dist(square1, square2)


    #calculate height score of player in given position
    def height_score(self, player):
        level1 = self.get_square(player.worker1.row, player.worker1.col).level
        level2 = self.get_square(player.worker2.row, player.worker2.col).level
        return level1 + level2


    #calculate center score of player in given position
    def center_score(self, player):
        center_square = self.get_square(2,2)
        square1 = self.get_square(player.worker1.row, player.worker1.col)
        square2 = self.get_square(player.worker2.row, player.worker2.col)

        d1 = self.square_dist(square1, center_square)
        d2 = self.square_dist(square2, center_square)

        d1 = max(2-d1, 0)
        d2 = max(2-d2, 0)

        return d1+d2


    #calculate the distance score of player in given position
    def distance_score(self, player):
        opponent = self.get_opponent(player)

        #dij = distance from player.workeri to opponent.workerj
        d11 = self.worker_dist(player.worker1, opponent.worker1)
        d21 = self.worker_dist(player.worker2, opponent.worker1)
        d12 = self.worker_dist(player.worker1, opponent.worker2)
        d22 = self.worker_dist(player.worker2, opponent.worker2)

        return 8 - (min(d11, d21) + min(d12, d22))

    #calculate the total heuristic score of current player
    def score(self):
        c1, c2, c3 = 3, 2, 1
        player = self.curr_player
        if(self.check_won(player)):
            return 1000
        return c1*self.height_score(player) + c2*self.center_score(player) + c3*self.distance_score(player)


    def display_score(self):
        player = self.curr_player
        h_score = self.height_score(player)
        c_score = self.center_score(player)
        d_score = self.distance_score(player)
        return "({}, {}, {})".format(h_score, c_score, d_score)


    #evalutes what the score would be after making the given move
    def get_move_score(self, move):
        self.execute_move(move)
        #print("tried move")
        score = self.score()
        self.undo_move(move)
        #print("undid move")
        return score

    #return move with best score
    def get_best_move(self, legal_moves):
        if(len(legal_moves) == 0):
            print("error: no legal moves!")
            return
        
        high_score = -1
        for move in legal_moves:
            score = self.get_move_score(move)
            print(score)
            if score >= high_score:
                best_move = move
                high_score = score

        #print(best_move.worker.name)
        #print(best_move.direction)
        return best_move

    
    #same as above but with build
    def get_build_score(self, build):
        self.execute_build(build)
        score = self.score()
        self.undo_build(build)
        return score


    #return build with best score
    def get_best_build(self, legal_builds):
        if(len(legal_builds) == 0):
            print("error: no legal builds!")
            return
        
        high_score = -1
        for build in legal_builds:
            score = self.get_build_score(build)
            if(score > high_score):
                high_score = score
                best_build = build

        return best_build


    #updates board state given move
    def execute_move(self, move):
        #print("hello!")
        old_row = move.worker.row
        old_col = move.worker.col
        new_row = move.get_new_coords()[0]
        new_col = move.get_new_coords()[1]

        move.worker.update_location(new_row, new_col)

        #update occupancy status of old/new squares
        old_square = self.get_square(old_row, old_col)
        old_square.button.config(fg = "black")
        old_square.update_occupant(None)

        new_square = self.get_square(new_row, new_col)
        new_square.update_occupant(move.worker)
        new_square.button.config(fg = "green")


    #moves in opposite direction of given move
    def undo_move(self, move):
        opp_direction = opp_directions.get(move.direction)
        reverse_move = Move(opp_direction, move.worker)
        self.execute_move(reverse_move)



    #updates board state given build
    def execute_build(self, build):
        new_row = build.get_new_coords()[0]
        new_col = build.get_new_coords()[1]

        #update level of new_square
        new_square = self.get_square(new_row, new_col)
        new_square.update_level()
        #self.switch_player()


    #decrements height of building where the given build object would build
    def undo_build(self, build):
        new_row = build.get_new_coords()[0]
        new_col = build.get_new_coords()[1]

        #update level of new_square
        new_square = self.get_square(new_row, new_col)
        new_square.level -= 1
        #self.switch_player()
        


    #returns the opponent of the input player
    def get_opponent(self, player):
        if(player == self.white_player):
            return self.blue_player
        elif(player == self.blue_player):
            return self.white_player
        else:
            print("Invalid player!")


    def switch_player(self):
        self.curr_player = self.get_opponent(self.curr_player)


    def print_board(self):
        # for i in range(5):
        #     print('+--+--+--+--+--+')
        #     s=""
        #     for j in range(5):
        #         s += str(self.squares[i][j])
        #     s += '|'
        #     print(s)
        # print('+--+--+--+--+--+')
        for i in range(5):
            for j in range(5):
                self.squares[i][j].button.grid(row=i, column=j)
        self.board_frame.pack()



    def get_square(self, row, col):
        return self.squares[row][col]
