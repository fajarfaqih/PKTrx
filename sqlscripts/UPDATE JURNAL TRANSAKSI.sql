select c.branchcode,transactiondate, inputer, a.amount, c.description
from transaction.transactionitem a, transaction.accounttransactionitem b, transaction.transaction c
where a.transactionitemid = b.transactionitemid 
  and a.transactionid = c.transactionid
  and accounttitype='D' 
  and a.mutationtype='D'
  and c.branchcode = '103';


select count(*) from transaction.transactionitem a where exists
(select 1 
  from transaction.accounttransactionitem b 
  where a.transactionitemid=b.transactionitemid
     and accounttitype='D'
     and percentageofamil = 0
) ;

update transaction.transactionitem a set parameterjournalid='10' where exists
(select 1 
  from transaction.accounttransactionitem b 
  where a.transactionitemid=b.transactionitemid
     and accounttitype='D'
     and percentageofamil = 0
);

update transaction.transactionitem a set parameterjournalid='C10Z' where exists
(select 1 
  from transaction.accounttransactionitem b 
  where a.transactionitemid=b.transactionitemid
     and accounttitype='D'
     and percentageofamil > 0
     and fundentity = 1
);

select * from transaction.transactionitem a where exists
(select 1 
  from transaction.accounttransactionitem b 
  where a.transactionitemid=b.transactionitemid
     and accounttitype='D'
     and percentageofamil > 0
     and fundentity = 1
) and parameterjournalid <> 'C10Z' ;

update transaction.transactionitem a set parameterjournalid='C10I' where exists
(select 1 
  from transaction.accounttransactionitem b 
  where a.transactionitemid=b.transactionitemid
     and accounttitype='D'
     and percentageofamil > 0
     and fundentity = 2
);

update transaction.transactionitem a set parameterjournalid='C10W' where exists
(select 1 
  from transaction.accounttransactionitem b 
  where a.transactionitemid=b.transactionitemid
     and accounttitype='D'
     and percentageofamil > 0
     and fundentity = 3
);

update transaction.transactionitem a set parameterjournalid='10' where exists
(select 1 
  from transaction.accounttransactionitem b 
  where a.transactionitemid=b.transactionitemid
     and accounttitype='D'
     and fundentity = 5
);

select count(*) from transaction.transactionitem a where exists
(select 1 
  from transaction.accounttransactionitem b 
  where a.transactionitemid=b.transactionitemid
     and accounttitype='D'
     and fundentity = 4
) ;

select * from transaction.transactionitem a where exists
(select 1 
  from transaction.accounttransactionitem b 
  where a.transactionitemid=b.transactionitemid
     and accounttitype='D'
     and fundentity = 5
     and percentageofamil > 0
) ;

select c.branchcode,transactiondate, inputer, a.amount, c.description, b.percentageofamil
from transaction.transactionitem a, transaction.accounttransactionitem b, transaction.transaction c
where a.transactionitemid = b.transactionitemid 
  and a.transactionid = c.transactionid
  and accounttitype='D'

select * from transaction.transactionitem where parameterjournalid='C10I' order by transactionitemid desc limit 1

