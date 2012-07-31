alter table transaction.distributionTransferInfo add distributionamount float;

update transaction.distributiontransferinfo a set distributionamount= 
(select amount from transaction.transaction b where a.transactionid=b.transactionid);

drop table transaction.tmpdistributioninfo;

create table transaction.tmpdistributioninfo as select *,
( select coalesce(sum(amount),0.0)
from transaction.transactionitem b , transaction.accounttransactionitem c 
where b.transactionitemid = c.transactionitemid
and c.distributionTransferId=a.distributionId
) as used,
( select count(amount) 
from transaction.transactionitem b , transaction.accounttransactionitem c 
where b.transactionitemid = c.transactionitemid
and c.distributionTransferId=a.distributionId
) as usedcount
from transaction.distributionTransferInfo a;


update transaction.distributiontransferinfo a set balance= (distributionamount -
(select used from transaction.tmpdistributioninfo b where a.distributionid=b.distributionid))