select * from transaction.transaction where transactionno='KM-2011-001-KKP01-0015424';

select * from transaction.accounttransactionitem c where exists 
( select 1 from transaction.transaction a , transaction.transactionitem b
  where a.transactionid = b.transactionid and b.transactionitemid=c.transactionitemid
    and a.transactioncode='INVS' ) and fundentity is not null


select * from transaction.transactionitem where transactionid=115494

select * from transaction.investmenttransactitem

create table transaction.accreceivabletransactitem(
  transactionitemid integer primary key,
  artransactitemtype varchar(1),
  investmenttitype varchar(1),
  principalamount numeric(38,2),
  shareamount numeric(38,2)
);
alter table transaction.accreceivabletransactitem owner to transaction;

update transaction.accounttransactionitem c set accounttitype='R' where exists 
( select 1 from transaction.transaction a , transaction.transactionitem b
  where a.transactionid = b.transactionid and b.transactionitemid=c.transactionitemid
    and a.transactioncode='INVSR' ) and fundentity is not null  ;

insert into transaction.accreceivabletransactitem 
select c.transactionitemid, 'I', 'S', a.amount-b.amount, b.amount
from transaction.transaction a , 
  transaction.transactionitem b, 
  transaction.accounttransactionitem c 
where a.transactionid = b.transactionid and b.transactionitemid=c.transactionitemid
    and a.transactioncode='INVSR' and fundentity is not null and isupdatebalance='F';

insert into transaction.accreceivabletransactitem 
select c.transactionitemid, 'I','P', b.amount, a.amount-b.amount
from transaction.transaction a , 
  transaction.transactionitem b, 
  transaction.accounttransactionitem c 
where a.transactionid = b.transactionid and b.transactionitemid=c.transactionitemid
    and a.transactioncode='INVSR' and fundentity is not null and isupdatebalance='T';

select * from transaction.accounttransactionitem c where exists 
( select 1 from transaction.transaction a , transaction.transactionitem b
  where a.transactionid = b.transactionid and b.transactionitemid=c.transactionitemid
    and a.transactioncode='INVSR' ) and fundentity is not null  and isupdatebalance='F'

select * from transaction.accounttransactionitem c where exists 
( select 1 from transaction.transaction a , transaction.transactionitem b
  where a.transactionid = b.transactionid and b.transactionitemid=c.transactionitemid
    and a.transactioncode='INVSR' ) 

    and fundentity is not null and isupdatebalance='F'

 select count(*) from transaction.transaction a
  where a.transactioncode='INVSR' 

 select a.amount,b.* from transaction.transaction a , transaction.transactionitem b
  where a.transactionid = b.transactionid 
    and a.transactioncode='INVSR'  and mutationtype='C' and parameterjournalid='PAK-A'


update transaction.accounttransactionitem c set parameterjournalid='PI-A' where exists 
( select 1 from transaction.transaction a , transaction.transactionitem b
  where a.transactionid = b.transactionid and b.transactionitemid=c.transactionitemid
    and a.transactioncode='INVSR' and parameterjournalid='PAK-A') and fundentity is not null  ;

update transaction.transactionitem b set parameterjournalid='PI-A' where exists(
  select 1 from transaction.transaction a
  where a.transactionid = b.transactionid    and a.transactioncode='INVSR' ) 
  and parameterjournalid='PAK-A'


delete from transaction.transactionitem b where exists(
  select 1 from transaction.accreceivabletransactitem a
  where a.transactionitemid = b.transactionitemid) 
  and parameterjournalid='10';

update transaction.transactionitem b set amount=(select amount from transaction.transaction c where c.transactionid=b.transactionid)  where exists(
  select 1 from transaction.accreceivabletransactitem a
  where a.transactionitemid = b.transactionitemid) 
  and parameterjournalid='PI-A';

select * from transaction.transaction where transactioncode='INVSR'  
select * from transaction.financialaccount where accountno='INVEST.001.00005'
select * from transaction.investment where accountno='INVEST.001.00005'
select 112900000 +( 714556 * 158)
//------------------- UPDATE PARAMETER JOURNAL

select * from transaction.transactionitem a where exists (
select 1 from transaction.accounttransactionitem b where a.transactionitemid=b.transactionitemid and accountno='INVEST.001.00005')
update transaction.accreceivabletransactitem set investmenttitype='P'
select * from transaction.accreceivabletransactitem a where not exists(
select * from transaction.transactionitem b where a.transactionitemid=b.transactionitemid)

select * from transaction.parameterjournal;
insert into transaction.parameterjournal values(57,'PI-Z','PENGEMBALIAN INVESTASI KE DANA ZAKAT','SQL_25.sql');
insert into transaction.parameterjournal values(58,'PI-I','PENGEMBALIAN INVESTASI KE DANA INFAQ','SQL_25.sql');
insert into transaction.parameterjournal values(59,'PI-W','PENGEMBALIAN INVESTASI KE DANA WAKAF','SQL_25.sql');
insert into transaction.parameterjournal values(60,'PI-A','PENGEMBALIAN INVESTASI KE DANA AMIL','SQL_25.sql');
update transaction.id_gen set last_id=60 where id_code ='PARAMETERJOURNAL';

select * from transaction.parameterjournalitem where parameterjournalid=50;

create sequence transaction.seq_paramjournal start with 160;

-- Zakat
insert into transaction.parameterjournalitem
select nextval('transaction.seq_paramjournal'),accountcode,branchbase,description,basesign,currencybase,'PrincipalAmount',ratebase,57,accountbase
 from transaction.parameterjournalitem where parameterjournalid=50;
insert into transaction.parameterjournalitem values
(nextval('transaction.seq_paramjournal'),'4510603','T','REKENING AMIL PENERIMAAN BAGI HASIL INVESTASI','P','T','ShareAmount','Rate',57,'P'
); 

-- INFAQ
insert into transaction.parameterjournalitem 
select nextval('transaction.seq_paramjournal'),accountcode,branchbase,description,basesign,currencybase,'PrincipalAmount',ratebase,58,accountbase
 from transaction.parameterjournalitem where parameterjournalid=51; 
insert into transaction.parameterjournalitem values
(nextval('transaction.seq_paramjournal'),'4510603','T','REKENING AMIL PENERIMAAN BAGI HASIL INVESTASI','P','T','ShareAmount','Rate',58,'P'
); 

-- WAKAF
insert into transaction.parameterjournalitem
select nextval('transaction.seq_paramjournal'),accountcode,branchbase,description,basesign,currencybase,'PrincipalAmount',ratebase,59,accountbase
 from transaction.parameterjournalitem where parameterjournalid=52; 
insert into transaction.parameterjournalitem values
(nextval('transaction.seq_paramjournal'),'4510603','T','REKENING AMIL PENERIMAAN BAGI HASIL INVESTASI','P','T','ShareAmount','Rate',59,'P'
); 

-- AMIL
insert into transaction.parameterjournalitem
select nextval('transaction.seq_paramjournal'),accountcode,branchbase,description,basesign,currencybase,'PrincipalAmount',ratebase,60,accountbase
 from transaction.parameterjournalitem where parameterjournalid=53;  
insert into transaction.parameterjournalitem values
(nextval('transaction.seq_paramjournal'),'4510603','T','REKENING AMIL PENERIMAAN BAGI HASIL INVESTASI','P','T','ShareAmount','Rate',60,'P'
); 

drop sequence transaction.seq_paramjournal ;

update transaction.id_gen set last_id=(select max(parameterjournalitemid) from transaction.parameterjournalitem) where id_code ='PARAMETERJOURNALITEM';