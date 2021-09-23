##
##*************************************************************
##Assignment 6 Question 2
##Cedric Zhang
##Rock Paper Scissors
##*************************************************************
##

import random   # needed for get_move()


# global (state) variable 
# all_rocks: bool
all_rocks = False


# strings used for this question

rock = "rock"
paper = "paper"
scissors = "scissors"

input_prompt = "Rock-Paper-Scissors, play! [rock,paper,scissors,end]: "

output_computer_move = "Computer plays"
output_computer_win = "Computer wins"
output_user_win = "User wins"
output_tie = "Tie"
output_end = "Game stats ="


# get_move: None -> str
# Purpose: consumes nothing and produces a string
#    which is a "random" rock-paper-scissor move.
#    That is, it produces one of rock, paper, or scissors
# Examples:
#    get_move() => "paper"
#    get_move() => "rock"
#    get_move() => "paper"
#    get_move() => "scissors"

def get_move():
    if (all_rocks == True):
        return rock
    else:
        x = random.randint(1,3)
        if x==1:
            return rock
        elif x==2:
            return paper
        else:
            return scissors


##rock_paper_scissors: None -> None
##Purpose: rock_paper_scissors() consumes nothing and produces nothing
##Effects: User can enter strings and play rock_paper_scissors mutltiple times.
##When the game is ended the score will be printed
##Examples:
##If user enters rock and computer gets scissors, then displays User wins, user
##gets 2 points, and continues the game
##If user enters rock and computer plays rock, then displays Tie, user gets 1
##point, and continues the game
##If user enters rock and computer plays paper, then displays Computer wins, 
##user loses 1 point, and continues the game
##If user enters end, then displays Game Stat = X where X is the user's score
def rock_paper_scissors():    
    def play_game(w,t,l):
        player = raw_input (input_prompt)
        comput = get_move()
        if player == "end":
            print output_end + " " + str(2*w+t-l)
        else:
            print output_computer_move + " " + comput
            if player == comput:
                print output_tie
                return play_game (w,1+t,l)
            elif ((player == rock and comput == paper) 
                  or (player == paper and comput == scissors)
                  or (player == scissors and comput == rock)):
                print output_computer_win
                return play_game (w,t,1+l)
            else:
                print output_user_win
                return play_game (1+w,t,l)
    return play_game (0,0,0)

##Testing:
all_rocks = True
##When computer produces rock and user types scissors,
##rock_paper_scissors()=> None
print "Test 1 (computer always produces rock from now on)"
print 'If user enters scissors on the first call and end on the second call,'
print 'then Computer wins is produced and the score is -1'
rock_paper_scissors()

##rock_paper_scissors()=>None when user types rock
print 'Test 2'
print 'If user enters rock and end, then Tie is produced and the score is 1'
rock_paper_scissors()

##rock_paper_scissors() => None when user types paper
print 'Test 3'
print 'If user enters paper and end, then User wins is produced and scores 2'
rock_paper_scissors()

##rock_paper_scissors() => None when user types end
print 'Test 4'
print 'If user enters end on the first round, the function ends and score is 0'
rock_paper_scissors()