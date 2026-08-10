UPDATE FREDObservations
SET NativeValue = NULL
WHERE TRIM(NativeValue) = ''
OR TRIM(NativeValue) = '.';