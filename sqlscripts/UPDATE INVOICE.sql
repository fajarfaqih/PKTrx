alter table transaction.invoice add column currencycode varchar(20);
alter table transaction.invoice add column paymenttransactionitemid integer;
update transaction.invoice set currencycode='000';
insert into transaction.parameterglobal (kode_parameter, deskripsi, nilai_parameter_string) values('GLIPROJAR','Acount Piutang Proyek','1130301');
insert into transaction.parameterinbox values('INVP','TRANSAKSI PEMBAYARAN INVOICE','fInvoicePayment','TRAN');


-- Update invoice yang sudah memiliki payment
update transaction.invoice a set paymenttransactionid=(select transactionid from transaction.transaction b where a.invoiceamount=b.amount and transactioncode='INVP')
where invoicepaymentstatus ='T' and exists( select 1 from transaction.transaction b where a.invoiceamount=b.amount and transactioncode='INVP');

update transaction.invoice a set paymenttransactionitemid = 
  (select transactionitemid from transaction.transactionitem b where a.paymenttransactionid=b.transactionid and mutationtype='C')
where invoicepaymentstatus  = 'T' and paymenttransactionid is not null;

select *
from transaction.invoice a
where invoicepaymentstatus  = 'T' or paymenttransactionitemid is not null

select * from transaction.transactiontype where transactioncode='INVP';
select * from transaction.parameterinbox where kodeinbox='INVP';
