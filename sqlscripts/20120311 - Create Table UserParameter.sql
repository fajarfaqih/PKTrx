create table transaction.userparameter(
 userid varchar(20) primary key,
 printertype varchar(1),
 voucherformat varchar(1));

alter table transaction.userparameter owner to transaction ;

insert into transaction.userparameter select id_user,1,1 from transaction.userapp;

update transaction.userparameter a set printertype=2
where exists (
select 1 from transaction.userapp b where a.userid=b.id_user and branch_code='101');

drop table transaction.parameterjournaltrans ;
create table transaction.parameterjournaltrans as select * from transaction.parameterjournal where journalcode like 'AK-A3';

drop table transaction.parameterjournalitemtrans ;
create table transaction.parameterjournalitemtrans as select * from transaction.parameterjournalitem b where 
exists (select 1 from transaction.parameterjournal a where a.parameterjournalid=b.parameterjournalid and a.journalcode like 'AK-A3')