/****************************************************************************
 * vigenere.c
 *
 * Computer Science 50
 *
 * Encrypts inputted plaintext using Vigenere cipher
 *
 * Demonstrates use of ASCII and command line arguments
 ***************************************************************************/
#include <stdio.h>
#include <string.h>
#include <cs50.h>
#include <stdlib.h>

int
main (int argc, string argv[])
{
   
    // exit program if more than one command lines are inputted
    if(argc != 2)
    {
        printf("Error. Input one keyword please.\n");
        return 1;
    }
    
    // exit program if a character in argument is a non-alphabetical character
    int key_length = strlen(argv[1]);    
    for (int j = 0; j < key_length; j++)
    {    
        if(argv[1][j] < 'A' || argv[1][j] > 'z')
        {
            printf("Error. Input only alphabetical characters.\n");
            return 1;            
        }
    }
    
    string message = GetString();
    int n = strlen(message);
    // loops following for each character in the message
    for (int i = 0, j = 0; i < n; i++, j++)
    {
        // allows letters in keyword to be reused cyclically
        if(i >= key_length)
            j = j % (key_length);        
            
        // if character in message is not a letter, decrement j so it can be used later             
        if(message[i] < 'A' || message[i] > 'z')
             j--;
 
        // offset character in the keyword so that k ranges between 0 and 26          
        char offset;
        if(argv[1][j] >= 'a' && argv[1][j] <= 'z')
            offset = 'a';
        else if(argv[1][j] >= 'A' && argv[1][j] <= 'Z')
            offset = 'A';           
        int k = argv[1][j] - offset;
        
        // preserve lowercase letters, shift character of message by keyword's character
        if(message[i] >= 'a' && message[i] <= 'z')
            message[i] = ((message[i] - 'a' + k) % 26) + 'a';

        // preserve uppercase letters and shift the same way
        else if(message[i] >= 'A' && message[i] <= 'Z')
            message[i] = ((message[i] - 'A' + k) % 26) + 'A';
        
        printf("%c", message[i]);
        
    }        

    printf("\n");
    return 0;
}
