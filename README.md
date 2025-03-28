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
* `daily_sales_uploader.py` - **главный модуль** 


### Важные папки (Important folders):
1. [Data](./data) - примеры выгрузок данных о продажах
2. [Img](./img) - скриншоты планировщиков автоматизации / таблиц(структуры) БД
3. [SQL](./sql) - модуль `database.py`, отвечающий за инициализацию БД (`DDL-команды`)

### Установка (Installation)
1. Клонирование репозитория: `git clone https://github.com/Va1erCa/Automation_easy_case`
2. Создание виртуального окружения: `python -m venv venv`
3. Активация виртуального окружения: `./venv/bin/activate.ps1`
4. Установка зависимостей: `pip install -r requirements.txt`
5. Запуск: `python automation_easy_case`