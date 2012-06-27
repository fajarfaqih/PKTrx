create table transaction.migrationaccount as 
	select accountno, accountname, branchcode,currencycode
	from transaction.financialaccount 
	where financialaccounttype='R' and accountno like 'PKPU%';

alter table transaction.migrationaccount add newaccountno varchar(30);
alter table transaction.migrationaccount owner to transaction;

update transaction.migrationaccount set newaccountno=accountno || '.' || branchcode || '.' || currencycode;

select * from transaction.financialaccount a where exists(
select 1 from transaction.migrationaccount b where a.accountno = b.accountno);

update  transaction.financialaccount a set accountno= (select b.newaccountno from transaction.migrationaccount b where a.accountno = b.accountno)
where exists(
  select 1 from transaction.migrationaccount b where a.accountno = b.accountno);

update  transaction.AccountReceivable a set accountno = (select b.newaccountno from transaction.migrationaccount b where a.accountno = b.accountno)
where exists(
  select 1 from transaction.migrationaccount b where a.accountno = b.accountno);


update  transaction.Accounttransactionitem a set accountno = (select b.newaccountno from transaction.migrationaccount b where a.accountno = b.accountno)
where exists(
  select 1 from transaction.migrationaccount b where a.accountno = b.accountno);


update  transaction.transactionitem a set refaccountno = (select b.newaccountno from transaction.migrationaccount b where a.refaccountno = b.accountno)
where exists(
  select 1 from transaction.migrationaccount b where a.refaccountno = b.accountno);

update  transaction.logmergeaccount a set newaccount = (select b.newaccountno from transaction.migrationaccount b where a.newaccount = b.accountno)
where exists(
  select 1 from transaction.migrationaccount b where a.newaccount = b.accountno);



----- update akun user arafat
update  transaction.financialaccount a set accountno='PKPU0193831'
where accountno='PKPU0109262';

update  transaction.AccountReceivable a set accountno='PKPU0193831',employeeidnumber=193831
where accountno='PKPU0109262';


update  transaction.Accounttransactionitem a set accountno='PKPU0193831'
where accountno='PKPU0109262';

update  transaction.transactionitem a set refaccountno = 'PKPU0193831'
where refaccountno='PKPU0109262';


----- query daftar employee yang sudah tidak terdaftar
select employeeidnumber as EmployeeId,a.accountname as EmployeeName,a.balance,a.accountno
from transaction.financialaccount a, transaction.accountreceivable b
where a.accountno=b.accountno and b.accountreceivabletype='E'
and exists( select 1 from transaction.branch tb                          
  where tb.branchcode=a.branchcode and 
  GroupBranchCode= '001' )
and not exists( select 1 from transaction.vemployee v, transaction.branch tb
  where tb.branchid=v.branch_id 
      and tb.groupbranchcode='001'
      and v.employeeid=b.employeeidnumber)
