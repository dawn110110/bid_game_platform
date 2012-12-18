import java.io.*;
import java.util.*;

public class Solution {

    static int calculate_bid(int player, int pos,int[] first_moves,int[] second_moves) {
        //Your logic to be put here
        return 10;
    } 

    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        in.useDelimiter("\n");
        int player = Integer.parseInt(in.next().trim());                     //1 if first player 2 if second
        int scotch_pos = Integer.parseInt(in.next().trim());                 //position of the scotch
        int bid = 0;                                   //Amount bid by the player
        int[] first_moves = new int[100];
        int[] second_moves = new int[100];
        
        String first_move = in.next();
        String[] move_1 = first_move.trim().split(" ");
        String second_move = in.next();
        String[] move_2= second_move.trim().split(" ");

        if(first_move.equals("") == false) {
            for (int i=0;i<move_1.length;i++) {
                first_moves[i] = Integer.parseInt(move_1[i]);
                second_moves[i] = Integer.parseInt(move_2[i]);
            }
        }
        bid = calculate_bid(player,scotch_pos,first_moves,second_moves);
        System.out.print(bid);
    }
}
