#include<stdio.h>

int distance_before;
int distance_after;



if(distance_before<15)
    {
      while(1)   // 컵가져가기전까지 무한루프 0.5초마다 갱신
      {
        long distance_after = ultrasonic_distance();
        if(distance_after>15){break;}   // 15초과(컵가져간상태)
        delay(500);
      }
      Serial.println("Complete");
    }
else
{
    Serial.println("Failed");
}