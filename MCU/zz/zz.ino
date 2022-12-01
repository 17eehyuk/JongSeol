/*
초음파거리가 15 미만일때만
LED 제어
*/

#include <DHT.h>

#define dhtpin A1
#define dhttype DHT11
DHT dht(dhtpin, dhttype);
int Peltier  = 8;


const int echo = 13;
const int trig = 12;
long ultrasonic_distance();
void setup()
{
  // LED 포트설정 4,5,6,7
  for(int i=4; i<=7; i++)
  {
    pinMode(i, OUTPUT);
    digitalWrite(i, HIGH);
  }
  pinMode(echo, INPUT);
  pinMode(trig, OUTPUT);

  
  pinMode(Peltier, OUTPUT);
  digitalWrite(Peltier, HIGH);
  dht.begin();

  Serial.begin(115200);   // 모니터
  Serial3.begin(115200);
}

//before : 음료 제작 전
//after : 음료 제작 후

void loop()
{
  long distance_before = ultrasonic_distance();
  int temp = dht.readTemperature();
  Serial.println(temp);
  if(temp<18)
  {
    digitalWrite(Peltier, HIGH);
  }
  else
  {
    digitalWrite(Peltier, LOW);
  }
  
  
  //Serial.println(distance_before);
  
  
  if(Serial3.available())    // Serial3로 데이터가 들어온 경우만 실행
  {
    String rx = Serial3.readString();

    if(rx[0]=='S' && rx[1]=='T')
    {
      digitalWrite(Peltier, HIGH);
      if(distance_before<10)
      {
        Serial.println(rx);   // 모니터
        Serial.println(distance_before);    // 모니터
  
        for(int i=0; i<4; i++)
        { 
          if(rx[4*i+2]=='!'){continue;}
          int opt = 10*(100*(rx[4*i+3]-'0')+10*(rx[4*i+4]-'0')+1*(rx[4*i+5]-'0'));  //operating time
          int LED = rx[4*i+2] - '0';
          //LED 작동
          // LED0는 7번, LED1는 6번, LED2는 5번, LED3는 4번
          // 따라서 7-rx[4*i]를 통해서 구할수 있음
          digitalWrite(7-LED, LOW);
          delay(opt);
          digitalWrite(7-LED, HIGH);
        }
        while(1)   // 컵가져가기전까지 무한루프 0.5초마다 갱신
        {
          long distance_after = ultrasonic_distance();
          if(distance_after>10){break;}   // 15초과(컵가져간상태)
          delay(500);
        }
        Serial3.println("Complete");
        Serial.println("Complete");   // 모니터
      }
      else
      {
        Serial3.println("Failed");
        Serial.println("Failed");   // 모니터
      }



      
    }
    
    
    
  }
  
}

long ultrasonic_distance()  // 초음파 거리
{
  long duration, distance;
  digitalWrite(trig, LOW);
  delayMicroseconds(2);
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);

  duration = pulseIn(echo, HIGH);   // 시간
  distance = duration*17/1000;      // 거리

  return distance;
}
