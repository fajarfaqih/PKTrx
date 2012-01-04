select * from transaction.parameterinbox;
delete from transaction.transactiontype  where transactioncode='FAD';
delete from transaction.parameterinbox where kodeinbox='FAD';
insert into transaction.transactiontype values('FAD','DONASI AKTIVA TETAP','KM','INCOME');
insert into transaction.parameterinbox values('FAD','DONASI AKTIVA TETAP','fFixedAssetNew','TRAN');


create table transaction.deprassettransactitem
( transactionitemid integer primary key,
  deprassettitype varchar(1)    
);
alter table transaction.deprassettransactitem owner to transaction;

create table transaction.fixedassettransactitem
( transactionitemid integer primary key,
  fatransactitemtype varchar(1),
  donorid integer
);
alter table transaction.fixedassettransactitem owner to transaction;

alter table transaction.fixedasset add donorid integer;
alter table transaction.fixedasset add fundentity integer;

insert into transaction.deprassettransactitem select transactionitemid,'F' from transaction.transactionitem a where exists (
 select 1 from transaction.transaction b where transactioncode like 'F%'
 and a.transactionid = b.transactionid
) and parameterjournalid like 'DA01%' and not exists
(select 1 from transaction.deprassettransactitem b where a.transactionitemid = b.transactionitemid);

insert into transaction.fixedassettransactitem select transactionitemid,null,null from transaction.transactionitem a where exists (
 select 1 from transaction.transaction b where transactioncode like 'F%'
 and a.transactionid = b.transactionid
) and parameterjournalid like 'DA01%' and not exists
(select 1 from transaction.fixedassettransactitem b where a.transactionitemid = b.transactionitemid);

-- insert into transaction.transitemglinterface 
-- select 'ASET_KELOLA','4610201',transactionitemid,'Penambahaan Aset Kelolaan' from transaction.transactionitem a where exists (
--  select 1 from transaction.transaction b where transactioncode like 'F%'
--  and a.transactionid = b.transactionid
-- ) and parameterjournalid like 'DA01D' and exists
-- (select 1 from transaction.fixedassettransactitem b where a.transactionitemid = b.transactionitemid)
-- and not exists
-- (select 1 from transaction.transitemglinterface b where a.transactionitemid = b.transactionitemid)

update transaction.accounttransactionitem a set accounttitype = 'A' where exists
(select 1 from transaction.fixedassettransactitem b where a.transactionitemid = b.transactionitemid)

insert into transaction.transitemglinterface 
select 'ASET_KELOLA','4610201',transactionitemid,'Penambahaan Aset Kelolaan' from transaction.accounttransactionitem c where exists (
 select 1 from transaction.transaction b, transaction.transactionitem a where transactioncode like 'F%'
 and a.transactionid = b.transactionid and c.transactionitemid = a.transactionitemid and parameterjournalid = 'DA02A'
);

update transaction.transitemglinterface a set accountcode = '4610401' where exists
(select 1 from transaction.fixedassettransactitem b where a.transactionitemid = b.transactionitemid)
and exists
(select 1 from transaction.accounttransactionitem b where a.transactionitemid = b.transactionitemid and fundentity = 4) 

select * from transaction.userapp where upper(id_user) like '%ACENG%'

select * from transaction.transaction where transactionno='KK-2011-101-KBD01-0001354'