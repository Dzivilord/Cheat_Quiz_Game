# Cheat Quiz Game

This is my first spontaneous project. The program automatically solves quiz games displayed on your monitor. It uses image-to-text technology (OCR) to scan questions and matches them with answers stored in a JSON file (key-value pairs). It can search a question database of around 500 questions in under 2 seconds.

## Instructions

1. **Set Positions:**  
    Drag and drop to allocate all required positions (6 points total, or 8 in some cases depending on the layout).  
    - **A:** Choice #1  
    - **B:** Choice #2  
    - **Ques_TL:** Top-left corner of the question frame  
    - **Ques_BR:** Bottom-right corner of the question frame  
    Repeat for the frame containing four questions if needed.

2. **Get the Answer:**  
    Press `Enter` or click the "Enter here" button to retrieve the answer.

3. **Auto-Select Answer:**  
    The program will automatically move the cursor to the correct answer. This step takes about 1.5 to 2.5 seconds.

**Tips:**
- You can save all coordinates in `cordinates.json` to speed up setup next time.
- Questions not found in the database are saved temporarily in `temp.txt`. Review these and add them to `questions.json` with the correct answers.

