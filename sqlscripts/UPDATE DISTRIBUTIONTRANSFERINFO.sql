alter table transaction.distributiontransferinfo add transactionitemid integer;
alter table transaction.distributiontransferinfo add cashaccountnosource varchar(30);
alter table transaction.distributiontransferinfo add cashaccountnodest varchar(30);

create table transaction.refupdatedtisource as 
select transactionid, accountno 
from transaction.transactionitem a, transaction.accounttransactionitem c
where exists(
  select 1 from transaction.distributiontransferinfo b 
  where a.transactionid = b.transactionid) 
  and a.transactionitemid=c.transactionitemid
  and mutationtype='C'
  ;

create table transaction.refupdatedtidest as 
select transactionid, accountno 
from transaction.transactionitem a, transaction.accounttransactionitem c
where exists(
  select 1 from transaction.distributiontransferinfo b 
  where a.transactionid = b.transactionid) 
  and a.transactionitemid=c.transactionitemid
  and mutationtype='D'
  ;  


update transaction.distributiontransferinfo a 
set cashaccountnosource=
  (select accountno from transaction.refupdatedtisource b where a.transactionid = b.transactionid);


update transaction.distributiontransferinfo a 
set cashaccountnodest=
  (select accountno from transaction.refupdatedtidest b where a.transactionid = b.transactionid);  

drop table transaction.refupdatedtisource ;
drop table transaction.refupdatedtidest ;

select transactionid,
(select transactionitemid from transaction.refupdatetransactionitem b where a.transactionid = b.transactionid)
from transaction.distributiontransferinfo a;

--update transaction.distributiontransferinfo a 
--set transactionitemid=
  --(select transactionitemid from transaction.transactionitem b where a.transactionid=b.transactionid and mutationtype='D');