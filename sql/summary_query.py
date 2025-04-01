# A module for a large SQL query text of summary information.

SUMMARY_QUERY = '''
--Summary info
select 
    0 as line,
    'total_dates_in_database' as rep_param_name, 
    count(distinct date(r.receipt_time)) as rep_param_value
from receipt r
union
select 
    1 as line,
    'total_stores' as rep_param_name, 
    count(*) as rep_param_value
from store s
union
select 
    2 as line,
    'total_cash_registers' as rep_param_name, 
    count(*) as rep_param_value 
from cash_register cr
union
select 
    3 as line,
    'total_employees' as rep_param_name, 
    count(*) as rep_param_value 
from stuff s
union
select 
    4 as line,
    'total_receipts' as rep_param_name, 
    count(distinct r.id) as rep_param_value 
from receipt r 
union
select 
    5 as line,
    'total_receipt_lines' as rep_param_name, 
    count(*) as rep_param_value
from receipt_line rl 
union
select 
    6 as line,
    'total_amount_items' as rep_param_name, 
    sum(rl.amount) as rep_param_value
from receipt_line rl 
union
select 
    7 as line,
    'total_revenue' as rep_param_name, 
    sum(rl.amount * g.price) as rep_param_value
from receipt_line rl 
left join goods g 
on rl.id_item = g.id 
order by line
'''
