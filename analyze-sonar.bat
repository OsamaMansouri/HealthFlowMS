@echo off
REM HealthFlow-MS SonarQube Analysis Script for Windows

echo ================================================
echo   HealthFlow-MS SonarQube Analysis
echo ================================================
echo.

set SONAR_TOKEN=sqp_8d2e8b0475536945fc30c926462a1efe9ed1c37a
set PROJECT_DIR=c:\Users\Dark\Desktop\5iir\HealthFlowMS

echo Analyzing Score API...
docker run --rm --network=healthflowms_default -v "%PROJECT_DIR%\score-api:/usr/src" sonarsource/sonar-scanner-cli -Dsonar.login=%SONAR_TOKEN% -Dsonar.host.url=http://sonarqube:9000

echo.
echo Analyzing DeID Service...
docker run --rm --network=healthflowms_default -v "%PROJECT_DIR%\deid:/usr/src" sonarsource/sonar-scanner-cli -Dsonar.login=%SONAR_TOKEN% -Dsonar.host.url=http://sonarqube:9000

echo.
echo Analyzing Featurizer...
docker run --rm --network=healthflowms_default -v "%PROJECT_DIR%\featurizer:/usr/src" sonarsource/sonar-scanner-cli -Dsonar.login=%SONAR_TOKEN% -Dsonar.host.url=http://sonarqube:9000

echo.
echo Analyzing Model Risque...
docker run --rm --network=healthflowms_default -v "%PROJECT_DIR%\model-risque:/usr/src" sonarsource/sonar-scanner-cli -Dsonar.login=%SONAR_TOKEN% -Dsonar.host.url=http://sonarqube:9000

echo.
echo Analyzing Audit Fairness...
docker run --rm --network=healthflowms_default -v "%PROJECT_DIR%\audit-fairness:/usr/src" sonarsource/sonar-scanner-cli -Dsonar.login=%SONAR_TOKEN% -Dsonar.host.url=http://sonarqube:9000

echo.
echo ================================================
echo   Analysis Complete!
echo ================================================
echo View results at: http://localhost:9000
echo.
pause
