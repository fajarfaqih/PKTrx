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

-- ## TEST
update transaction.transactionitem set parameterjournalid='DA01D' where transactionid=120654

select * from transaction.transitemglinterface 
insert into transaction.transitemglinterface values('ASET_KELOLA','4610201','286422','PENAMBAHAN ASET KELOLAAN');

select * from accounting.account where account_code like '461%'

select * from transaction.glinterface where productid=229 and interfacecode='PHP_MANF_INFAQ'
update transaction.glinterface set interfacecode='ASSET_FROM_INFAQ' where productid=229 and interfacecode='PHP_MANF_INFAQ'

select * from transaction.product where productid=229
select * from transaction.parameterglobal
