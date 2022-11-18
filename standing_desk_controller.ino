#include "Adafruit_VL53L0X.h"


Adafruit_VL53L0X lox = Adafruit_VL53L0X();
const int greenPin =  3;  //UP
const int whitePin =  4; //Down


void setup() {
  Serial.begin(115200);
  for(int i=11; i < 22; i++) {
    if(i ==  18 || i ==  19){
      //skip
    }
    else {
      digitalWrite(i, LOW);
    }
  }

  // wait until serial port opens for native USB devices
  while (! Serial) {
    delay(1);
  }
  
  if (!lox.begin()) {
    Serial.println("SFailed to boot VL53L0X");
    while(1);
  }
  Serial.println("SReady");
}

void loop() {
  while (Serial.available() == 0) {
  }
  int menuChoice = 0;
  float tableHeight=0.0, height=0.0;
  float x = Serial.parseFloat();
  //Serial.println(x);
  //Serial.println(menuChoice);
  if (x > 100.00 && x < 200.00) {
    height = x - 100.00;
    menuChoice = 1;
  } else if (x > 200.00 && x < 300.00) {
    height = x - 200.00;
    menuChoice = 2;
  } else if (x > 700.00 && x < 800.00) {
    height = x - 700.00;
    menuChoice = 3;
  } else if (x == 888.00) {
    menuChoice = 4;
  }
    
  switch (menuChoice) {
    case 1://Up
      tableHeight = readTableRange();
      //Serial.print("Height"); Serial.println(height);
      if (tableHeight < height) {
        Serial.println("Table is raising");
        while (height > tableHeight) {
         Serial.println("Up Loop");
         tableHeight = readTableRange();
         Serial.println(tableHeight);
         tableUp();
         float doneFlag = lookForBreak();
         if (doneFlag == 555.00) {
          Serial.println("SAbort");
          tableStop();
          break;
         }
        }
        Serial.print("H");Serial.println(tableHeight);
        tableStop();
      }
      break;

    case 2://Down
      tableHeight = readTableRange();
      //Serial.print("Height"); Serial.println(height);
      if (tableHeight > height) {
        Serial.println("Table is lowering");
        while (height < tableHeight) {
         Serial.println("Low Loop");
         tableHeight = readTableRange();
         Serial.println(tableHeight);
         tableDown();
         float doneFlag = lookForBreak();
         if (doneFlag == 555.00) {
          Serial.println("SAbort");
          tableStop();
          break;
         }
        }
        Serial.print("H");Serial.println(tableHeight);
        tableStop();
      }
      break;

    case 3:
      //Serial.print("Height"); Serial.println(height);
      tableHeight = readTableRange();
      if (tableHeight < height) {//@Height UP
        Serial.println("Table is raising");
        while (height > tableHeight) {
          tableHeight = readTableRange();
          tableUp();
          float doneFlag = lookForBreak();
          if (doneFlag == 555.00) {
            Serial.println("SAbort");
            tableStop();
            break;
          }
        }
        Serial.print("H");Serial.println(tableHeight);
        tableStop();
      } else if (tableHeight > height) {//@Height Down
        Serial.println("Table is lowering");
        tableHeight = readTableRange();
        while (height < tableHeight) {
          tableHeight = readTableRange();
          tableUp();
          float doneFlag = lookForBreak();
          if (doneFlag == 555.00) {
            Serial.println("SAbort");
            tableStop();
            break;
          }
        }
        Serial.print("H");Serial.println(tableHeight);
        tableStop();
      }
      break;

    case 4:
      tableHeight = readTableRange();
      Serial.print("H");Serial.println(tableHeight);
      break;
  }
}

float readTableRange() {
  VL53L0X_RangingMeasurementData_t measure;
  float Samples=0.0, AvgRange=0.0, rangeInch=0.0;
  Serial.print("Reading a measurement... ");
  lox.rangingTest(&measure, false); // pass in 'true' to get debug data printout!
  if (measure.RangeStatus != 4) {  // phase failures have incorrect data
    for (int x = 0; x < 25; x++){
      Samples = Samples + measure.RangeMilliMeter;
      delay(1);
    }
    AvgRange=Samples/25.0;
    rangeInch = AvgRange / 25.4;
    return rangeInch;
  } else {
    Serial.println("Sout of range");
    return rangeInch;
  }
}

void tableUp() {
  digitalWrite(whitePin, LOW);
  digitalWrite(greenPin, HIGH);
}

void tableDown() {
  digitalWrite(whitePin, HIGH);
  digitalWrite(greenPin, LOW);
}

void tableStop() {
  digitalWrite(greenPin, LOW);
  digitalWrite(whitePin, LOW);  
}

float lookForBreak() {
  float z = 0.00;
  if (Serial.available() != 0) {
     z = Serial.parseFloat();
    return z;
  }
}
