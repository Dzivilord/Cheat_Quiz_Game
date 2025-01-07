
import pytesseract as tess 
tess.pytesseract.tesseract_cmd=r'Pytesseract\\tesseract.exe'
from PIL import Image 
from fuzzywuzzy import fuzz
import pyautogui
import customtkinter 
import pyautogui as pag
import time
import json
import os

# Tạo các biến lưu tọa độ

#pyinstaller --onefile --windowed your_script.py
#pyinstaller --onefile --windowed D:\Auto_Answer\Attempt2.py

root = customtkinter.CTk()
root.title("Drag and Drop Demo")
root.geometry("340x450")
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
X1 = customtkinter.StringVar(value="10")
Y1 = customtkinter.StringVar(value="20")
X2 = customtkinter.StringVar(value="30")
Y2 = customtkinter.StringVar(value="40")
X3 = customtkinter.StringVar(value="10")
Y3 = customtkinter.StringVar(value="20")
X4 = customtkinter.StringVar(value="30")
Y4 = customtkinter.StringVar(value="40")
Question_X_TL = customtkinter.StringVar(value="10")
Question_Y_TL = customtkinter.StringVar(value="20")
Question_X_BR = customtkinter.StringVar(value="10")
Question_Y_BR = customtkinter.StringVar(value="20")
Choice_X_TL = customtkinter.StringVar(value="10")
Choice_Y_TL = customtkinter.StringVar(value="20")
Choice_X_BR = customtkinter.StringVar(value="10")
Choice_Y_BR = customtkinter.StringVar(value="20")




def Load_question(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        questions = json.load(file)
    return questions

# Sử dụng hàm để load câu hỏi từ file
questions = Load_question('questions.json')

def erasefile(path):
    with open(path,"w"):
        pass
    

def capture():
    x = int(Question_X_TL.get())
    y = int(Question_Y_TL.get())
    width = int(Question_X_BR.get()) - x
    height = int(Question_Y_BR.get()) - y

    X = int(Choice_X_TL.get())
    Y = int(Choice_Y_TL.get())
    WIDTH = int(Choice_X_BR.get()) - X
    HEIGHT = (int(Choice_Y_BR.get()) - Y)

    pos_A=pag.position(X1.get(),Y1.get())
    pos_B=pag.position(X2.get(),Y2.get())
    pos_C=pag.position(X3.get(),Y3.get())
    pos_D=pag.position(X4.get(),Y4.get())

    Choice_Position={0:pos_A,
            1:pos_B,
            2:pos_C,
            3:pos_D}
    # Chụp ảnh màn hình vùng xác định
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    screenshot.save('question.png')
    
    img=Image.open("question.png")
    #img.show()
    Question=tess.image_to_string(img,lang='vie')
    #print(Question)
    
    exists = False
    best_ratio = 0
    best_key = None

    for key in questions:
        current_ratio = fuzz.ratio(Question, key)
        if current_ratio >70:
            print(f"Key: {key}, Ratio: {current_ratio}")
        if current_ratio > best_ratio:
            best_ratio = current_ratio
            best_key = key


    if best_key:
        #print("Answer: " + questions.get(best_key))
        my_label.configure(text=questions.get(best_key))
        index = best_key
        exists = True
        
    non_exists_path="Temp.txt"
    if(exists==False):
        with open(non_exists_path,"a",encoding='utf-8') as file:
            my_label.configure(text="Not Found")
            file.write(Question)
            return

    
    options_screenshot= pyautogui.screenshot(region=(X, Y, WIDTH, HEIGHT))
    #options_screenshot.show()
    
    # custom_config = r'--psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,./*+0123456789'
    # options_text = tess.image_to_string(options_screenshot, config=custom_config)
    options_text = tess.image_to_string(options_screenshot,lang='vie')
    #print (options_text)
    
    lines = options_text.splitlines()
    lines = [line for line in lines if line.strip() != ""]  # Xóa các dòng chỉ chứa khoảng trắng
    #print(lines)

    # for i in range(0, len(lines)):
    #     print(lines[i])
    #     if (questions.get(index)==lines[i]):
    #         print("This is it: "+ lines[i])
    #         print(i)
    #         pag.click(Choice_Position.get(i))
    best_match_index = -1
    best_match_ratio = 0

    for i in range(0, len(lines)):
        
        current_ratio = fuzz.ratio(questions.get(index), lines[i])
        print(f"Index: {i}, Line: {lines[i]}, Ratio: {current_ratio}")
        if current_ratio > best_match_ratio:
            best_match_ratio = current_ratio
            best_match_index = i
            #print(i)

    if best_match_index != -1:
        print("Best match: " + lines[best_match_index])
        print("Index: " + str(best_match_index))
        pag.click(Choice_Position.get(int(best_match_index)))
        

    
def create_on_release(X_var, Y_var, Label):
    def on_release(event):
        mouse_pos = pag.position()
        X_var.set(mouse_pos.x)
        Y_var.set(mouse_pos.y)
        frame1.configure(cursor="arrow")
        Label.configure(text=f"X: {X_var.get()}, Y: {Y_var.get()}")
    return on_release

# Tạo cửa sổ giao diện chính





def save_position():
 
    coordinates = {
        "X1": X1.get(),
        "Y1": Y1.get(),
        "X2": X2.get(),
        "Y2": Y2.get(),
        "X3": X3.get(),
        "Y3": Y3.get(),
        "X4": X4.get(),
        "Y4": Y4.get(),
        
        "Question_X_TL": Question_X_TL.get(),
        "Question_Y_TL": Question_Y_TL.get(),
        "Question_X_BR": Question_X_BR.get(),
        "Question_Y_BR": Question_Y_BR.get(),
        
        "Choice_X_TL": Choice_X_TL.get(),
        "Choice_Y_TL": Choice_Y_TL.get(),
        "Choice_X_BR": Choice_X_BR.get(),
        "Choice_Y_BR": Choice_Y_BR.get()
    }
    with open('coordinates.json', 'w') as f:
        json.dump(coordinates, f, indent=4)


def load_position():
    try:
        with open('coordinates.json', 'r') as f:
            coordinates = json.load(f)

        X1.set(coordinates["X1"])
        Y1.set(coordinates["Y1"])
        X2.set(coordinates["X2"])
        Y2.set(coordinates["Y2"])
        X3.set(coordinates["X3"])
        Y3.set(coordinates["Y3"])
        X4.set(coordinates["X4"])
        Y4.set(coordinates["Y4"])
        
        Question_X_TL.set(coordinates["Question_X_TL"])
        Question_Y_TL.set(coordinates["Question_Y_TL"])
        Question_X_BR.set(coordinates["Question_X_BR"])
        Question_Y_BR.set(coordinates["Question_Y_BR"])
        
        Choice_X_TL.set(coordinates["Choice_X_TL"])
        Choice_Y_TL.set(coordinates["Choice_Y_TL"])
        Choice_X_BR.set(coordinates["Choice_X_BR"])
        Choice_Y_BR.set(coordinates["Choice_Y_BR"])
        
        Label_A.configure(text=f"X: {X1.get()}, Y: {Y1.get()}")
        Label_B.configure(text=f"X: {X2.get()}, Y: {Y2.get()}")
        Label_C.configure(text=f"X: {X3.get()}, Y: {Y3.get()}")
        Label_D.configure(text=f"X: {X4.get()}, Y: {Y4.get()}")
        
        Label_QTL.configure(text=f"X: {Question_X_TL.get()}, Y: {Question_Y_TL.get()}")
        Label_QBR.configure(text=f"X: {Question_X_BR.get()}, Y: {Question_Y_BR.get()}")
        
        Label_ATL.configure(text=f"X: {Choice_X_TL.get()}, Y: {Choice_Y_TL.get()}")
        Label_ABR.configure(text=f"X: {Choice_X_BR.get()}, Y: {Choice_Y_BR.get()}")
        
    except FileNotFoundError:
        print("File not found. Make sure you have saved coordinates before loading.")

#Tao Thanh tieu de 




# Tạo nút bấm
frame1 = customtkinter.CTkButton(root, width=30, height=30, text='A', font=("Helvetica", 14))
frame1.place(x=20,y=150)

Label_A=customtkinter.CTkLabel(root,text="",width=100,height=40,font=("Helvetica",14),bg_color="Gray",text_color="White")
Label_A.place(x=70,y=150)

frame2 = customtkinter.CTkButton(root, width=30, height=30, text='B', font=("Helvetica", 14))
frame2.place(x=20,y=200)

Label_B=customtkinter.CTkLabel(root,text="",width=100,height=40,font=("Helvetica",14),bg_color="Gray",text_color="White")
Label_B.place(x=70,y=200)

frame3 = customtkinter.CTkButton(root, width=30, height=30, text='C', font=("Helvetica", 14))
frame3.place(x=20,y=250)

Label_C=customtkinter.CTkLabel(root,text="",width=100,height=40,font=("Helvetica",14),bg_color="Gray",text_color="White")
Label_C.place(x=70,y=250)

frame4 = customtkinter.CTkButton(root, width=30, height=30, text='D', font=("Helvetica", 14))
frame4.place(x=20,y=300)

Label_D=customtkinter.CTkLabel(root,text="",width=100,height=40,font=("Helvetica",14),bg_color="Gray",text_color="White")
Label_D.place(x=70,y=300)


#
Question_TL = customtkinter.CTkButton(root, width=30, height=30, text='Ques_TL', font=("Helvetica", 14))
Question_TL.place(x=20,y=350)

Label_QTL=customtkinter.CTkLabel(root,text="",width=100,height=40,font=("Helvetica",14),bg_color="Gray",text_color="White")
Label_QTL.place(x=120,y=350)

Question_BR = customtkinter.CTkButton(root, width=30, height=30, text='Ques_BR', font=("Helvetica", 14))
Question_BR.place(x=20,y=400)

Label_QBR=customtkinter.CTkLabel(root,text="",width=100,height=40,font=("Helvetica",14),bg_color="Gray",text_color="White")
Label_QBR.place(x=120,y=400)

#
Choice_TL = customtkinter.CTkButton(root, width=30, height=30, text='Choice_TL', font=("Helvetica", 14))
Choice_TL.place(x=220,y=150)

Label_ATL=customtkinter.CTkLabel(root,text="",width=100,height=40,font=("Helvetica",14),bg_color="Gray",text_color="White")
Label_ATL.place(x=220,y=200)

Choice_BR = customtkinter.CTkButton(root, width=30, height=30, text='Choice_BR', font=("Helvetica", 14))
Choice_BR.place(x=220,y=250)

Label_ABR=customtkinter.CTkLabel(root,text="",width=100,height=40,font=("Helvetica",14),bg_color="Gray",text_color="White")
Label_ABR.place(x=220,y=300)

SAVE = customtkinter.CTkButton(root, width=30, height=30, text='SAVE', font=("Helvetica", 14),command=save_position)
SAVE.place(x=240,y=350)

LOAD = customtkinter.CTkButton(root, width=30, height=30, text='LOAD', font=("Helvetica", 14),command=load_position)
LOAD.place(x=240,y=400)

# Gắn sự kiện click và release vào các khung
frame1.bind("<ButtonPress-1>", lambda event: frame1.configure(cursor="fleur"))
frame1.bind("<ButtonRelease-1>", create_on_release(X1, Y1, Label_A))

frame2.bind("<ButtonPress-1>", lambda event: frame2.configure(cursor="fleur"))
frame2.bind("<ButtonRelease-1>", create_on_release(X2, Y2,Label_B))

frame3.bind("<ButtonPress-1>", lambda event: frame3.configure(cursor="fleur"))
frame3.bind("<ButtonRelease-1>", create_on_release(X3, Y3,Label_C))

frame4.bind("<ButtonPress-1>", lambda event: frame4.configure(cursor="fleur"))
frame4.bind("<ButtonRelease-1>", create_on_release(X4, Y4,Label_D))

Question_TL.bind("<ButtonPress-1>", lambda event: Question_TL.configure(cursor="fleur"))
Question_TL.bind("<ButtonRelease-1>", create_on_release(Question_X_TL, Question_Y_TL,Label_QTL))

Question_BR.bind("<ButtonPress-1>", lambda event: Question_BR.configure(cursor="fleur"))
Question_BR.bind("<ButtonRelease-1>", create_on_release(Question_X_BR, Question_Y_BR,Label_QBR))

Choice_TL.bind("<ButtonPress-1>", lambda event: Choice_TL.configure(cursor="fleur"))
Choice_TL.bind("<ButtonRelease-1>", create_on_release(Choice_X_TL, Choice_Y_TL,Label_ATL))

Choice_BR.bind("<ButtonPress-1>", lambda event: Choice_BR.configure(cursor="fleur"))
Choice_BR.bind("<ButtonRelease-1>", create_on_release(Choice_X_BR, Choice_Y_BR,Label_ABR))

# Bắt đầu vòng lặp chính của Tkinter


 

Find_Answer_Button=customtkinter.CTkButton(root,text="Press Enter",command=capture,width=100,height=30,font=("Helvetica",18))
Find_Answer_Button.place(x=70,y=30)

my_label=customtkinter.CTkLabel(root,text="",width=100,height=70,font=("Helvetica",15),wraplength=300)
my_label.place(x=20,y=70)


if os.path.exists("coordinates.json"):  # Kiểm tra sự tồn tại của file
    if os.path.getsize("coordinates.json") > 0:  # Kiểm tra xem file có trống không
        with open("coordinates.json", 'r', encoding='utf-8') as file:
            load_position()
    else:
        print(f"The file {"coordinates.json"} is empty.")
            
else:
        print(f"The file {"coordinates.json"} does not exist.")
      
        
root.bind('<Return>', capture)
root.mainloop()
