#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
using namespace std;

int calculate_bid(int player, int pos,int* first_moves, int* second_moves) {
    //Your logic to be put here
    int i=0;
    while(*(first_moves+i)!=0)
    {
        i++;
    }
    return i;
}

int main() {
    int player;                                 //1 if first player 2 if second
    int scotch_pos;                             //position of the scotch 
    int bid,iter=0;                                    //Amount bid by the player
    size_t buf_limit = 500;
    char *first_move = (char *) malloc(buf_limit);      //previous bids of the first player
    char *second_move = (char *) malloc(buf_limit);     //prevous bids of the second player
    char remove_new_line[2];
    int first_moves[100] = {0};
    int second_moves[100] = {0};
    char *tok_1,*tok_2;
    cin>>player;
    cin>>scotch_pos;
    cin.getline(remove_new_line,2);           //removes a new line from the buffer
    cin.getline(first_move,100);
    cin.getline(second_move,500);
    tok_1 = strtok(first_move," ");
    for(int i=0; tok_1; i++) {
        first_moves[i] = atoi(tok_1); 
        tok_1 = strtok(NULL," ");
    }
    tok_2 = strtok(second_move," ");
    for(int i=0;tok_2;i++) {
        second_moves[i] = atoi(tok_2); 
        tok_2 = strtok(NULL," ");
    }
    bid = calculate_bid(player,scotch_pos,first_moves,second_moves);
    cout<<bid;
    return 0;
}
