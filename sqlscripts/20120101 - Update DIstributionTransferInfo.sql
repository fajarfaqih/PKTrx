alter table transaction.distributiontransferinfo  add balance numeric(32,2);
update transaction.distributiontransferinfo c set balance = (
select sum(amount) from transaction.transactionitem a, transaction.accounttransactionitem b
where a.transactionitemid=b.transactionitemid and c.distributionid = b.distributiontransferid and distributiontransferid is not null)