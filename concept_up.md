# Концепция системы загрузки в PostgreSQL базу данных

## Начальная инициализация:

### 0. Настройка подключения к базе данных.
Для корректной работы этапа, в разделе: `[config.json, раздел: database_connection]`
должны быть указаны актуальные параметры для подключения к Postgres базе данных - по умолчанию,
указаны настройки для случая размещения базы с именем `household_goods_chain` на локальном 
PostgreSQL сервере.

### 1. Создание базы данных.
При наличии корректно созданного на сервере подключения и пустой базы данных, скрипт автоматически 
создает все таблицы в базе данных.

## Структура базы данных.

### 1. ... 
...

### 2. ...
...
