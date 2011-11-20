--###################################################################
-- create table temporary for delete account receivable
-- drop table transaction.accountdelete
create table transaction.accountdelete as select accountno,sum(d.amount),count(d.transactionitemid) from 
        transaction.accounttransactionitem c ,
        transaction.transactionitem d
       where c.transactionitemid = d.transactionitemid 
         and accountno like 'PKPU%'
       group by  accountno
       having sum(d.amount) = 0;

-- delete financialaccount
delete from transaction.financialaccount a
where balance = 0
and exists(select 1 from 
        transaction.accountdelete c
       where c.accountno=a.accountno );

-- delete accountreceivable
delete from transaction.accountreceivable a
where accountreceivabletype = 'E'
and exists(select 1 from 
        transaction.accountdelete c
       where c.accountno=a.accountno );

-- delete accounttransactionitem
delete
from transaction.accounttransactionitem a where accountno like 'PKPU%'  and not exists(select 1 from transaction.financialaccount b where a.accountno=b.accountno);

-- delete transactionitem
delete from transaction.transactionitem a where refaccountno like 'PKPU%'  and not exists(select 1 from transaction.accounttransactionitem b where a.transactionitemid=b.transactionitemid)

drop table transaction.accountdelete;

--###################################################################

select accountno,count(*) 
from transaction.accounttransactionitem a where accountno like 'PKPU%'  and not exists(select 1 from transaction.financialaccount b where a.accountno=b.accountno)
group by accountno
having count(*) > 1

select a.accountno,a.accountname
from 
  transaction.financialaccount a,
  transaction.accountreceivable b
where a.accountno = b.accountno
  and a.balance = 0
  and b.accountreceivabletype = 'E'
  and exists( 
       select 1 from 
        transaction.accountdelete c
       where c.accountno=a.accountno 
        ) 
               
select * from transaction.accounttransactionitem a where not exists(select 1 from transaction.financialaccount b where a.accountno=b.accountno)

select * from transaction.productaccount where accountno='P2030501.001.0019'

select * from transaction.projectsponsor where accountno='P2030501.001.0019'

select a.accountno,a.accountname
from 
  transaction.financialaccount a,
  transaction.accountreceivable b
where a.accountno = b.accountno
  and a.balance = 0
  and b.accountreceivabletype = 'E'
  and exists( 
       select 1 from 
        transaction.accountdelete c
       where c.accountno=a.accountno 
        ) 


select * from transaction.financialaccount where accountno='PKPU0109780';
select * from transaction.accounttransactionitem where accountno='PKPU0038125'

select * from transaction.transactionitem where transactionitemid in (76099,17505)


"PKPU0038125"
select accountno,sum(d.amount) from 
        transaction.accounttransactionitem c ,
        transaction.transactionitem d
       where c.transactionitemid = d.transactionitemid 
         and accountno='PKPU0109780'
       group by  accountno
       having sum(d.amount) < 0 

select accountno,sum(d.amount),count(d.transactionitemid) from 
        transaction.accounttransactionitem c ,
        transaction.transactionitem d
       where c.transactionitemid = d.transactionitemid 
         and accountno like 'PKPU%'
       group by  accountno
       having sum(d.amount) = 0

select * from transaction.transactionitem a
where exists(
  select 1 from 
   transaction.accounttransactionitem b
  where  b.transactionitemid=a.transactionitemid
    and accountno not in (select accountno from transaction.financialaccount c))

