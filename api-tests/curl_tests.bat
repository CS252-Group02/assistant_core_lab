@echo off
setlocal
rem Run with the API server already running. Override BASE_URL and API_ADMIN_KEY as needed.
rem The valid feedback request adds one in-memory record.
if not defined BASE_URL set "BASE_URL=http://127.0.0.1:8000"
if "%BASE_URL:~-1%"=="/" set "BASE_URL=%BASE_URL:~0,-1%"

echo == health (expect 200)
curl.exe --silent --show-error --connect-timeout 5 --max-time 20 --write-out " [%%{http_code}]\n" -X GET "%BASE_URL%/health"

echo == chat empty (expect 422)
curl.exe --silent --show-error --connect-timeout 5 --max-time 20 --write-out " [%%{http_code}]\n" -X POST "%BASE_URL%/v1/chat" -H "Content-Type: application/json" --data-raw "{\"message\":\"\"}"

echo == chat missing message (expect 422)
curl.exe --silent --show-error --connect-timeout 5 --max-time 20 --write-out " [%%{http_code}]\n" -X POST "%BASE_URL%/v1/chat" -H "Content-Type: application/json" --data-raw "{}"

echo == chat greeting (expect 200)
curl.exe --silent --show-error --connect-timeout 5 --max-time 20 --write-out " [%%{http_code}]\n" -X POST "%BASE_URL%/v1/chat" -H "Content-Type: application/json" --data-raw "{\"message\":\"hello\"}"

echo == chat tuition (expect 200)
curl.exe --silent --show-error --connect-timeout 5 --max-time 20 --write-out " [%%{http_code}]\n" -X POST "%BASE_URL%/v1/chat" -H "Content-Type: application/json" --data-raw "{\"message\":\"tuition for 18 credits and 2 retake\"}"

echo == chat office (expect 200)
curl.exe --silent --show-error --connect-timeout 5 --max-time 20 --write-out " [%%{http_code}]\n" -X POST "%BASE_URL%/v1/chat" -H "Content-Type: application/json" --data-raw "{\"message\":\"where is the library\"}"

echo == chat handbook (expect 200)
curl.exe --silent --show-error --connect-timeout 5 --max-time 20 --write-out " [%%{http_code}]\n" -X POST "%BASE_URL%/v1/chat" -H "Content-Type: application/json" --data-raw "{\"message\":\"thesis registration credits\"}"

echo == chat unknown (expect 200)
curl.exe --silent --show-error --connect-timeout 5 --max-time 20 --write-out " [%%{http_code}]\n" -X POST "%BASE_URL%/v1/chat" -H "Content-Type: application/json" --data-raw "{\"message\":\"xyzzy\"}"

echo == feedback valid (expect 201)
curl.exe --silent --show-error --connect-timeout 5 --max-time 20 --write-out " [%%{http_code}]\n" -X POST "%BASE_URL%/v1/feedback" -H "Content-Type: application/json" --data-raw "{\"request_id\":\"curl-contract-test\",\"rating\":1,\"comment\":\"curl contract check\"}"

echo == feedback invalid rating (expect 422)
curl.exe --silent --show-error --connect-timeout 5 --max-time 20 --write-out " [%%{http_code}]\n" -X POST "%BASE_URL%/v1/feedback" -H "Content-Type: application/json" --data-raw "{\"request_id\":\"curl-contract-test\",\"rating\":2}"

echo == feedback missing request_id (expect 422)
curl.exe --silent --show-error --connect-timeout 5 --max-time 20 --write-out " [%%{http_code}]\n" -X POST "%BASE_URL%/v1/feedback" -H "Content-Type: application/json" --data-raw "{\"rating\":1}"

echo == feedback without admin key (expect 401)
curl.exe --silent --show-error --connect-timeout 5 --max-time 20 --write-out " [%%{http_code}]\n" -X GET "%BASE_URL%/v1/feedback"

if not defined API_ADMIN_KEY goto skip_admin
echo == feedback with admin key (expect 200)
curl.exe --silent --show-error --connect-timeout 5 --max-time 20 --write-out " [%%{http_code}]\n" "%BASE_URL%/v1/feedback" -H "X-API-Key: %API_ADMIN_KEY%"
goto weather
:skip_admin
echo == feedback with admin key (skipped: set API_ADMIN_KEY to the server key)

:weather
echo == weather (expect 200 or 503 if upstream unavailable)
curl.exe --silent --show-error --connect-timeout 5 --max-time 20 --write-out " [%%{http_code}]\n" "%BASE_URL%/v1/weather"
endlocal

pause