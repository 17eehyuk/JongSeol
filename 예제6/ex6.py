from flask import Flask, render_template, request
import socket, time

app = Flask(__name__)

def len16(tx):
    try:
        int(tx)
        return str(tx) + ''.join(list('!' for i in range(16-len(tx))))
    except:
        return print('잘못된 입력')

# ip주소
get_ip_addr = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
get_ip_addr.connect(("8.8.8.8", 80))
ip_addr = get_ip_addr.getsockname()[0]

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        
        rx_ctrls = request.form['led_ctrls']        # 받은 명령어
        tx_ctrls = len16(rx_ctrls)                  # 보낼 명령어


        # 옳바른 명령어인 경우에만 eps32에 전송
        if(len(tx_ctrls)==16):
            print(tx_ctrls)
            # TCP접속
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((ip_addr, 9008)) # ip주소(ipconfig IPv4 주소), 포트번호 지정
            server_socket.listen(0)     # 클라이언트의 연결요청을 기다리는 상태    
            client_socket, addr = server_socket.accept() # 연결 요청을 수락함. 길이가 2인 튜플 데이터를 가져옴
            
            # 명령 보내기
            client_socket.send(tx_ctrls.encode())      # 클라이언트에게 메세지 전송


            # ESP32 메시지1 (확인용)
            rx_msg = client_socket.recv(100) # 클라이언트로 부터 데이터를 받음. 출력되는 버퍼 사이즈. (만약 2할 경우, 2개의 데이터만 전송됨)
            print(rx_msg.decode()) # 받은 데이터를 해석함.

            # ESP 메시지2 (아두이노 결과)
            rx_msg = client_socket.recv(100) # 클라이언트로 부터 데이터를 받음. 출력되는 버퍼 사이즈. (만약 2할 경우, 2개의 데이터만 전송됨)
            print(rx_msg.decode()) # 받은 데이터를 해석함.


            server_socket.close()
        time.sleep(1)

    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)