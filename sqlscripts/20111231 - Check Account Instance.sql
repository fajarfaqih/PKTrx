select * from accounting.accountinstance where account_code='5530101' and 
      branch_code='001' and 
      currency_code='000';
      
select account_code, branch_code , currency_code, 
  (select count(accountinstance_id) from accounting.accountinstance e 
    where a.account_code=e.account_code and 
      b.branch_code=e.branch_code and 
      c.currency_code=e.currency_code )
from accounting.account a , accounting.branchlocation b,accounting.currency c where is_detail='T'

drop table accounting.accountinstance_check ;
create table accounting.accountinstance_check as 
select account_code, branch_code , currency_code,0 as is_exist
from accounting.account a , accounting.branchlocation b,accounting.currency c where is_detail='T';
alter table accounting.accountinstance_check owner to accounting;

update accounting.accountinstance_check a set is_exist=1 where exists(
select 1 from accounting.accountinstance e 
    where a.account_code=e.account_code and 
      a.branch_code=e.branch_code and 
      a.currency_code=e.currency_code )

select * from accounting.accountinstance_check where is_exist =0
select * from accounting.branchlocation
select *,(select count(accountinstance_id) from accounting.accountinstance e 
    where a.account_code=e.account_code and 
      a.branch_code=e.branch_code and 
      a.currency_code=e.currency_code ) from accounting.accountinstance_check a where account_code like '3%'

select count(*) from accounting.accountinstance_check where account_code like '3%'