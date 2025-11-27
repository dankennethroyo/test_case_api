@echo off
REM Quick API test for NGINX deployment
REM Tests Windows access to the API via NGINX

echo.
echo ========================================================
echo    Quick API Test - NGINX Deployment
echo ========================================================
echo.

echo Testing Windows access (localhost:8009)...
curl -s http://localhost:8009/health
echo.
echo.

echo Testing health endpoint...
curl -s http://localhost:8009/health | jq .
echo.

echo Testing models endpoint...
curl -s http://localhost:8009/models | jq .
echo.

echo.
echo ========================================================
echo    Test Complete
echo ========================================================
echo.
echo If you see JSON responses above, the API is working!
echo.
echo Access the web interfaces:
echo   Client: http://localhost:8009/client
echo   Admin:  http://localhost:8009/admin
echo.
pause
