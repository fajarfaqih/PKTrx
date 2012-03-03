select * from accounting.account where 

select * from accounting.account where account_code like '533%' 

select * from accounting.accounthierarchy where fl_parentaccountcode like '533%'

select * from accounting.accounthierarchy where fl_childaccountcode like '533%'

create table accounting.convertaccount (
  old_account varchar(20) primary key, new_account varchar(20));

insert into  accounting.convertaccount values('5330201','5530201');
insert into  accounting.convertaccount values('5330301','5530301');
insert into  accounting.convertaccount values('5330401','5530401');
insert into  accounting.convertaccount values('5330501','5530501');

update accounting.accounthierarchy ah
set fl_parentaccountcode=(select new_account 
                           from accounting.convertaccount ca 
                           where ah.fl_parentaccountcode=ca.old_account)
where exists(
 select 1 from accounting.convertaccount ca 
 where ah.fl_parentaccountcode=ca.old_account);

update accounting.accounthierarchy ah
set fl_childaccountcode=(select new_account 
                           from accounting.convertaccount ca 
                           where ah.fl_childaccountcode=ca.old_account)
where exists(
 select 1 from accounting.convertaccount ca 
 where ah.fl_childaccountcode=ca.old_account); 

update accounting.account a
set account_code=(select new_account 
                           from accounting.convertaccount ca 
                           where a.account_code=ca.old_account)
where exists(
 select 1 from accounting.convertaccount ca 
 where a.account_code=ca.old_account); 

update accounting.accountinstance a
set account_code=(select new_account 
                           from accounting.convertaccount ca 
                           where a.account_code=ca.old_account)
where exists(
 select 1 from accounting.convertaccount ca 
 where a.account_code=ca.old_account); 

update accounting.journalitem a
set fl_account=(select new_account 
                           from accounting.convertaccount ca 
                           where a.fl_account=ca.old_account)
where exists(
 select 1 from accounting.convertaccount ca 
 where a.fl_account=ca.old_account); 


update accounting.cashflowmember a
set account_code=(select new_account 
                           from accounting.convertaccount ca 
                           where a.account_code=ca.old_account)
where exists(
 select 1 from accounting.convertaccount ca 
 where a.account_code=ca.old_account); 


update transaction.parameterjournalitem  a
set accountcode=(select new_account 
                           from accounting.convertaccount ca 
                           where a.accountcode=ca.old_account)
where exists(
 select 1 from accounting.convertaccount ca 
 where a.accountcode=ca.old_account);

-----------------
select * from accounting.cashflowmember

select * from transaction.transactionitem a  
where exists(
 select 1 from accounting.convertaccount ca 
 where a.accountcode=ca.old_account); 

 

 
