@echo off

SET FUNCTION=catalog-emit-consumer

pip install -r requirements.txt -t ./

7z a -r deploy.zip *.py

aws lambda update-function-code --function-name %FUNCTION% --zip-file fileb://deploy.zip --region sa-east-1
goto fim

:sintax
@echo exemplo deploy.bat

:fim
pause