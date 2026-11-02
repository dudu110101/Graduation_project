#include <Servo.h>


// ============================================================
// Servo objects
// ============================================================

Servo servo1;
Servo servo2;
Servo servo3;


// ============================================================
// Servo pins
// ============================================================

const int SERVO1_PIN = 9;
const int SERVO2_PIN = 10;
const int SERVO3_PIN = 11;


// ============================================================
// Normal position
// ============================================================

const int NORMAL_ANGLE = 90;


// ============================================================
// Setup
// ============================================================

void setup()
{
    Serial.begin(9600);

    servo1.attach(SERVO1_PIN);
    servo2.attach(SERVO2_PIN);
    servo3.attach(SERVO3_PIN);

    // 초기 위치
    servo1.write(NORMAL_ANGLE);
    servo2.write(NORMAL_ANGLE);
    servo3.write(NORMAL_ANGLE);

    delay(500);
}


// ============================================================
// Main loop
// ============================================================

void loop()
{
    if (Serial.available() > 0)
    {
        String command =
            Serial.readStringUntil('\n');

        command.trim();

        command.toUpperCase();


        // ----------------------------------------------------
        // Bent
        // ----------------------------------------------------

        if (command == "BENT")
        {
            servo1.write(30);
            servo2.write(90);
            servo3.write(90);
        }


        // ----------------------------------------------------
        // Missing
        // ----------------------------------------------------

        else if (command == "MISSING")
        {
            servo1.write(90);
            servo2.write(0);
            servo3.write(90);
        }


        // ----------------------------------------------------
        // Solder defect
        // ----------------------------------------------------

        else if (command == "SOLDER")
        {
            servo1.write(90);
            servo2.write(90);
            servo3.write(0);
        }


        // ----------------------------------------------------
        // Good
        // ----------------------------------------------------

        else if (command == "GOOD")
        {
            servo1.write(90);
            servo2.write(90);
            servo3.write(90);
        }
    }
}