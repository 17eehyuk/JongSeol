/*
client : PC와 통신
Serail : 아두이노와 통신
*/


#include <WiFi.h>
WiFiClient client;    // WiFiClient 를 clinet라고 정의
//const char* ssid = "iptime99"; // Your WiFi SSID
//const char* password = "dlgurwo721"; // Your WiFi Password



const char* ssid = "Note10_1500"; // Your WiFi SSID
const char* password = "dlgurwo721"; // Your WiFi Password
//const char* host = "192.168.0.4";  // ipconfig 이용해서 IPv4 주소 입력
const char* host = "3.39.94.57";  // AWS

const uint16_t port = 9008;

void setup()
{
    Serial2.begin(115200);
    /*WIFI 접속관련*/
    WiFi.mode(WIFI_STA);    // WIFI_STA : 다른공유기에서 ip주소를 받는다는 의미
    WiFi.begin(ssid, password);
    while(WiFi.waitForConnectResult() != WL_CONNECTED){}    // 연결될때까지 대기
}

void loop()
{ 
  while(!client.connect(host,port)){}   // 접속될때까지 무한루프   
  /*PC에서 명령어를 받고 아두이노에 전달*/ 
  String rx_ctrl = client.readStringUntil('\r');    // TCP 서버에서 명령어를 가져옴
  client.print(rx_ctrl + " is recieved complete");    // 파이썬에 잘 받았다고 출력
  Serial2.println(rx_ctrl);    // 아두이노에 명령 전달
  
  
  /*아두이노에서 결과를 받고 PC에 출력*/
  while (!Serial2.available()){}    // 아두이노에서 결과를 받기전까지 무한루프   // 아두이노에서 성공시 Complete 실패시 Failed
  String tx_msg = Serial2.readString();
  client.print(tx_msg);

  /*종료*/
  client.stop();
  /*버퍼 초기화*/
  if(client.available()){client.readStringUntil('\r');}
  if(Serial2.available()){Serial2.readStringUntil('\n');}

}
