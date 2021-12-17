opp_directions = { 
    'n': 's', 
    'ne': 'sw', 
    'e': 'w', 
    'se': 'nw', 
    's': 'n', 
    'sw': 'ne', 
    'w': 'e', 
    'nw': 'se'
    }


directions = { 
    'n': (-1,0), 
    'ne': (-1,1), 
    'e': (0,1), 
    'se': (1,1), 
    's': (1,0), 
    'sw': (1,-1), 
    'w': (0, -1), 
    'nw': (-1, -1)
    }

inv_directions = {v: k for k, v in directions.items()}