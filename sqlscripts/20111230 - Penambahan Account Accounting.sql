select * from accounting.temptablenew  where is_processed is null and accountcode not in (
select account_code from accounting.account)

update accounting.temptablenew set is_processed=1 where is_processed is null;

insert into accounting.temptablenew values('45107','Penerimaan Pengelola Dari Aset Kelolaan','I','F','451',null,null);
insert into accounting.temptablenew values('4510701','Penerimaan Pengelola Dari Aset Kelolaan','I','T','45107','3150101',null);
insert into accounting.temptablenew values('46105','Penambahan Aset Kelolaan dari Non Halal','I','F','461',null,null);
insert into accounting.temptablenew values('4610501','Penambahan Aset Kelolaan dari Non Halal','I','T','46105','3210101',null);
insert into accounting.temptablenew values('553','Beban Aset Kelolaan','X','F','55',null,null);
insert into accounting.temptablenew values('55301','Beban Aset Kelolaan Atas Aset Tetap','X','F','553','',null);
insert into accounting.temptablenew values('5530101','Beban Aset Kelolaan Atas Tanah','X','T','55301',null,null);
insert into accounting.temptablenew values('5530102','Beban Aset Kelolaan Atas Gedung','X','T','55301','3150101',null);
insert into accounting.temptablenew values('5530103','Beban Aset Kelolaan Atas Kendaraan','X','T','55301',null,null);
insert into accounting.temptablenew values('5530104','Beban Aset Kelolaan Atas Peralatan','X','T','55301','3150101',null);
insert into accounting.temptablenew values('55302','Beban Aset Kelolaan Atas Piutang','X','F','553',null,null);
insert into accounting.temptablenew values('5330201','Beban Aset Kelolaan Atas Piutang','X','T','55302','3150101',null);
insert into accounting.temptablenew values('55303','Beban Aset Kelolaan Atas Uang Muka','X','F','553',null,null);
insert into accounting.temptablenew values('5330301','Beban Aset Kelolaan Atas Uang Muka','X','T','55303','3150101',null);
insert into accounting.temptablenew values('55304','Beban Aset Kelolaan Atas Biaya Dimuka','X','F','553',null,null);
insert into accounting.temptablenew values('5330401','Beban Aset Kelolaan Atas Biaya Dimuka','X','T','55304','3150101',null);
insert into accounting.temptablenew values('55305','Beban Aset Kelolaan Atas Investasi','X','F','553',null,null);
insert into accounting.temptablenew values('5330501','Beban Aset Kelolaan Atas Investasi','X','T','55305','3150101',null);
insert into accounting.temptablenew values('56105','Pengurang Aset Kelolaan dari Dana Non Halal','X','F','561',null,null);
insert into accounting.temptablenew values('5610501','Pengurang Aset Kelolaan dari Dana Non Halal','X','T','56104','3210101',null);

select accountcode from accounting.temptablenew where is_processed is null and accountcode not in
(select account_code from accounting.account );

select max(accounthierarchy_id) from accounting.accounthierarchy;
select * from accounting.accounthierarchy where accounthierarchy_id=6786
SELECT nextval('accounting.SEQ_ACCOUNTHIERARCHY')

INSERT INTO accounting.ACCOUNTHIERARCHY(ACCOUNTHIERARCHY_ID, FL_PARENTACCOUNTCODE, FL_CHILDACCOUNTCODE) VALUES (6786, '4', '4510701')
select * from accounting.accounthierarchy;

select * from accounting.account where account_code='5530103'
select * from accounting.accountinstance where account_code ='5530102'
select * from accounting.accountinstance where account_code ='3150101' and branch_code='115' and currency_code='000'
