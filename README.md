# Automation easy case
## Простой проект автоматизации (The easy project of automation)

### [Постановка задачи (Assignment)](./md/main_task.md)

### Общая идея (The general idea):
Для каждого этапа моделирования пайплайна будет написан отдельный скрипт, кроме того, чтобы этап загрузки
выглядел более реалистично, создадим базу данных - упрощенную имитацию полноценной продуктивной базы данных 
торговой сети. Наполним ее минимально необходимым начальным набором данных о магазинах, товарах, сотрудниках и т.д.
Последующая загрузка "сырых" данных о продажах будет осуществляться с учетом необходимости их корректного
проецирования на структуру продуктивной базы.  

### Особенности реализации (Implementation features):
0. подготовительный этап - инициализация целевой PostgreSQL базы данных - [database concept](./md/concept_db.md)
1. этап генерации продаж(чеков) - [generation concept](./md/concept_gen.md)
2. этап загрузки в PostgreSQL базу данных - [upload concept](./md/concept_up.md)
3. настройка автоматизации / база данных: [скриншоты](./img)

### Модули подготовительного этапа (Preparatory stage modules):
- `./sql/database_create.py` - **главный модуль** этапа - создание и начальное заполнение базы данных
- `app_types.py` - модуль типов для работы с базой данных:

      DBCategory, DBDiscount, DBGoods, DBStuff, DBStore, DBCashRegister, DBReceipt, DBReceiptLine
 
### Модули этапа генерации продаж (Modules of the sales generation stage):
- `daily_sales_generator.py` - **главный модуль** этапа
- `chain_stores.py` - реализация функциональности этапа - модуль основных классов:   

      ChainStores, Store, CashRegister, Receipt, ReceiptLine, Item, Goods

- `gen_utils.py` - вспомогательные функции этапа

### Модули этапа загрузки в базу данных (Modules for the stage of uploading sales data to the database):
* `daily_sales_uploader.py` - **главный модуль** этапа 
* `./sql/summary_query.py` - вынесенный в отдельный модуль sql-запрос для формирования сводки по PostgreSQL БД

### Вспомогательные модули (Auxiliary modules)
* `logger.py` - модуль кастомизации логирования в приложении (сохранение отдельных логов каждого этапа)
* `config_py.py` - управление конфигурированием приложения с помощью возможностей `pydantic`
* `config.json` - конфигурационный `json-файл` приложения
* `pgdb.py` - расширенный интерфейс к `PostgreSQL` базе данных (на основе `psycopg2`)


### Важные папки (Important folders):
1. [Data](./data) - пример выгрузки данных о продажах (по 2-й кассе 4-го магазина)
2. [Img](./img) - скриншоты планировщиков автоматизации / таблиц(структуры) БД 
3. [SQL](./sql) - модули взаимодействия с PostgreSQL базой данных 
4. [.log](./.log) - примеры лог-файлов для каждого этапа (с уровнем логирования `DEBUG` - задается в настройках) 

### Установка (Installation)
1. Клонирование репозитория: `git clone https://github.com/Va1erCa/Automation_easy_case`
2. Создание виртуального окружения: `python -m venv venv`
3. Активация виртуального окружения: `./venv/bin/activate.ps1`
4. Установка зависимостей: `pip install -r requirements.txt`
5. Запуск: `python ./sql/database_create.py` - начальная инициализация PostgreSQL базы данных
6. Запуск: `python daily_sales_generator.py` - генерация выгрузки о продажах в торговой сети
7. Запуск: `python daily_sales_uploader.py` - загрузка данных о продажах на наш PostgresSQL-сервер
8. Для запуска автоматизации необходимо:
    -
    _(при условии успешного запуска скрипта инициализации БД `./sql/database_create.py`)_
    - для каждого основного этапа создать командные файлы (файлы сценария) включающие одну строку
    с запуском главного модуля этапа:
        - для этапа генерации продаж - вида: 
     
               <полный путь до интерпретатора python в вашем виртульном окружении>python<пробел>
               <полный путь до скрипта генерации>daily_sales_generator.py
        пример ([start_gen.bat](start_gen.bat)):
     
               D:\MyPythonProjects\Automation_easy_case\.venv\Scripts\python.exe<пробел>
               D:\MyPythonProjects\Automation_easy_case\daily_sales_generator.py
        
        - для этапа загрузки в PostgreSQL базу данных - вида: 
     
               <полный путь до интерпретатора python в вашем виртульном окружении>python<пробел>
               <полный путь до скрипта загрузки в базу>daily_sales_uploader.py   

        пример ([start_upload.bat](start_upload.bat)):
     
               D:\MyPythonProjects\Automation_easy_case\.venv\Scripts\python.exe<пробел>
               D:\MyPythonProjects\Automation_easy_case\daily_sales_uploader.py

    - в доступном вам планировщике (cron, windows scheduler и т.д.) создать задачи (для каждого этапа):
        - с действием: - `запуск соответствующего командного файла (файла сценария) из предыдущего пункта`
        - с регулярностью - `ежеднено`,
        - с временем запуска - `любым (на ваше усмотрение)`, но для этапа генерации более ранним,
        чем для этапа загрузки в базу (исходя из смысла пайплайна).  
    - сохранить задачи (и наслаждаться процессом 😎... )