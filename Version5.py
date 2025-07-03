import pytesseract as tess 
tess.pytesseract.tesseract_cmd=r'Pytesseract\\tesseract.exe'
# If you are using a virtual environment (e.g., tess_env) and want to package your script as an exe with PyInstaller, activate your venv first:
# On Windows:
# > tess_env\Scripts\activate

# Then run (from your project directory):
# > pyinstaller --onefile --windowed --add-data "Pytesseract\\tesseract.exe;Pytesseract" --paths=./tess_env/Lib/site-packages D:/Auto_Answer/Version3.py

# Notes:
# - Adjust the --add-data path if your tesseract.exe is elsewhere.
# - The --paths argument helps PyInstaller find packages in your venv.
# - Use forward slashes or double backslashes in paths.
from PIL import Image 
from rapidfuzz import fuzz, process
import customtkinter 
import pyautogui as pag
import json
import os
import mss
import time

# pyinstaller --onefile --windowed --add-data "Pytesseract\\tesseract.exe;." --exclude-module numpy --exclude-module scipy --exclude-module matplotlib --exclude-module pandas --exclude-module seaborn --exclude-module scikit-learn --exclude-module tensorflow --exclude-module statsmodels --exclude-module pygame --exclude-module multiprocessing --exclude-module metadata  D:\Auto_Answer\Attempt2.py

# Tạo các biến lưu tọa độ

#pyinstaller --onefile --windowed your_script.py
#pyinstaller --onefile --windowed D:\Auto_Answer\Attempt2.py

root = customtkinter.CTk()
root.title("Drag and Drop Demo")
root.geometry("340x520")
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

CheckPoint_X=customtkinter.StringVar(value="10")
CheckPoint_Y=customtkinter.StringVar(value="20")

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

max_capture_default = 2

try:
    with open("max_capture.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        max_capture_default = int(data.get("max_capture", 2))
except Exception:
    max_capture_default = 2

max_capture_var = customtkinter.StringVar(value=str(max_capture_default))
max_capture_label = customtkinter.CTkLabel(root, text="Max Captures:", width=100, height=30, font=("Helvetica", 14))
max_capture_label.place(x=70, y=3)
max_capture_entry = customtkinter.CTkEntry(root, textvariable=max_capture_var, width=60, font=("Helvetica", 14))
max_capture_entry.place(x=180, y=3)

# Track repeated question skip count
repeat_limit = [max_capture_default]
last_question = [""]

def update_repeat_limit_from_entry(*args):
    try:
        val = int(max_capture_var.get())
        if val < 0:
            val = 0
        repeat_limit[0] = val
    except ValueError:
        repeat_limit[0] = 0

max_capture_var.trace_add("write", update_repeat_limit_from_entry)

def screenshot_fast(region):
    with mss.mss() as sct:
        sct_img = sct.grab(region)
        img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
        return img
    
import threading
def capture():
    start_time = time.time()

    # ==== Lấy tọa độ câu hỏi và lựa chọn ====
    x1 = int(Question_X_TL.get())
    y1 = int(Question_Y_TL.get())
    x2 = int(Question_X_BR.get())
    y2 = int(Question_Y_BR.get())
    width = x2 - x1
    height = y2 - y1

    X = int(Choice_X_TL.get())
    Y = int(Choice_Y_TL.get())
    WIDTH = int(Choice_X_BR.get()) - X
    HEIGHT = int(Choice_Y_BR.get()) - Y

    pos_A = pag.position(X1.get(), Y1.get())
    pos_B = pag.position(X2.get(), Y2.get())
    pos_C = pag.position(X3.get(), Y3.get())
    pos_D = pag.position(X4.get(), Y4.get())
    Choice_Position = {0: pos_A, 1: pos_B, 2: pos_C, 3: pos_D}
    checkPos = pag.position(CheckPoint_X.get(), CheckPoint_Y.get())

    # ==== Chụp ảnh ====
    t1 = time.time()
    question_img = screenshot_fast({"top": y1, "left": x1, "width": width, "height": height})
    options_img = screenshot_fast({"top": Y, "left": X, "width": WIDTH, "height": HEIGHT})
    t2 = time.time()
    print(f"Capture screenshots: {(t2 - t1)*1000:.2f} ms")

    # ==== OCR song song ====
    question_result = [None]
    options_result = [None]

    def ocr_question(img):
        question_result[0] = tess.image_to_string(img, lang='vie').strip()
        print(question_result[0])
    def ocr_options(img):
        # Try to improve number reading by using --oem 3 (LSTM), --psm 6, and a whitelist focused on digits and common symbols
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,./*+-'
        
        # Convert to black and white before OCR
        bw_img = img.convert('L').point(lambda x: 0 if x < 128 else 255, '1')
        text_bw = tess.image_to_string(bw_img, lang='en', config=custom_config)
        options_result[0] = text_bw
        print(options_result[0])

    t3 = time.time()
    q_thread = threading.Thread(target=ocr_question, args=(question_img,))
    o_thread = threading.Thread(target=ocr_options, args=(options_img,))
    q_thread.start()
    o_thread.start()
    q_thread.join()
    o_thread.join()
    t4 = time.time()
    print(f"Parallel OCR: {(t4 - t3)*1000:.2f} ms")

    Question = question_result[0]
    options_text = options_result[0]
    print("Question OCR result:", Question)
    # ==== Kiểm tra câu hỏi lặp lại ====
    if Question == last_question[0]:
        if repeat_limit[0] > 0:
            repeat_limit[0] -= 1
            max_capture_var.set(str(repeat_limit[0]))
        else:
            repeat_limit[0] -= 1
            print(f"End capture (repeat limit reached): {(time.time() - start_time)*1000:.2f} ms")
            return
    else:
        last_question[0] = Question
        repeat_limit[0] = max_capture_default - 1
        max_capture_var.set(str(repeat_limit[0]))
        if repeat_limit[0] < 0:
            print(f"End capture (negative repeat limit): {(time.time() - start_time)*1000:.2f} ms")
            return

    # ==== Fuzzy match câu hỏi ====
    t5 = time.time()
    best_key, best_ratio, _ = process.extractOne(Question, questions.keys(), scorer=fuzz.ratio)
    t6 = time.time()
    print(f"Fuzzy match question: {(t6 - t5)*1000:.2f} ms")

    if best_ratio is None or best_ratio < 80:
        with open("Temp.txt", "a", encoding='utf-8') as f:
            f.write(Question + "\n")
        my_label.configure(text="Not Found")
        print(f"End capture (not matched): {(time.time() - start_time)*1000:.2f} ms")
        return

    my_label.configure(text=questions.get(best_key))
    print("Question matched:", questions.get(best_key))
    index = best_key

    # ==== Xử lý các dòng lựa chọn ====
    t7 = time.time()
    lines = [line.strip() for line in options_text.splitlines() if line.strip() != ""]
    t8 = time.time()
    print(f"Process options text: {(t8 - t7)*1000:.2f} ms")

    # ==== Fuzzy match lựa chọn ====
    t9 = time.time()
    best_idx = -1
    best_score = 0
    for i, line in enumerate(lines):
        score = fuzz.ratio(questions.get(index), line)
        print(f"Line {i}: {line}, score: {score}")
        if score > best_score:
            best_score = score
            best_idx = i
    t10 = time.time()
    print(f"Fuzzy match options: {(t10 - t9)*1000:.2f} ms")

    # ==== Click kết quả ====
    if best_idx != -1:
        pag.click(Choice_Position.get(best_idx))
        pag.click(checkPos)

    print(f"✅ Capture done in {(time.time() - start_time)*1000:.2f} ms\n")
    

    
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
        "Choice_Y_BR": Choice_Y_BR.get(),
        
        "CheckPoint_X": CheckPoint_X.get(),
        "CheckPoint_Y": CheckPoint_Y.get()
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
        
        CheckPoint_X.set(coordinates["CheckPoint_X"])
        CheckPoint_Y.set(coordinates["CheckPoint_Y"])
        
        
        Label_A.configure(text=f"X: {X1.get()}, Y: {Y1.get()}")
        Label_B.configure(text=f"X: {X2.get()}, Y: {Y2.get()}")
        Label_C.configure(text=f"X: {X3.get()}, Y: {Y3.get()}")
        Label_D.configure(text=f"X: {X4.get()}, Y: {Y4.get()}")
        
        Label_QTL.configure(text=f"X: {Question_X_TL.get()}, Y: {Question_Y_TL.get()}")
        Label_QBR.configure(text=f"X: {Question_X_BR.get()}, Y: {Question_Y_BR.get()}")
        
        Label_ATL.configure(text=f"X: {Choice_X_TL.get()}, Y: {Choice_Y_TL.get()}")
        Label_ABR.configure(text=f"X: {Choice_X_BR.get()}, Y: {Choice_Y_BR.get()}")
        
        CheckPoint_Label.configure(text=f"X: {CheckPoint_X.get()}, Y: {CheckPoint_Y.get()}")
    except FileNotFoundError:
        #print("File not found. Make sure you have saved coordinates before loading.")
        pass

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

frame5 = customtkinter.CTkButton(root, width=30, height=30, text='Check Point', font=("Helvetica", 14))
frame5.place(x=20,y=450)

CheckPoint_Label=customtkinter.CTkLabel(root,text="",width=100,height=40,font=("Helvetica",14),bg_color="Gray",text_color="White")
CheckPoint_Label.place(x=120,y=450)

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

frame5.bind("<ButtonPress-1>", lambda event: frame5.configure(cursor="fleur"))
frame5.bind("<ButtonRelease-1>", create_on_release(CheckPoint_X, CheckPoint_Y,CheckPoint_Label))

# Bắt đầu vòng lặp chính của Tkinter

# Add a variable to track lock state
buttons_locked = [False]  # Use a mutable type to allow modification inside functions

def lock_buttons():
    if not buttons_locked[0]:
        # Disable all buttons except Find_Answer_Button and Lock_Button
        for btn in [
            frame1, frame2, frame3, frame4, Question_TL, Question_BR,
            Choice_TL, Choice_BR, SAVE, LOAD, frame5
        ]:
            btn.configure(state="disabled", fg_color="gray")
            btn._state = "disabled"  # Ensure underlying state is set
            btn._draw()  # Force redraw if needed
            btn.unbind("<ButtonPress-1>")
            btn.unbind("<ButtonRelease-1>")
        for lbl in [
            Label_A, Label_B, Label_C, Label_D, Label_QTL, Label_QBR,
            Label_ATL, Label_ABR, CheckPoint_Label
        ]:
            lbl.configure(bg_color="gray")
        Lock_Button.configure(text="Unlock All")
        buttons_locked[0] = True
    else:
        # Enable all buttons and restore their original color
        for btn, press, release in [
            (frame1, lambda _: frame1.configure(cursor="fleur"), create_on_release(X1, Y1, Label_A)),
            (frame2, lambda _: frame2.configure(cursor="fleur"), create_on_release(X2, Y2, Label_B)),
            (frame3, lambda _: frame3.configure(cursor="fleur"), create_on_release(X3, Y3, Label_C)),
            (frame4, lambda _: frame4.configure(cursor="fleur"), create_on_release(X4, Y4, Label_D)),
            (Question_TL, lambda _: Question_TL.configure(cursor="fleur"), create_on_release(Question_X_TL, Question_Y_TL, Label_QTL)),
            (Question_BR, lambda _: Question_BR.configure(cursor="fleur"), create_on_release(Question_X_BR, Question_Y_BR, Label_QBR)),
            (Choice_TL, lambda _: Choice_TL.configure(cursor="fleur"), create_on_release(Choice_X_TL, Choice_Y_TL, Label_ATL)),
            (Choice_BR, lambda _: Choice_BR.configure(cursor="fleur"), create_on_release(Choice_X_BR, Choice_Y_BR, Label_ABR)),
            (frame5, lambda _: frame5.configure(cursor="fleur"), create_on_release(CheckPoint_X, CheckPoint_Y, CheckPoint_Label)),
        ]:
            btn.configure(state="normal", fg_color='#2C3E50')
            btn._state = "normal"
            btn._draw()
            btn.bind("<ButtonPress-1>", press)
            btn.bind("<ButtonRelease-1>", release)
        # Enable SAVE and LOAD buttons
        SAVE.configure(state="normal", fg_color='#2C3E50', command=save_position)
        SAVE._state = "normal"
        SAVE._draw()
        SAVE.bind("<ButtonPress-1>", lambda event: SAVE.configure(cursor="hand2"))
        SAVE.bind("<ButtonRelease-1>", lambda event: save_position())

        LOAD.configure(state="normal", fg_color='#2C3E50', command=load_position)
        LOAD._state = "normal"
        LOAD._draw()
        LOAD.bind("<ButtonPress-1>", lambda event: LOAD.configure(cursor="hand2"))
        LOAD.bind("<ButtonRelease-1>", lambda event: load_position())

        for lbl in [
            Label_A, Label_B, Label_C, Label_D, Label_QTL, Label_QBR,
            Label_ATL, Label_ABR, CheckPoint_Label
        ]:
            lbl.configure(bg_color="Gray")
        Lock_Button.configure(text="Lock All")
        buttons_locked[0] = False

Lock_Button = customtkinter.CTkButton(
    root, text="Lock All", command=lock_buttons, width=100, height=30, font=("Helvetica", 16)
)
Lock_Button.place(x=180, y=30)
 

Find_Answer_Button=customtkinter.CTkButton(root,text="Press Enter",command=capture,width=100,height=30,font=("Helvetica",18))
Find_Answer_Button.place(x=70,y=30)

my_label=customtkinter.CTkLabel(root,text="",width=100,height=70,font=("Helvetica",15),wraplength=300)
my_label.place(x=20,y=70)


if os.path.exists("coordinates.json"):  # Kiểm tra sự tồn tại của file
    if os.path.getsize("coordinates.json") > 0:  # Kiểm tra xem file có trống không
        with open("coordinates.json", 'r', encoding='utf-8') as file:
            load_position()
    else:
        #print(f"The file {"coordinates.json"} is empty.")
        pass
            
else:
        #print(f"The file {"coordinates.json"} does not exist.")
        pass
      
root.bind('<Return>', lambda event: capture())
root.mainloop()
