# Automation easy case
## Простейший проект автоматизации (the easiest project of automation)

### [Постановка задачи (assignment)](main_task.md)

### Особенности реализации (implementation features)
Реализованы два скрипта:
1. скрипт имитирующий выгрузку кассовых чеков торговой сети: [daily_sales_generator.py](daily_sales_generator.py) 
2. скрипт обрабатывающий выгрузку и сохраняющий все чеки в бд Postgresql: [daily_sales_uploader.py](daily_sales_uploader.py)  

Моделирование каждого дня работы торговой сети происходит согласно регламента изложенного 
в [TODO.txt](todo.txt) 

### Установка (Win)
1. Клонирование репозитория: `git clone https://github.com/Va1erCa/Pandas_bussiness_case.git`
2. Создание виртуального окружения: `python -m venv venv`
3. Активация виртуального окружения: `./venv/bin/activate.ps1`
4. Установка зависимостей: `pip install -r requirements.txt`
5. Запуск: `python pandas_pharm