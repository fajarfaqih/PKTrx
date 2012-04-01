select * from sdm_employee where id=149735
select * from enterprise.userapp where id_user='SUDIANA';

-- Update Cabang User
update sdm_employee set branch_id=21 where id=149735;
update enterprise.userapp set kode_cabang='104' where id_user='SUDIANA';

select count(*) from transaction.transaction
where inputer = 'SUDIANA'

create table transaction.transhistoryofchanges
( historyid integer primary key,
  transactionno varchar(50),
  newtransactionno varchar(50),
  userid varchar(20),
  changetype varchar(1),
  processtime timestamp(6)
);

alter table transaction.transhistoryofchanges owner to transaction;

select distinct channelaccountno from transaction.transaction
where inputer = 'SUDIANA' and transactioncode = 'SD001' 
and channelcode ='A'
order by transactionno limit 1;

select * from transaction.transhistoryofchanges

select * from transaction.transaction where transactionno='KM-2011-101-000-0000007'
select * from transaction.transaction where branchcode='104'