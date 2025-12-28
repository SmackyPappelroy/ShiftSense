FOR i := 1 TO 500 DO
    ArrayData[i] := i * 2;
END_FOR;

CASE State OF
    1: MotorStart := TRUE;
    2: MotorStart := FALSE;
END_CASE;
