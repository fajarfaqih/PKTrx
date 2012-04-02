select * from sdm_employee where id=149735
select * from enterprise.userapp where id_user='SUDIANA';
select * from transaction.branch
-- Update Cabang User

update sdm_employee set branch_id=21 where id=149735;
update enterprise.userapp set kode_cabang='104' where id_user='SUDIANA';

create table transaction.transhistoryofchanges
( historyid integer primary key,
  transactionno varchar(50),
  newtransactionno varchar(50),
  userid varchar(20),
  changetype varchar(1),
  processtime timestamp(6)
);

alter table transaction.transhistoryofchanges owner to transaction;

alter table transaction.inboxhistory add branchcode varchar(5);
