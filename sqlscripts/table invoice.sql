
create table transaction.invoice(
  invoiceid integer,
  invoiceno varchar(30),
  invoicedate timestamp(6),
  invoiceamount double precision,
  invoiceaddress varchar(250),
  invoicebankname varchar(100),
  invoicebankaccountname varchar(100),
  invoicebankaccountnumber varchar(30),
  invoiceofficername varchar(100),
  invoiceofficerposition varchar(100),
  invoicetermdate timestamp(6),
  transactionid integer,
  paymenttransactionid integer,
  sponsorid integer,
  constraint invoice_pkey PRIMARY KEY (invoiceid)
);


ALTER TABLE transaction.invoice OWNER TO transaction;