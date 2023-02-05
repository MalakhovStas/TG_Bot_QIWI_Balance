# ___Bot QIWI Balance___

Телеграм бот для пополнения баланса пользователя через платежную систему QIWI.
___
<a id="ceiling"></a>

### __Установка приложения:__
1. Для запуска необходимо: Python , Git
2. Для установки бота клонируйте этот репозиторий в нужную директорию 
   командой: <i><span style="color:  #228B22;"> git clone <ссылка на репозиторий> </span><i>

3. Установите зависимости из файла [requirements.txt](requirements.txt) командой: 
   <i><span style="color:  #228B22;"> pip install -r requirements.txt </span></i>

4. Создайте токен бота при помощи [BotFather](https://telegram.me/BotFather), полученный токен необходимо указать 
   в переменной [<span style="color:  #228B22;">BOT_TOKEN</span>](.env.template) файла [.env.template](.env.template) 
   вместо текста в кавычках (кавычки оставить).

5. Переменные [<span style="color:  #228B22;">ADMINS и TECH_ADMINS </span>](.env.template) в файле [.env.template](.env.template) - это список 
   id пользователей Telegram, которым будут предоставлены права администраторов вашего бота. Можно не указывать, либо указать 
   позднее, удалив текст и оставив пустые кавычки. 

6. [<span style="color:  #228B22;">QIWI_PRIV_KEY </span>](.env.template) в файле [.env.template](.env.template) - это уникальный 
   приватный токен платежной системы QIWI, подробнее -> https://qiwi.com/

7. [<span style="color:  #228B22;">PG_DATABASE </span>](.env.template) в файле [.env.template](.env.template) - настройка
   базы данных приложения. Для использования PostgeSQL необходимо изменить соответствующие данные для доступа к вашей БД 
   и убрать знак # в начале строки, или ничего не изменять, тогда будет использоваться БД SQLite, файл БД будет 
   автоматически создан в директории [<span style="color:  #228B22;">database</span>](database) 

8. Обязательно необходимо переименовать файл [.env.template](.env.template) в <i><span style="color:  #228B22;">.env
   </span></i> На этом установка завершена, запускайте файл [main.py](main.py) и пользуйтесь вашим приложением.

### __Настройка бота:__

- [config.py](config.py) - пользовательские настройки, с описанием. 

### __Структура:__
<ul><details><summary><b><i><span style="color:  #6495ED;">показать</span></i></b></summary>

[.env.template](.env.template)
   
    файл с конфиденциальной информацией (перед запуском бота, внести изменения и переименовать в .env).

[loader.py](loader.py)

    Модуль загрузки основных инструментов приложения

[main.py](main.py)

    Модуль запуска приложения с механизмом автоматического перезапуска в случае завершения программы в
    результате непредвиденной ошибки

[requirements.txt](requirements.txt)

    файл с информацией о зависимостях проекта, названием и релизом, необходимых для работы бота библиотек.

[<span style="color:  #228B22;">database</span>](database)

    Утилиты базы данных

[<span style="color:  #228B22;">handlers</span>](handlers)

    Обработчики сообщений от пользователя

[<span style="color:  #228B22;">logs</span>](logs) 

    Папка с log файлами записывающими ход исполнения скрипта проекта и регистрацией ошибок.

[<span style="color:  #228B22;">middlewares</span>](middlewares)

    предварительные обработчики сообщений от пользователя


[<span style="color:  #228B22;">utils</span>](utils)

    Папка с утилитами проекта

[наверх](#ceiling)


