echo off
cd C:\StravaAPI
call C:\ProgramData\Anaconda3\Scripts\activate.bat
SET CUR_YYYY=%date:~10,4%
SET CUR_MM=%date:~4,2%
SET CUR_DD=%date:~7,2%
SET FLDT=%CUR_YYYY%%CUR_MM%%CUR_DD%
activate SocMedDash && python fitnesstracker.py > C:\StravaAPI\lofgile_%FLDT%.log


