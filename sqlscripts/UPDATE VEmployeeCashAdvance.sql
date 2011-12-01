select * from transaction.financialaccount where accountno like 'CA%';
select * from transaction.accountreceivable where accountno like 'PK%'

select * from public.sdm_employee a where exists(
select 1 from transaction.accountreceivable b where 
a.id=b.employeeidnumber and b.accountreceivabletype='C')

CREATE OR REPLACE VIEW "transaction".vemployeecashadvance AS 
 SELECT a.id AS employeeid, a.full_name AS employeename, a.email, a.permanent_address, a.current_phone_no, a.permanent_phone_no, a.branch_id
   FROM public.sdm_employee a where exists(
select 1 from transaction.accountreceivable b where 
a.id=b.employeeidnumber and b.accountreceivabletype='C');
alter table transaction.vemployeecashadvance owner to transaction;

CREATE OR REPLACE VIEW "transaction".vemployeeaccountreceivable AS 
 SELECT a.id AS employeeid, a.full_name AS employeename, a.email, a.permanent_address, a.current_phone_no, a.permanent_phone_no, a.branch_id
   FROM public.sdm_employee a where exists(
select 1 from transaction.accountreceivable b where 
a.id=b.employeeidnumber and b.accountreceivabletype = 'E');
alter table transaction.vemployeeaccountreceivable owner to transaction;


insert into transaction.transactiontype values('CARB','PENGEMBALIAN UANG MUKA (REIMBURSE)','KK');
insert into transaction.parameterinbox values('CARB','PENGEMBALIAN UANG MUKA (REIMBURSE)','KK','INCOME');

--insert into transaction.transactiontype values('CAB','PENGEMBALIAN UANG MUKA (REIMBURSE)','fCashAdvanceReturn','TRAN');
--insert into transaction.transactiontype values('CARR','PENGEMBALIAN UANG MUKA (RAK)','fCashAdvanceReturnRAK','TRAN');
--insert into transaction.transactiontype values('DTR','PENGEMBALIAN UANG MUKA (RAK)','fCashAdvanceReturnRAK','TRAN');
