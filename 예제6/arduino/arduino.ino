/*
초음파거리가 15 미만일때만
LED 제어
*/

long ultrasonic_distance(int trig, int echo)  // 초음파 거리
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

const int echo = 8;
const int trig = 9;
void setup()
{
  // LED 포트설정 4,5,6,7
  for(int i=4; i<=7; i++)
  {
    pinMode(i, OUTPUT);
  }
  pinMode(echo, INPUT);
  pinMode(trig, OUTPUT);
  
  Serial.begin(9600);
}

void loop() {
  long distance = ultrasonic_distance(trig, echo);
  if(Serial.available())    // Serial로 데이터가 들어온 경우만 실행
  {
    if(distance<15)
    {
      String rx = Serial.readString();

      for(int i=0; i<4; i++)
      { 
        if(rx[4*i]=='!'){continue;}
        int opt = 10*(100*(rx[4*i+1]-'0')+10*(rx[4*i+2]-'0')+1*(rx[4*i+3]-'0'));  //operating time
        int LED = rx[4*i] - '0';
        //LED 작동
        // LED0는 7번, LED1는 6번, LED2는 5번, LED3는 4번
        // 따라서 7-rx[4*i]를 통해서 구할수 있음
        digitalWrite(7-LED, HIGH);
        delay(opt);
        digitalWrite(7-LED, LOW);
      }
      Serial.println("Complete");
    }
    else
    {
      Serial.readString();    // 버퍼지우기(안지우면 다음 명령을 해도 그전 명령이 처리됨)
      Serial.println("Failed");
    }
  }
  
}
