#!/bin/python
import random
def calculate_bid(player,pos,first_moves,second_moves):
    """your logic here"""
    print 'fuck'
    return 10

#gets the id of the player
player = input()

scotch_pos = input()         #current position of the scotch

first_moves = [int(i) for i in raw_input().split()]
second_moves = [int(i) for i in raw_input().split()]
bid = calculate_bid(player,scotch_pos,first_moves,second_moves)
print bid