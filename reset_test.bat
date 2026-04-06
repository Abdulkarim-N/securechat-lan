@echo off
echo Resetting both instances...
curl -X POST http://127.0.0.1:8000/reset
curl -X POST http://127.0.0.1:8001/reset
state.handshake_complete = False
state.handshake_error = None
echo.
echo Both instances reset. Ready for new test.
pause