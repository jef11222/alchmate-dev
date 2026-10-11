@echo off
title Update OSRS Alch Bridge Plugin
echo =======================================================
echo   Updating AlchBridgePlugin.jar for RuneLite Client
echo =======================================================
echo.

:copy_loop
set "COPIED=0"
if exist "%~dp0bridge_plugin\AlchBridgePlugin.jar" set "SRC=%~dp0bridge_plugin\AlchBridgePlugin.jar"
if not defined SRC if exist "%~dp0..\bridge_plugin\AlchBridgePlugin.jar" set "SRC=%~dp0..\bridge_plugin\AlchBridgePlugin.jar"

if exist "%USERPROFILE%\.runelite\plugins" (
    copy /Y "%SRC%" "%USERPROFILE%\.runelite\plugins\AlchBridgePlugin.jar" >nul 2>&1
    if not errorlevel 1 set "COPIED=1"
)
for /d %%D in ("%USERPROFILE%\.runelite\*plugins*") do (
    copy /Y "%SRC%" "%%D\AlchBridgePlugin.jar" >nul 2>&1
    if not errorlevel 1 set "COPIED=1"
)

if "%COPIED%"=="1" (
    echo [SUCCESS] AlchBridgePlugin.jar successfully updated!
    echo.
    echo The in-game overlay and dashboard bridge is installed.
    echo You can now launch your RuneLite client!
    echo.
    pause
    exit /b 0
)

echo [NOTICE] The game client is currently running and holding the plugin file.
echo Please close or restart the client, then press any key to finish the update...
pause >nul
goto copy_loop
