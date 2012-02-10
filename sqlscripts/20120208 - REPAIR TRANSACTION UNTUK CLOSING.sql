select a.*,b.accountname from transaction.Transaction a     
left outer join transaction.financialaccount b     
on (a.channelaccountno=b.accountno)     
left outer join transaction.branch c     
on (a.branchcode=c.branchcode)     
where  ActualDate >= '2010-12-31' and ActualDate <='2012-02-08'  
and Amount between 0.0 and 100000000.0  
and a.BranchCode='001'  
and upper(TransactionNo) like '%GT-2011-001-000-0000001%' order by ActualDate asc;

select * from accounting.journalitem where accountinstance_id=38674

update transaction.transactionitem set accountcode='5210102' where transactionid=2573 and mutationtype='C';
select * from transaction.transactionitem where refaccountno='P2010201.001.0001';

select a.*,b.accountname from Transaction a     left outer join financialaccount b     on (a.channelaccountno=b.accountno)     left outer join branch c     on (a.branchcode=c.branchcode)     where  ActualDate >= '2011-01-01' and ActualDate <='2011-01-31'  and Amount between 0.0 and 100000000.0  and a.BranchCode='001'  and upper(TransactionNo) like '%GT-2011-001-000-0000140%'     order by ActualDate asc     Limit 50 

select * from transaction.parameterglobal

select * from transaction.transaction a where upper(TransactionNo) like '%KK-2011-212-000-0000001%'
select * from transaction.transaction a where exists(
select 1 from transaction.transactionbatch b where a.batchid=b.batchid and batchno='IST.2011.01.0000023')



select * from accounting.journalitem where journalblock_id=1182
select * from accounting.journalblock where key_id=1182 and id_journalblock=15207

"GT-2011-001-000-0000002"

-- Daftar transaksi yang gagal jurnal
select * from transaction.transaction where 
actualdate between '2011-01-01' and '2011-01-31' 
and authstatus='T'
and isposted='F'

select * from 

select * from transaction.parameterjournal
-- UPDATE TRANSAKSI yang ga ada jurnalnya
update transaction.transaction set batchid=329 where transactionno in ('KM-2011-101-BMD09-0000001','KM-2011-101-BMD09-0000002')


--UPDATE TRANSAKSI ITEM YANG ACCOUNTCODEnya kosong
select a.* from transaction.transactionitem a, transaction.accounttransactionitem b 
where a.transactionitemid = b.transactionitemid and transactionid = 36293 

select * from transaction.transactionitem where refaccountno='P2020101.101.0001' and mutationtype='D'
update transaction.transactionitem set accountcode='5210103' where transactionitemid=13764 and mutationtype='D'
update transaction.transactionitem set accountcode='5210103' where transactionitemid=19625 and mutationtype='D'

select * from accounting.account where account_code like '52101%'

-- UPDATE TRANSAKSI ITEM yang parameterjurnalnya ga ada di tabel master parameterjournal
select * from transaction.transactionitem a where not exists
(select 1 from transaction.parameterjournal b where a.parameterjournalid =b.journalcode )
update transaction.transactionitem set parameterjournalid='AK-A1' where parameterjournalid='AK-A'

-- DAFTAR JOURNAL ITEM YANG ACCOUNTINSTANCE nya Tidak terdaftar
select * from accounting.journalitem a where not exists(
select accountinstance_id from accounting.accountinstance b where a.accountinstance_id=b.accountinstance_id) 
and dateposting >= '2011-01-01' and dateposting <= '2011-01-31' 

select * from accounting.accountinstance a where fl_cpa_accountinstance is not null and not exists(
select accountinstance_id from accounting.accountinstance b where a.fl_cpa_accountinstance=b.accountinstance_id) 
SELECT * FROM accounting.ACCOUNTINSTANCE WHERE ACCOUNTINSTANCE_ID = 2302

select * from accounting.journal a ,accounting.journalitem b where  
a.journal_no=b.fl_journalno and  ACCOUNTINSTANCE_ID = 2302

select * from accounting.journalitem b where  ACCOUNTINSTANCE_ID = 2302
select * from accounting.account where account_code='111201'
-- SELECT JOURNAL ITEM BY journalblockid
select * from accounting.journalitem where id_journalblock=15207;

select * from transaction.transaction where channelaccountno is null
and ActualDate >= '2011-01-01' and ActualDate <='2011-01-31'  

-- DELETE JOURNAL ITEM Accounting yang tidak memiliki transaksi 
select * from accounting.journalitem a where not exists (
select 1 from transaction.transaction c where c.journalblockid = a.id_journalblock
) ;

delete from accounting.journalitem a where not exists (
select 1 from transaction.transaction c where c.journalblockid = a.id_journalblock
) ;



-- DELETE JOURNAL ITEM Accounting yang tidak memiliki transaksi dan accountinstance
select *from accounting.journalitem a where accountinstance_id = 57021
--and not exists(
--select accountinstance_id from accounting.accountinstance b where a.accountinstance_id=b.accountinstance_id) 
and exists (
select 1 from transaction.transaction c where c.journalblockid = a.id_journalblock
) ;

delete from accounting.journalitem a where accountinstance_id = 2302
and not exists (
select 1 from transaction.transaction c where c.journalblockid = a.id_journalblock
) ;


delete from accounting.journalitem a where not exists(
select accountinstance_id from accounting.accountinstance b where a.accountinstance_id=b.accountinstance_id) 
and dateposting >= '2011-01-01' and dateposting <= '2011-01-31' 
and not exists (
select 1 from transaction.transaction c where c.journalblockid = a.id_journalblock
)

-- DAFTAR JOURNAL ITEM Accounting yang tidak memiliki accountinstance tapi ada transaksi
select a.fl_journal, fl_account, amount_debit, amount_credit,
a.description, a.branch_code, a.datecreate, c.actualdate, c.transactiondate, c.transactionno, c.transactionid
from accounting.journalitem a ,transaction.transaction c where 
c.journalblockid = a.id_journalblock and 
not exists(
select accountinstance_id from accounting.accountinstance b where a.accountinstance_id=b.accountinstance_id) 
and dateposting >= '2011-01-01' and dateposting <= '2011-01-31'

select distinct c.transactionid
from accounting.journalitem a ,transaction.transaction c where 
c.journalblockid = a.id_journalblock and 
not exists(
select accountinstance_id from accounting.accountinstance b where a.accountinstance_id=b.accountinstance_id) 
and c.actualdate between '2011-01-01' and '2011-01-31'
and exists(
select 1 from accounting.journal b where a.fl_journal=b.journal_no and journal_date between '2011-01-01' and '2011-01-31')
and dateposting >= '2011-01-01' and dateposting <= '2011-01-31'

select * from transaction.transactionitem a where transactionid=3670 not exists(
select 1 from accounting.account b where a.accountcode = b.account_code )

and exists (
select 1 from transaction.transaction c where 
)

-------------
select * from accounting.journal where journal_no='IST.2011.01.0000006';

select amount_debit,description,id_journalblock 
from accounting.journalitem 
where fl_journal in ('IST.2011.01.0000006','IST.2011.02.0000006')
  and fl_account='1110201' order by id_journalblock;

select * from transaction.transactionbatch where batchno in ('IST.2011.01.0000006','IST.2011.02.0000006')

select a.*
from 
  transaction.transactionitem a, 
  transaction.accounttransactionitem b
where a.transactionitemid=b.transactionitemid
and mutationtype = 'C'
and exists (
select 1 from transaction.transaction c where c.transactionid=a.transactionid 
and batchid in (85,214) and inputer ='RIJAL'
)
and a.transactionitemid not in (
select i.transactionitemid
       from transaction.accounttransactionitem a, transaction.transactionitem i, 
            transaction.transaction t, transaction.financialaccount f , transaction.productaccount p, 
            public.php_donor d, transaction.branch b 
       where a.TransactionItemId = i.TransactionItemId           
       and i.TransactionId = t.TransactionId
       and p.AccountNo = f.AccountNo           
       and a.AccountNo = f.AccountNo
       and a.DonorId = d.id           
       and b.branchcode = i.branchcode           
       and a.Accounttitype = 'D'           
       and t.ActualDate >= '2011-01-01'           
       and t.ActualDate < '2011-01-02'            
       and i.BranchCode='001'    and inputer='RIJAL' )

select * from transaction.transaction where transactionid in (874,873)

1806;"001";"000";"C";280000;1;280000;"A";874;"10";"";"";"Infaq Shodaqoh";"11901.001.000";"Infaq Shodaqoh";"4510302"
1804;"001";"000";"C";100000;1;100000;"A";873;"10";"";"";"Infaq Shodaqoh";"11901.001.000";"Infaq Shodaqoh";"4510302"

create table transaction.backupbatch as select a.description,batchdate,actualdate,a.inputer as batchinputer,b.inputer, b.transactioncode,transactionno from 
transaction.transactionbatch a,transaction.transaction b
where a.batchid=b.batchid and  (a.inputer <> b.inputer or a.batchdate <> b.actualdate)
and transactioncode <> 'TB'
and batchdate = '2010-12-31'

select * from transaction.backupbatch 
select * from transaction.transaction where transactionno='KM-2010-213-KSL01-0000001'

select * from transaction.transactionbatch where description like '%31/12/2010'