from tkinter import *
from functools import partial
import _thread
import time
import random
import socket

#Create main window
win = Tk()
win.title("Color Competition")
win.geometry("700x400")


grid =  ([0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],)

#Place grid of buttons in the upper left corner
gridFrame = Frame(win)
gridFrame.pack()
gridFrame.place(anchor = "nw")
gridFrame.grid(row = 0, column = 0)

def change_color(button, num, color):
    #Change the color and # displayed on the button and cause it to switch back on next click
    button.configure(text = ("[" + str(num) + "]"), bg = color, command = partial(change_color, button, 1, "RED"))
    #print("Row: " + str(button.grid_info()["row"]) + "\nColumn: " + str(button.grid_info()["column"]) + "\n")

    
#Fill grid with default buttons
def reset():
    for rowNum in range(8):
        for colNum in range(8):
            grid[rowNum][colNum] = Button(gridFrame, text = "[ ]", width = 5, height = 2)
            #partial() makes a call to change_color() when the button is clicked
            grid[rowNum][colNum].configure(command = partial(change_color, grid[rowNum][colNum], 1, "RED"))
            grid[rowNum][colNum].grid(row = rowNum, column = colNum)

reset()


#                     <<< MESSAGE BOX >>>

#Keep the display frame and message frame together
megaFrame = Frame(win)
megaFrame.grid(row = 0, column = 1)


displayFrame = Frame(megaFrame)
displayFrame.pack(side = TOP, fill = X)

#Scrollbar for the message display
bar = Scrollbar(displayFrame)
bar.pack(side = RIGHT, fill = Y)

#Create message display
textBox = Listbox(displayFrame, width = 36, height = 20, yscrollcommand = bar.set)
textBox.pack(side = RIGHT)


#Create frame to take message input
messageFrame = Frame(megaFrame)
messageFrame.pack(side = BOTTOM)
enter = Entry(messageFrame)
enter.grid(row = 1, column = 1)
Label(messageFrame, text = "Message: ").grid(row = 1, column = 0)

#Move text from the message box to the display box
def call():
    textBox.insert(END, "[P1] " + enter.get())
    enter.delete(0, len(enter.get()))
    
Button(messageFrame, text = "Send", command = call).grid(row = 2, column = 1)

#               <<< END OF MESSAGE BOX CODE >>>



def empty():
    print()


#Returns the number of buttons 
def count(color):
    count = 0
    
    for row in range(8):
        for col in range(8):
            if grid[row][col].cget("bg") == color:
                count += 1

    return count


def single(seconds, menu):
    reset()

    #Disable multiple active singleplayer games
    menu.entryconfig(2, command = partial(empty))
    menu.entryconfig(3, command = partial(empty))
    menu.entryconfig(4, command = partial(empty))

    start = time.time()
    textBox.insert(END, "45 seconds on the clock!")
    textBox.insert(END, "[P2] Game on!")
    
    cur = time.time()
    display = False
    while (cur - start) < 45:
        time.sleep(seconds)
        grid[random.randint(0, 7)][random.randint(0, 7)].configure(text = "[2]", bg = "BLUE")
        
        cur = time.time()
        if (cur - start) >= 35 and not display:
            textBox.insert(END, "10 seconds left!")
            display = True

    score = count("RED")
    botScore = count("BLUE")
    reset()

    textBox.insert(END, "~~~~~~~~~~~~~")
    textBox.insert(END, "P1 Score: " + str(score))
    textBox.insert(END, "P2 Score: " + str(botScore))
    textBox.insert(END, "P1 wins!" if score > botScore else ("P2 wins!" if score != botScore else "Tie!"))
    textBox.insert(END, "~~~~~~~~~~~~~")

    #Reenable new games
    menu.entryconfig(2, command = lambda : _thread.start_new_thread(single, (0.6, gameMenu)))
    menu.entryconfig(3, command = lambda : _thread.start_new_thread(single, (0.35, gameMenu)))
    menu.entryconfig(4, command = lambda : _thread.start_new_thread(single, (0.2, gameMenu)))

def multiClick(row, col, conn, button):
    button.configure(text = "1", bg = "RED")
    conn.send(bytes([row]))
    conn.send(bytes([col]))
    
def multi():
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(("108.218.148.128", 1212))
    textBox.insert(END, "Connected to server!")

    #Configure buttons to send data
    for row in range(8):
        for col in range(8):
            grid[row][col].configure(command = partial(multiClick, row, col, conn, grid[row][col]))
                                     
    _thread.start_new_thread(waiter, (conn,))

    
def waiter(conn):
    while True:
        row = int.from_bytes(conn.recv(1024), sys.byteorder)
        col = int.from_bytes(conn.recv(1024), sys.byteorder)

        grid[row][col].configure(text = "[2]", bg = "BLUE")

    
#Create cascade menu, placed at the bottom so it has access to all above functions
mainMenu = Menu(win)
win.config(menu = mainMenu) #Set mainMenu as the default menu for the window
gameMenu = Menu(mainMenu) #Create submenu for the Game button
helpMenu = Menu(mainMenu)
mainMenu.add_cascade(label = "Game", menu = gameMenu) #Create game button
mainMenu.add_cascade(label = "Help", menu = helpMenu) #Create help button


gameMenu.add_command(label = "Singleplayer")
gameMenu.add_command(label = "Easy", command = lambda : _thread.start_new_thread(single, (0.6, gameMenu)))
gameMenu.add_command(label = "Medium", command = lambda : _thread.start_new_thread(single, (0.35, gameMenu)))
gameMenu.add_command(label = "Hard", command = lambda : _thread.start_new_thread(single, (0.2, gameMenu)))

gameMenu.add_separator()
gameMenu.add_command(label = "Connect to Multiplayer", command = lambda : _thread.start_new_thread(multi, ()))
gameMenu.add_separator()
gameMenu.add_command(label = "Exit", command = win.destroy) #<<< NEEDS FUNCTIONING COMMAND >>>

win.mainloop()
