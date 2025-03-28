# Automation easy case
## Простейший проект автоматизации (The easiest project of automation)

### [Постановка задачи (Assignment)](main_task.md)

### Особенности реализации (Implementation features):
1. этап генерации продаж(чеков) - концепция изложена в [generation concept](concept_gen.md)
2. этап загрузки в PostgreSQL базу данных - концепция изложена в [upload concept](concept_up.md)
3. настройка автоматизации / база данных: [скриншоты](./img)

### Модули этапа генерации продаж (Modules of the sales generation stage):
- `daily_sales_generator.py` - **главный модуль** этапа
- `chain_stores.py` - основные классы: `ChainStores`, `Store`, `CashRegister`, `Receipt`, `ReceiptLine`, `Item`, `Goods`
- `gen_utils.py` - вспомогательные функции этапа

### Модули этапа загрузки в базу данных (Modules for the stage of uploading sales data to the database):
* `daily_sales_uploader.py` - **главный модуль** этапа
* `./sql/database.py` - модуль инициализации базы данных 
* `pgdb.py` - класс-коннектор PostgreSQL базы данных - `Database`

### Вспомогательные модули (Auxiliary modules)
* `logger.py` - модуль кастомизации логирования в приложении
* `config_py.py` - управление конфигурированием приложения с помощью возможностей `pydantic`
* `config.json` - конфигурационный `json-файл` приложения 


### Важные папки (Important folders):
1. [Data](./data) - примеры выгрузок данных о продажах
2. [Img](./img) - скриншоты планировщиков автоматизации / таблиц(структуры) БД
3. [SQL](./sql) - модуль `database.py`, отвечающий за инициализацию БД (`DDL-команды`)
4. [.log](./.log) - примеры лог-файлов для каждого этапа (с уровнем логирования `DEBUG`) 

### Установка (Installation)
1. Клонирование репозитория: `git clone https://github.com/Va1erCa/Automation_easy_case`
2. Создание виртуального окружения: `python -m venv venv`
3. Активация виртуального окружения: `./venv/bin/activate.ps1`
4. Установка зависимостей: `pip install -r requirements.txt`
5. Запуск: `python daily_sales_generator.py` или `python daily_sales_uploader.py`
6. Для запуска автоматизации необходимо:
    -
    _(при условии корректно настроенного подключения к PostgreSQL серверу и базе данных)_
    - для каждого этапа создать командные файлы (файлы сценария) включающие одну строку
    с запуском главного модуля этапа:
        - для этапа генерации такого вида: 
     
               <полный путь до интерпретатора python в вашем виртульном окружении>python<пробел>
               <полный путь до скрипта генерации>daily_sales_generator.py
        пример ([start_gen.bat](start_gen.bat)):
     
               D:\MyPythonProjects\Automation_easy_case\.venv\Scripts\python.exe<пробел>
               D:\MyPythonProjects\Automation_easy_case\daily_sales_generator.py
        
        - для этапа загрузки в базу данных такого вида: 
     
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
    - запустить задачи (и наслаждаться процессом 😎... )