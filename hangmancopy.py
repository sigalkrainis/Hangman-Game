import random
import os
from colorama import  Fore,Style
from playsound import playsound
import socket

LISTENNING_PORT = 60012
LISTENNING_INTERFACE = "0.0.0.0"

HANGMAN_PHOTOS ={0: """
    x-------x""",
    1: """
    x-------x
    |
    |
    |
    |
    |""",
    2: """
    x-------x
    |       |
    |       0
    |
    |
    |""",
    3: """
    x-------x
    |       |
    |       0
    |       |   
    |
    |""",
    4: """
    x-------x
    |       |
    |       0
    |      /|\ 
    |
    |""",
    5: """
    x-------x
    |       |
    |       0
    |      /|\ 
    |      /
    |""",
    6: """
    x-------x
    |       |
    |       0
    |      /|\ 
    |      / \ 
    """}
MAX_TRIES = len(HANGMAN_PHOTOS)
OLD_LETTERS_GUESSED = []
wavFile = "/home/sigal/Downloads/happysound.m4a"
mp3File = "/home/sigal/Downloads/Failsound.m4a"


def print_welcome(client):
    
    client.send(f"""{Fore.BLUE + Style.BRIGHT}Welcome to the game Hangman {Style.RESET_ALL}
                
   | |  | |                                                
   | |__| | __ _ _ __   __ _ _ __ ___   __ _ _ __
   |  __  |/ _' | '_ \ / _' | '_ ' _ \ / _' | '_  |
   | |  | | (_| | | | | (_| | | | | | | (_| | | | |
   |_|  |_|\__,_|_| |_|\__, |_| |_| |_|\__,_|_| |_|
                        __/ |
                       |___/                 
                                                     """.encode())    
    # client.send(HANGMAN_PHOTOS[0].encode())


def check_valid_recv(letter_guessed, OLD_LETTERS_GUESSED, client):
    if letter_guessed.isalpha() and len(letter_guessed) == 1 and letter_guessed.lower() not in OLD_LETTERS_GUESSED:
        return True
    else:
        return False
    

def get_word_from_file(file_path, index):
    with open(file_path, 'r') as words:
        words_data = words.read()
        words_list = words_data.split(' ')
        if index > len(words_list):
            index = 1
        chosen_word = words_list[index - 1].replace('\n', '')
        return chosen_word

number_of_tries = 0

def try_update_letter_guessed(letter_guessed, OLD_LETTERS_GUESSED, secret_word, client):
    global number_of_tries 
    #if the letter is valid and not gussed before so add it to the guused letters list
    if not check_valid_recv(letter_guessed, OLD_LETTERS_GUESSED): 
        client.send('X')
        OLD_LETTERS_GUESSED.sort()
        client.send("->".join(OLD_LETTERS_GUESSED))
    else:
        if letter_guessed.lower() in secret_word:
            OLD_LETTERS_GUESSED.append(letter_guessed.lower())
            client.send(show_hidden_word(secret_word, OLD_LETTERS_GUESSED))
        else:
            OLD_LETTERS_GUESSED.append(letter_guessed.lower())
            number_of_tries += 1
            client.send(send_status(number_of_tries))
            client.send(':(')
            client.send(show_hidden_word(secret_word, OLD_LETTERS_GUESSED))
        
            
def show_hidden_word(secret_word, OLD_LETTERS_GUESSED):
    currect_guess = ['']
    for letter in secret_word:
        if letter in OLD_LETTERS_GUESSED:
            currect_guess.append(letter + " ")
        else:
            currect_guess.append("_")
        result = ''.join(currect_guess)
    return result


def check_win(secret_word, OLD_LETTERS_GUESSED,client):
    return ''.join(show_hidden_word(secret_word, OLD_LETTERS_GUESSED).split()) in secret_word:


def word_placeholder(secret_word):
    return '_ ' * len(secret_word)

def send_status(number_of_tries, HANGAM_PHOTOS):
    return (HANGAM_PHOTOS[number_of_tries])

def init_server():
    server = socket.socket() #creating an object 
    server.bind((LISTENNING_INTERFACE, LISTENNING_PORT))
    server.listen(1) #number of connections possible

def wait_for_client(server):
    client, adress = server.accept()
    server.close()
    return client, adress

def choose_hidden_word(client):
    client.send(r"Please enter index: ".encode())
    choice = int(client.recv(1024).decode())
    secret_word = get_word_from_file("/home/sigal/Documents/chosenword.txt", choice)
    return secret_word

def win(client):
    client.send(Fore.GREEN + 'YOU WIN!\nGOOD JOB!!!')
    playsound(wavFile, True)

def lose(client):
    client.send(Fore.RED + 'GAME OVER!'.encode())
    playsound(mp3File, True)

def main():
    global number_of_tries

    server = init_server()
    client = wait_for_client(server)

    print_welcome(client)

    secret_word = choose_hidden_word(client)

    client.send('Lets start!'.encode())
    client.send(word_placeholder(secret_word).encode())
    while number_of_tries < MAX_TRIES:
#        os.system('clear')
        client.send('Enter a letter: '.encode())
        choice2 = int(client.recv(1024).decode())
        try_update_letter_guessed(choice2 , OLD_LETTERS_GUESSED, secret_word, client)
        show_hidden_word(secret_word, OLD_LETTERS_GUESSED)
        is_win = check_win(secret_word, OLD_LETTERS_GUESSED)
        if is_win:
            win(client)
            break
    if not is_win:
        lose(client)


if __name__ == "__main__":
    main()
 


