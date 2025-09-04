void setup() {
  // Start the serial communication at 9600 baud rate
  Serial.begin(115200);

  // Give the serial port time to initialize
  delay(1000);
  
  // Print the required line
  Serial.println("T, 1178370, SR, 144, SF, 0, T1R, 17.75, T1A, 17.00, T1F, 1, T2R, 18.25, T2A, 18.00, T2F, 0, P1, 4.626, P1V, 2.202, P1F, 0, P2, 0.003, P2V, 1.892, P2F, 0, IgR, 0");
}

void loop() {
  Serial.println("T, 1178370, SR, 144, SF, 0, T1R, 17.75, T1A, 17.00, T1F, 1, T2R, 18.25, T2A, 18.00, T2F, 0, P1, 4.626, P1V, 2.202, P1F, 0, P2, 0.003, P2V, 1.892, P2F, 0, IgR, 0");
  delay(1000);
}

