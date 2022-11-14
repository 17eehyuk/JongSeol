#include <TimerOne.h>
 
void setup() 
{    
  Serial.begin(9600);
  Timer1.initialize(10000); //타이머 간격 100000us = 100ms = 0.1 sec
  Timer1.attachInterrupt( timerIsr ); // 타이머 간격대로 timerIsr 함수 실행
}
 
void loop(){
  
  while(1){Serial.println("1");}
}
 
// 인터럽트로 작동하는 함수
void timerIsr()
{
    delay(500);
    Serial.println("멈춰!");
}
