# RabotaYkt-bot
**Для работы бота необходимо:**
1. Установить Python 3.12.3
2. Установить библиотеки из requierments.txt
3. Скачать Docker Dekstop и прописать ``` docker-compose -d up ```
4. Запустить bot.py (Токен бота заранее прописан напрямую)

**Доступ к просмотру БД через веб pgAdmin**

Доступ к pgAdmin осуществляется по localhost:8080, данные задаются в .env

Адрес сервера в pgAdmin: postgres

Name: lorabot

Password: lorabot

**Ссылки**

Репрозиторий метрик и бд: https://github.com/aleksspevak/lorabot/tree/main

**Примечания**

Если при запуске возникает ошибка подключения к БД, помогает освобождение порта 5432 от старой версии Postgres

Если БД уже была запущена ранее, то сначало необходимо прописать 
``` docker -v down ``` и удалить папку database, а затем снова 
```
docker-compose -d up
```
