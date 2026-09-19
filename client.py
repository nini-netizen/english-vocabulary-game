import socket
import tkinter as tk #做GUI介面的
import threading 

# 伺服器資訊
HOST = '127.0.0.1'
PORT = 12345

client_socket = None  # 用來儲存連線的客戶端socket
time_left = 60  

# 客戶端連接伺服器
def connect_to_server():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((HOST, PORT))
        display_message("Connected to the server!\n") 
    except Exception as e:
        display_message(f"Connection failed: {e}\n")
        return

    # 接收伺服器訊息
    while True:
        msg = client_socket.recv(1024).decode()
        if msg:
            display_message(msg)
        else:
            break

# 顯示伺服器訊息
def display_message(msg):
    output_text.config(state=tk.NORMAL) 
    output_text.insert(tk.END, msg)
    output_text.config(state=tk.DISABLED) 
    output_text.yview(tk.END) 

# 玩家輸入
def handle_input():
    word = entry.get().strip().lower()  
    if word and client_socket:  # 確保連線已建立
        try:
            client_socket.send(word.encode())  # 發送輸入到server
            entry.delete(0, tk.END)
        except Exception as e:
            display_message(f"Error sending message: {e}\n")

# 開始遊戲
def on_start_button_click():
    start_button.config(state=tk.DISABLED)  #開始後關閉開始按鈕
    display_message("-------------------------------------\n")
    display_message("Game has started! Please enter a word starting with the given letter.\n")
    display_message("-------------------------------------\n")
    client_socket.send("start".encode())  # 發送開始訊號給server
    start_countdown()  # 開始倒數計時

# 倒數計時顯示
def update_countdown():
    global time_left
    if time_left > 0:
        countdown_label.config(text=str(time_left)) 
        time_left -= 1
        window.after(1000, update_countdown)  # 每秒更新一次倒數計時
    else:
        countdown_label.config(text="0")  # 當時間結束顯示 0
        submit_button.config(state=tk.DISABLED)  # 倒數結束關掉submit按鈕(不給按)
    
        # 要求顯示總成績
        client_socket.send("end_game".encode())

# 開始倒數計時
def start_countdown():
    global time_left
    time_left = 60  # 初始倒數時間
    update_countdown()  # 開始倒數

# 分隔線
def show_sp():
    display_message("-------------------------------------\n")

# 創建 GUI
window = tk.Tk()
window.title("Word Game")
window.geometry("400x600")
window.config(bg="#de75af") 

output_text = tk.Text(window, height=10, width=40, wrap=tk.WORD, state=tk.DISABLED, bg="#e0f7fa", font=("Arial", 12))
output_text.pack(pady=10)

#倒數計時顯示
countdown_label = tk.Label(window, text="60", font=("Arial", 30), width=5, height=2, relief="solid", bg="#ffcccb", fg="black")
countdown_label.pack(pady=10)  

entry = tk.Entry(window, width=40, font=("Arial", 14))
entry.pack(pady=10)

# Submit 按鈕顏色和字型
submit_button = tk.Button(window, text="Submit", command=handle_input, bg="#c173ad", fg="white", font=("Arial", 14), relief="raised", padx=10, pady=5)
submit_button.pack(pady=5)

# Start 按鈕
start_button = tk.Button(window, text="Start Game", command=on_start_button_click, bg="#E81FCA", fg="white", font=("Arial", 14), relief="raised", padx=10, pady=5)
start_button.pack(pady=5)

# 分隔線 按鈕
ranking_button = tk.Button(window, text="divider", command=show_sp, bg="#d33069", fg="white", font=("Arial", 14), relief="raised", padx=10, pady=5)
ranking_button.pack(pady=10)

# 啟動連接並處理伺服器訊息
threading.Thread(target=connect_to_server, daemon=True).start()

window.mainloop()
