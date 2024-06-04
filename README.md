# sport_app

## PostgreSQL pgAdmin4

скачать:
https://www.enterprisedb.com/downloads/postgres-postgresql-downloads (версия 15)

подробнее о настройке и управлении:
https://winitpro.ru/index.php/2019/10/25/ustanovka-nastrojka-postgresql-v-windows/

## Flask

Выполните в cmd для установки:
```bash       
python -m venv fproject\venv
```
Перейдите в только что созданную директорию:
```bash        
cd fproject
```    
Активируйте окружение:
```bash        
venv\scripts\activate
```    
И установите Flask:
```bash
pip install flask
```    
Активировать виртуальное окружение нужно перед каждым сеансом работы с Flask.


## Подключение к БД (попытка)

Если telnet не установлен — скачать его можно следующей командой:
```bash        
apt install telnet
```
Возможно, вам понадобятся root-права для установки утилиты. Получить их можно командой: sudo su. Конечно, вы должны знать пароль от root-пользователя.

Проверим доступность 5432 порта:
```bash
telnet 185.233.2.45 5432
```
Синтаксис команды следующий: telnet IP-адрес сервера Порт. В нашем случае IP-адрес сервера — 185.233.2.45, а порт — 5432.

Если порт доступен, telnet вернет следующую информацию:
```bash
Trying 185.233.2.45...
Connected to 185.233.2.45.
Escape character is '^]'.
```
Чтобы прервать подключение нажмите 2 раза Enter или сочетание клавиш Ctrl + Z. Теперь, когда мы убедились в доступности 5432 порта, подключимся к PostgreSQL с помощью специального PostgreSQL клиента — psql.

Скачаем psql из репозитория:
```bash
apt install psql
```
Теперь подключимся удаленно к PostgreSQL. Синтаксис команды следующий:
```bash
psql -U пользователь PostgreSQL -h IP сервера -d БД для подключения
```
В частном случае команда выглядит так:
```bash
psql -U postgres -h 185.233.2.45 -d postgres
```
Далее необходимо ввести пароль пользователя, под которым осуществляется подключения. Пароль задавался при установки PostgreSQL.

Команда вернула следующую информацию:
```bash
psql (12.7 (Ubuntu 12.7-0ubuntu0.20.04.1), server 13.3)
WARNING: psql major version 12, server major version 13.
Some psql features might not work.
Type "help" for help.

postgres=#
```
Все, мы подключились к PostgreSQL удаленно
