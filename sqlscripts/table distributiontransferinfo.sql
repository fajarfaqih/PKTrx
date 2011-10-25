
create table transaction.distributiontransferinfo(
  transactionid integer,
  reporttransactionid integer,
  accountno varchar(30),
  branchdestination varchar(3),
  branchsource varchar(3),
  reportstatus varchar(1),
  constraint distributiontransferinfo_pkey PRIMARY KEY (transactionid)
);


ALTER TABLE transaction.distributiontransferinfo OWNER TO transaction;