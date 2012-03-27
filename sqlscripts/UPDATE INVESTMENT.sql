-- Update Jurnal


INSERT INTO transaction.parameterjournal (parameterjournalid, journalcode, description, datasource) VALUES (63, 'AK-A3', 'ASET KELOLAAN INVESTASI DARI DANA AMIL', 'SQL_1.sql');
INSERT INTO transaction.parameterjournal (parameterjournalid, journalcode, description, datasource) VALUES (57, 'PI-Z', 'PENGEMBALIAN INVESTASI KE DANA ZAKAT', 'SQL_25.sql');
INSERT INTO transaction.parameterjournal (parameterjournalid, journalcode, description, datasource) VALUES (58, 'PI-I', 'PENGEMBALIAN INVESTASI KE DANA INFAQ', 'SQL_25.sql');
INSERT INTO transaction.parameterjournal (parameterjournalid, journalcode, description, datasource) VALUES (59, 'PI-W', 'PENGEMBALIAN INVESTASI KE DANA WAKAF', 'SQL_25.sql');
INSERT INTO transaction.parameterjournal (parameterjournalid, journalcode, description, datasource) VALUES (60, 'PI-A', 'PENGEMBALIAN INVESTASI KE DANA AMIL', 'SQL_25.sql');

INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (198, NULL, 'T', 'Rekening', 'P', 'T', 'Amount', 'Rate', 63, 'T', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (199, '4610401', 'T', 'PENAMBAHAN ASET KELOLAAN DARI AMIL', 'N', 'T', 'Amount', 'Rate', 63, 'P', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (200, '5530501', 'T', 'BEBAN AMIL UNTUK ASET KELOLAAN INVESTASI', 'P', 'T', 'Amount', 'Rate', 63, 'P', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (160, '', 'T', 'REKENING', 'P', 'T', 'PrincipalAmount', 'Rate', 57, 'T', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (161, '4110101', 'T', 'PENERIMAAN ZAKAT', 'N', 'T', 'PrincipalAmount', 'Rate', 57, 'P', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (162, '5610101', 'T', 'PENGURANG ASET KELOLAAN DARI ZAKAT', 'P', 'T', 'PrincipalAmount', 'Rate', 57, 'P', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (163, '4510603', 'T', 'REKENING AMIL PENERIMAAN BAGI HASIL INVESTASI', 'P', 'T', 'ShareAmount', 'Rate', 57, 'P', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (164, '', 'T', 'REKENING', 'P', 'T', 'PrincipalAmount', 'Rate', 58, 'T', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (165, '4220101', 'T', 'PENERIMAAN INFAQ TIDAK TERIKAT', 'N', 'T', 'PrincipalAmount', 'Rate', 58, 'P', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (166, '5610202', 'T', 'PENGURANG ASET KELOLAAN DARI INFAQ TIDAK TERIKAT', 'P', 'T', 'PrincipalAmount', 'Rate', 58, 'P', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (167, '4510603', 'T', 'REKENING AMIL PENERIMAAN BAGI HASIL INVESTASI', 'P', 'T', 'ShareAmount', 'Rate', 58, 'P', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (168, '', 'T', 'REKENING', 'P', 'T', 'PrincipalAmount', 'Rate', 59, 'T', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (169, '4310101', 'T', 'PENERIMAAN WAKAF', 'N', 'T', 'PrincipalAmount', 'Rate', 59, 'P', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (170, '5610301', 'T', 'PENGURANG ASET KELOLAAN DARI WAKAF', 'P', 'T', 'PrincipalAmount', 'Rate', 59, 'P', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (171, '4510603', 'T', 'REKENING AMIL PENERIMAAN BAGI HASIL INVESTASI', 'P', 'T', 'ShareAmount', 'Rate', 59, 'P', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (172, '', 'T', 'REKENING', 'P', 'T', 'PrincipalAmount', 'Rate', 60, 'T', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (175, '4510603', 'T', 'REKENING AMIL PENERIMAAN BAGI HASIL INVESTASI', 'P', 'T', 'ShareAmount', 'Rate', 60, 'P', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (174, '5610401', 'T', 'PENGURANG ASET KELOLAAN DARI PENGELOLA', 'N', 'T', 'PrincipalAmount', 'Rate', 60, 'P', 'F');
INSERT INTO transaction.parameterjournalitem (parameterjournalitemid, accountcode, branchbase, description, basesign, currencybase, amountbase, ratebase, parameterjournalid, accountbase, issendjournaldescription) VALUES (173, '5530501', 'T', 'Pengembalian Aset Kelolaan Ke Dana Amil', 'P', 'T', 'PrincipalAmount', 'Rate', 60, 'P', 'F');

-- 

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

update transaction.transactiontype set description='PENANAMAN INVESTASI' where transactioncode='INVS';

update transaction.accounttransactionitem c set accounttitype='R' where exists 
( select 1 from transaction.transaction a , transaction.transactionitem b
  where a.transactionid = b.transactionid and b.transactionitemid=c.transactionitemid
    and a.transactioncode='INVS' ) and fundentity is not null  ;



insert into transaction.accreceivabletransactitem 
select c.transactionitemid, 'I', 'P', b.amount, 0.0
from transaction.transaction a , 
  transaction.transactionitem b, 
  transaction.accounttransactionitem c 
where a.transactionid = b.transactionid and b.transactionitemid=c.transactionitemid
    and a.transactioncode='INVS' and fundentity is not null and isupdatebalance='T';

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