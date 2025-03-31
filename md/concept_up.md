## Концепция системы загрузки в postgres базу данных (The concept of a postgres database upload system)


## Структура и описание базы данных (Database structure and description).
([концепция имитации продуктивной базы данных](concept_db.md))

## Начальная инициализация (Initial initialization):

### 0. Настройка подключения к базе данных (Configuring the database connection).
Для корректной работы, в разделе: `[config.json, раздел: database_connection]`
должны быть указаны актуальные параметры для подключения к postgres базе данных.

        По умолчанию, указаны настройки для случая размещения базы с именем `household_goods_chain` на локальном PostgreSQL сервере.

### 1. Создание базы данных и ее начальное заполнение (Creating a database and its initial filling).
Принудительное пересоздание всех таблиц базы данных и их первоначальное заполнение производится
модулем `database_create.py`. Он должен быть запущен однократно, до запуска автоматизации основных этапов.

## ...
