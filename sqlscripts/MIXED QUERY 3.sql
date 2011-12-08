select * from transaction.transactiontype where transactioncode not in
(select kodeinbox from transaction.parameterinbox)



select * from transaction.budgettransaction

select distinct t.actualdate ,t.transactiondate, t.transactioncode,a.*
from transaction.transactionitem a ,
transaction.transaction t where a.transactionid = t.transactionid and exists(
select 1 from transaction.budgettransaction b where 
a.transactionitemid = b.transactionitemid and budgettranstype is null)

update transaction.budgettransaction set budgettranstype='A' where budgettranstype is null

insert into transaction.parameterinbox values('CARR','PENGEMBALIAN UANG MUKA (RAK)','fCashAdvanceReturnRAK','INCOME');
insert into transaction.parameterinbox values('DTR','PENGEMBALIAN DANA ANTAR CABANG','fBranchDistributionReturn','INCOME');
"DTR"

select * from transaction.transactiontype where transactioncode = 'INVC'

select * from transaction.transaction where transactioncode ='DTR'