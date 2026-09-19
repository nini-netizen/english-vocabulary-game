import socket
import threading
import random
import time
import enchant

# 遊戲設定(設定host,port number)
HOST = '127.0.0.1'
PORT = 12345
game_time = 60 

# 拼字檢查器(用python enchant)
d = enchant.Dict("en_US")

# 儲存玩家得分+輸入的字
players = {}
used_words = set()

# 用來儲存每個玩家的字母(避免給不同玩家重複的題目)
players_letters = {}

available_letters = list('abcdefghijklmnopqrstuvwxyz')

# 玩家與對應的連線 socket
players_sockets = {}

# 已經完成的玩家
players_done = set()
# 處理每個玩家的連線
def handle_client(client_socket, addr):
    print(f"New connection: {addr}")
    
    # 讓玩家輸入名字
    client_socket.send("Enter your name: ".encode())
    player_name = client_socket.recv(1024).decode().strip()
    players[player_name] = 0  # 初始化玩家分數

    # 玩家加入字典
    players_sockets[player_name] = client_socket
    client_socket.send(f"Hello, {player_name}! Please wait for the game to start...\n".encode())

    # 等待「開始遊戲」
    start_signal = client_socket.recv(1024).decode().strip()
    if start_signal == "start":
        # 隨機選擇一個字母
        if available_letters:
            letter = random.choice(available_letters)
            available_letters.remove(letter)  # 確保每個玩家有不同字母
        else:
            letter = random.choice('abcdefghijklmnopqrstuvwxyz')  # 字母池空->隨機選字母
        players_letters[player_name] = letter  # 儲存玩家的字母
        client_socket.send(f"The letter is: {letter.upper()}\n".encode())  

        # 遊戲倒數
        global game_time_left
        game_time_left = game_time

        # 開始遊戲(接收輸入+處理)
        while game_time_left > 0:
            word = client_socket.recv(1024).decode().strip().lower()  # 轉小寫
            print(f"Received word from {player_name}: {word}") 
            if not word:  
                break

            # 檢查單字
            if word.startswith(letter) and d.check(word) and word not in used_words:
                used_words.add(word)
                players[player_name] += 1
                client_socket.send(f"Good job! You scored 1 point. Your current score: {players[player_name]}\n".encode())
            else:
                client_socket.send(f"Invalid word or repeated word. Your current score: {players[player_name]}\n".encode())
            
            # 收到client的end訊息->結束遊戲
            if word == "end_game":
                print(f"End game signal received from {player_name}")
                break

    # 顯示分數
        client_socket.send(f"Game Over! Your final score: {players[player_name]}\n".encode())
     # 當玩家完成後，將該玩家標記為已完成
        players_done.add(player_name)

        # 所有玩家都完成->才會廣播
        if len(players_done) == len(players_sockets):
            broadcast_ranking()  

    while True:
        request_msg = client_socket.recv(1024).decode().strip()
        if request_msg == "request_ranking":
            broadcast_ranking(client_socket)
            break

# 廣播
def broadcast_ranking(client_socket=None):
    # 排序得分
    sorted_players = sorted(players.items(), key=lambda x: x[1], reverse=True)
    ranking_message = "------Final Rankings------\n"
    for idx, (name, score) in enumerate(sorted_players, start=1):
        ranking_message += f"{idx}. {name}: {score} points\n"
    
    print(f"{ranking_message}") 

    for player_name, client_socket in players_sockets.items():
        try:
            client_socket.send(ranking_message.encode())  # 發送排名給每個玩家
        except Exception as e:
            print(f"Error broadcasting ranking to {player_name}: {e}")
        
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#使用tcp
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print("Server started... Waiting for connections.")

    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, addr)).start()

start_server()
