echo off
echo "Replacing the old access token..."
SETX /S LAPTOP-P3PTPJS9 ACCESS_TOKEN /f dat /a 0,1
echo "Replacing the expiration time of the token..."
SETX /S LAPTOP-P3PTPJS9 EXPIRES_AT /f dat /a 1,1
echo "Removing the source file..."
rem del /f dat
echo "Success!"