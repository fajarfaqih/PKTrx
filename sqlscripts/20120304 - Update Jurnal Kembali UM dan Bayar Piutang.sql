-- Sebelumnya perlu di update parameter jurnal di modul transaksi

select * from transaction.transactionitem ti
where parameterjournalid='PAK-A' and 
exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.transactioncode='PXAR'
and c.fundentity = 4
and i.mutationtype = 'C'
and ti.transactionitemid=i.transactionitemid);


update transaction.transactionitem ti
set parameterjournalid='PAK-A2' where parameterjournalid='PAK-A' and 
exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.transactioncode='CAR'
and c.fundentity = 4
and i.mutationtype = 'C'
and ti.transactionitemid=i.transactionitemid);

update transaction.transactionitem ti
set parameterjournalid='PAK-A1' where parameterjournalid='PAK-A' and 
exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.transactioncode='PEAR'
and c.fundentity = 4
and i.mutationtype = 'C'
and ti.transactionitemid=i.transactionitemid);

update transaction.transactionitem ti
set parameterjournalid='PAK-A1' where parameterjournalid='PAK-A' and 
exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.transactioncode='PXAR'
and c.fundentity = 4
and i.mutationtype = 'C'
and ti.transactionitemid=i.transactionitemid);

