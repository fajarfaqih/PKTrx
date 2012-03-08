alter table transaction.fixedasset add buyername varchar(200);
alter table transaction.fixedasset add assetdetaildescription varchar(500);
alter table transaction.fixedasset add assetorigin varchar(1);

insert into transaction.enum_varchar values('eAssetOrigin','D','Donasi');
insert into transaction.enum_varchar values('eAssetOrigin','B','Pembelian');