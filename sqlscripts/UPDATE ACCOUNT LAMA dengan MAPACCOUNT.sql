select distinct c.transactioncode,a.accountcode,a.refaccountname from transaction.transaction c,transaction.transactionitem a where not exists (
select 1 from accounting.account b where a.refaccountno = b.account_code) and accountcode is not null
and transactionitemtype='G'
and c.transactionid=a.transactionid

select * from transaction.transactionitem where exists( select 1 from transaction.mapaccount where oldaccount=refaccountno)

select * from transaction.transactionitem where accountcode <> glnumber and transactionitemtype='G'


create table transaction.mapaccount 
( oldaccount varchar(20) primary key,
  newaccount varchar(20) );
alter table transaction.mapaccount owner to transaction;  

truncate table transaction.mapaccount ;
insert into transaction.mapaccount values('411','4110101');
insert into transaction.mapaccount values('413','4310101');
insert into transaction.mapaccount values('421','4510302');
insert into transaction.mapaccount values('511','5110101');
insert into transaction.mapaccount values('513','5310101');
insert into transaction.mapaccount values('514','5410101');
insert into transaction.mapaccount values('521','5210201');
insert into transaction.mapaccount values('1132','1130101');
insert into transaction.mapaccount values('1133','1130201');
insert into transaction.mapaccount values('1161','1160101');
insert into transaction.mapaccount values('1211','1210101');
insert into transaction.mapaccount values('1212','1210201');
insert into transaction.mapaccount values('4122','4210102');
insert into transaction.mapaccount values('4123','4210103');
insert into transaction.mapaccount values('4141','4410101');
insert into transaction.mapaccount values('4142','4410102');
insert into transaction.mapaccount values('4223','4510901');
insert into transaction.mapaccount values('5122','5210102');
insert into transaction.mapaccount values('5123','5210103');
insert into transaction.mapaccount values('11401','1140101');
insert into transaction.mapaccount values('11410','1140101');
insert into transaction.mapaccount values('42211','4510201');
insert into transaction.mapaccount values('42212','4510301');
insert into transaction.mapaccount values('42213','4510401');
insert into transaction.mapaccount values('42221','4510601');
insert into transaction.mapaccount values('42222','4510602');
insert into transaction.mapaccount values('99999','9999999');
insert into transaction.mapaccount values('111101','1110101');
insert into transaction.mapaccount values('111201','1110201');
insert into transaction.mapaccount values('113405','1130305');
insert into transaction.mapaccount values('122103','1220103');
insert into transaction.mapaccount values('122104','1220104');
insert into transaction.mapaccount values('122204','1220204');
insert into transaction.mapaccount values('522101','5520902');
insert into transaction.mapaccount values('522201','5510201');
insert into transaction.mapaccount values('522202','5510202');
insert into transaction.mapaccount values('522203','5510203');
insert into transaction.mapaccount values('522204','5510204');
insert into transaction.mapaccount values('522301','5510301');
insert into transaction.mapaccount values('522302','5510302');
insert into transaction.mapaccount values('522304','5510304');
insert into transaction.mapaccount values('522403','5520301');
insert into transaction.mapaccount values('522407','5520701');
insert into transaction.mapaccount values('620501','5210201');
insert into transaction.mapaccount values('620504','5210201');
insert into transaction.mapaccount values('5220201','5510208');
insert into transaction.mapaccount values('52210201','5510102');
insert into transaction.mapaccount values('52210202','5510103');
insert into transaction.mapaccount values('52210203','5510104');
insert into transaction.mapaccount values('52210204','5510105');
insert into transaction.mapaccount values('52210207','5510108');
insert into transaction.mapaccount values('52240101','5520101');
insert into transaction.mapaccount values('52240102','5520102');
insert into transaction.mapaccount values('52240103','5520103');
insert into transaction.mapaccount values('52240104','5520104');
insert into transaction.mapaccount values('52240105','5520105');
insert into transaction.mapaccount values('52240106','5520108');
insert into transaction.mapaccount values('52240107','5520106');
insert into transaction.mapaccount values('52240201','5520201');
insert into transaction.mapaccount values('52240202','5520202');
insert into transaction.mapaccount values('52240204','5520204');
insert into transaction.mapaccount values('52240205','5520205');
insert into transaction.mapaccount values('52240207','5520207');
insert into transaction.mapaccount values('52240208','5520208');
insert into transaction.mapaccount values('52240401','5520401');
insert into transaction.mapaccount values('52240402','5520402');
insert into transaction.mapaccount values('52240403','5520403');
insert into transaction.mapaccount values('52240501','5520501');
insert into transaction.mapaccount values('52240502','5520502');
insert into transaction.mapaccount values('52240503','5520503');
insert into transaction.mapaccount values('52240601','5520601');
insert into transaction.mapaccount values('62010201','5210201');

update transaction.transactionitem   set glnumber=accountcode where transactionitemtype='G'
and accountcode <> glnumber;

update transaction.transactionitem  
  set accountcode=(select newaccount from transaction.mapaccount where oldaccount=accountcode),
  glnumber=(select newaccount from transaction.mapaccount where oldaccount=accountcode),
  refaccountno=(select newaccount from transaction.mapaccount where oldaccount=accountcode)
where exists( select 1 from transaction.mapaccount where oldaccount=accountcode)
  and transactionitemtype='G'
  
select * from transaction.transaction where transactionid=7777

select * from accounting.account where account_code like '191%';
select * from accounting.temptablenew;
update accounting.temptablenew set is_processed=1 where accountcode='19101';

insert into accounting.temptablenew values('19101','REKENING ANTAR KANTOR OTOMATIS','A','F','191','',null);
update accounting.temptablenew set is_processed=1;
insert into accounting.temptablenew values('1910101','REKENING ANTAR KANTOR OTOMATIS','A','T','19101','',null);

select * from accounting.accounthierarchy where fl_par

select max(accounthierarchy_id) from accounting.accounthierarchy
