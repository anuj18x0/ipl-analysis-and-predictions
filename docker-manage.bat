@echo off
REM Docker management script for IPL Analytics (Windows)

set PROJECT_NAME=ipl-analysis-and-predictions

if "%1"=="build" goto build
if "%1"=="run" goto run
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="clean" goto clean
if "%1"=="status" goto status
goto usage

:build
echo [INFO] Building Docker image for IPL Analytics...
docker build -t %PROJECT_NAME% .
echo [INFO] Docker image built successfully!
goto end

:run
echo [INFO] Starting IPL Analytics container...
docker-compose up -d
echo [INFO] Container started! Visit http://localhost:8501
goto end

:stop
echo [INFO] Stopping IPL Analytics container...
docker-compose down
echo [INFO] Container stopped!
goto end

:restart
echo [INFO] Restarting IPL Analytics container...
docker-compose down
docker-compose up -d
echo [INFO] Container restarted! Visit http://localhost:8501
goto end

:logs
echo [INFO] Showing container logs...
docker-compose logs -f ipl-analysis-and-predictions
goto end

:clean
echo [WARNING] Cleaning up Docker images and containers...
docker-compose down
docker rmi %PROJECT_NAME% 2>nul
docker system prune -f
echo [INFO] Cleanup completed!
goto end

:status
echo [INFO] Docker container status:
docker-compose ps
goto end

:usage
echo Usage: %0 {build^|run^|stop^|restart^|logs^|clean^|status}
echo.
echo Commands:
echo   build   - Build the Docker image
echo   run     - Start the container
echo   stop    - Stop the container
echo   restart - Restart the container
echo   logs    - View container logs
echo   clean   - Clean up images and containers
echo   status  - Show container status
goto end

:end
