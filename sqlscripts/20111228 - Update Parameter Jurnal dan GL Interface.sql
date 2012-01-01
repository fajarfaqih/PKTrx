select * from transaction.transactionitem where transactionid=120654
-- CODE PHP_MANF_INFAQ dsb perlu diupdate juga kaya'nya
create table transaction.transitemglinterface (
  glinterfacecode varchar(20),
  accountcode varchar(20) ,
  transactionitemid integer,
  description varchar(200),
  primary key(glinterfacecode,transactionitemid)
);

alter table transaction.transitemglinterface owner to transaction

alter table transaction.parameterglobal alter column kode_parameter type varchar(25);
insert into transaction.parameterglobal (kode_parameter, deskripsi, nilai_parameter_string) values('GLIASSETFROMAMIL','PENAMBAHAN ASET KELOLAAN DARI AMIL','4610401');
insert into transaction.parameterglobal (kode_parameter, deskripsi, nilai_parameter_string) values('GLIAMILFORACCRECEIV','AMIL - BEBAN ASET KELOLAAN ATAS PIUTAN','5330201');


select * from transaction.parameterglobal where kode_parameter like 'GL%'
update transaction.parameterglobal set nilai_parameter_string='' where kode_parameter='GLIASSETFROMAMIL'

insert into transaction.glinterfacemember values(67,'AMILCOSTFORASSET','5530102',null,'BEBAN BIAYA AMIL ATAS ASSET',1); -- BANGUNAN
insert into transaction.glinterfacemember values(68,'AMILCOSTFORASSET','5530102',null,'BEBAN BIAYA AMIL ATAS ASSET',3); -- BANGUNAN
insert into transaction.glinterfacemember values(69,'AMILCOSTFORASSET','5530101',null,'BEBAN BIAYA AMIL ATAS ASSET',2); -- TANAH
insert into transaction.glinterfacemember values(70,'AMILCOSTFORASSET','5530101',null,'BEBAN BIAYA AMIL ATAS ASSET',8); -- TANAH
insert into transaction.glinterfacemember values(71,'AMILCOSTFORASSET','5530103',null,'BEBAN BIAYA AMIL ATAS ASSET',4); -- KENDARAAN
insert into transaction.glinterfacemember values(72,'AMILCOSTFORASSET','5530103',null,'BEBAN BIAYA AMIL ATAS ASSET',5); -- KENDARAAN
insert into transaction.glinterfacemember values(73,'AMILCOSTFORASSET','5530104',null,'BEBAN BIAYA AMIL ATAS ASSET',6); -- PERALATAN
insert into transaction.glinterfacemember values(74,'AMILCOSTFORASSET','5530104',null,'BEBAN BIAYA AMIL ATAS ASSET',7); -- PERALATAN

select * from transaction.glinterfacemember where glicontainerid=1 and gli
delete from transaction.glinterfacemember where glimemberid > 66
select * from transaction.id_gen where id_code='GLINTERFACEMEMBER';
update transaction.id_gen set last_id=(select max(glimemberid) from transaction.glinterfacemember)+1  where id_code='GLINTERFACEMEMBER';

-- ## TEST
update transaction.transactionitem set parameterjournalid='DA01D' where transactionid=120654

select * from transaction.transitemglinterface 
insert into transaction.transitemglinterface values('ASET_KELOLA','4610201','286422','PENAMBAHAN ASET KELOLAAN');

select * from accounting.account where account_code like '461%'

select * from transaction.glinterface where productid=229 and interfacecode='PHP_MANF_INFAQ'
update transaction.glinterface set interfacecode='ASSET_FROM_INFAQ' where productid=229 and interfacecode='PHP_MANF_INFAQ'

select * from transaction.product where productid=229
select * from transaction.parameterglobal

select * from accounting.accountingday where fl_accountingyear='2011' and periode_status = 'O'
update accounting.accountingday set periode_status = 'O' where fl_accountingyear='2012';

select * from transaction.transitemglinterface

update transaction.transactionitem b set parameterjournalid='AK-A1' where parameterjournalid='AK-A' and exists(
select 1 from transaction.transaction a
where a.transactionid=b.transactionid and a.transactioncode='EAR' );


update transaction.transactionitem b set parameterjournalid='AK-A2' where parameterjournalid='AK-A' and exists(
select 1 from transaction.transaction a
where a.transactionid=b.transactionid and a.transactioncode='CA' );

update transaction.transactionitem b set parameterjournalid='AK-A3' where parameterjournalid='AK-A' and exists(
select 1 from transaction.transaction a
where a.transactionid=b.transactionid and a.transactioncode='INVS' );

select * from transaction.transactionitem b where parameterjournalid='AK-A' and exists(
select 1 from transaction.transaction a
where a.transactionid=b.transactionid and a.transactioncode='INVS' )

/*
select * from transaction.transitemglinterface where glinterfacecode=''
insert into transaction.transitemglinterface 
select 'AMILCOSTFORPIUTANG','5330201',transactionitemid,'Beban Aset Kelolaan Amil Atas Piutang'
from transaction.accounttransactionitem  c where exists(
select 1 from transaction.transaction a, transaction.transactionitem b
where a.transactionid=b.transactionid 
and b.transactionitemid=c.transactionitemid
and mutationtype='D'
and a.transactioncode='EAR' ) and fundentity=4
*/




--insert into transaction.transitemglinterface select 'AMILCOSTFORPIUTANG','5330201',transactionitemid,'Beban Aset Kelolaan Amil Atas Piutang'
--select * from transaction.transitemglinterface where transactionitemid=286428
--delete from transaction.transitemglinterface  where glinterfacecode='AMILCOSTFORPIUTANG'

