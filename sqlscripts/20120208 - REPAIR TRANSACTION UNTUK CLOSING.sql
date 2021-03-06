
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

select * from transaction.transactionitem where refaccountno='P2020101.101.0001' and mutationtype='D';
update transaction.transactionitem set accountcode='5210103' where transactionitemid=13764 and mutationtype='D';
update transaction.transactionitem set accountcode='5210103' where transactionitemid=19625 and mutationtype='D';
update transaction.transactionitem set accountcode='5210101' where transactionitemid=11720 and mutationtype='D';
update transaction.transactionitem set accountcode='4210101' where transactionitemid=25082 and mutationtype='C';

select * from accounting.account where account_code like '52101%'

-- UPDATE TRANSAKSI ITEM yang parameterjurnalnya ga ada di tabel master parameterjournal
select * from transaction.transactionitem a where not exists
(select 1 from transaction.parameterjournal b where a.parameterjournalid =b.journalcode )
update transaction.transactionitem set parameterjournalid='AK-A1' where parameterjournalid='AK-A';
update transaction.transactionitem set parameterjournalid='10' where parameterjournalid='11';

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

select c.transactionid, c.transactioncode,c.transactionno, c.actualdate, c.description, c.branchcode
from accounting.journalitem a ,transaction.transaction c where 
c.journalblockid = a.id_journalblock and 
exists(
select accountinstance_id from accounting.accountinstance b where a.accountinstance_id=b.accountinstance_id) 
and c.actualdate between '2011-01-01' and '2011-01-31'
and exists(
select 1 from accounting.journal b where a.fl_journal=b.journal_no and journal_date between '2011-01-01' and '2011-01-31')
and a.fl_account='9999999'

-- CEK TRANSAKSI YANG ID DONORNYA GA VALID
--select a.actualdate, a.transactionid, a.transactioncode, b.ekuivalenamount
select a.transactionno , a.actualdate, a.inputer
from transaction.transaction a , 
  transaction.transactionitem b,
  transaction.accounttransactionitem c
where a.transactionid = b.transactionid and
b.transactionitemid = c.transactionitemid and 
--a.actualdate between '2011-01-04' and '2011-01-04' and
c.accounttitype = 'D' and
--b.branchcode ='001' and
c.fundentity = 1 and not exists (
select 1 from public.php_donor d where a.donorid = d.id)

--order by a.actualdate, a.transactionid

-- QUERY CEK JUMLAH TRANSAKSI PENGHIMPUNAN TRANSAKSI
select sum(case when i.mutationtype = 'C' then i.Ekuivalenamount else -1 * i.Ekuivalenamount end) as Ekuivalenamount 
from transaction.accounttransactionitem a, transaction.transactionitem i,           
     transaction.transaction t, transaction.financialaccount f , 
     transaction.productaccount p,           
     public.php_donor d, transaction.branch b         where a.TransactionItemId = i.TransactionItemId           
     and i.TransactionId = t.TransactionId           
     and p.AccountNo = f.AccountNo           and a.AccountNo = f.AccountNo           
     and a.DonorId = d.id           and b.branchcode = i.branchcode           and a.Accounttitype = 'D'           
  and t.ActualDate >= '2011-01-03'           and t.ActualDate <= '2011-01-03'            and i.BranchCode='001'     and fundentity=1
  order by ActualDate, BranchName,TransactionId

-- QUERY CEK JUMLAH JURNAL CROSSING DENGAN TRANSAKSI

select sum(a.amount_credit)
from accounting.journalitem a ,transaction.transaction c,transaction.transactionitem b where 
c.transactionid = b.transactionid and
c.journalblockid = a.id_journalblock and 
b.accountcode='4110101'
and c.actualdate between '2011-01-03' and '2011-01-03'
and a.fl_account='4110101'
and b.branchcode='001'
--order by c.actualdate, c.transactionid

select * from accounting.dailybalance a where exists(
select * from accounting.accountinstance b where 
  a.accountinstance_id=b.accountinstance_id 
  and b.account_code='4110101')
and datevalue between '2011-01-03' and '2011-01-03'  


select     db.DATEVALUE as TheDate,      
case         when sum(db.DEBIT) is null then 0.0         else sum(db.DEBIT)      end as Debit,      case         when sum(db.CREDIT) is null then 0.0         else sum(db.CREDIT)      end as Kredit,      case         when sum(db.DEBIT_EKUIV) is null then 0.0         else sum(db.DEBIT_EKUIV)      end as DebitEkuiv,      case         when sum(db.CREDIT_EKUIV) is null then 0.0         else sum(db.CREDIT_EKUIV)      end as KreditEkuiv,      case         when sum(db.BALANCECUMULATIVE) is null then 0.0         else sum(db.BALANCECUMULATIVE)      end as Balance,      case         when sum(db.BALANCECUMULATIVE_EKUIV) is null then 0.0         else sum(db.BALANCECUMULATIVE_EKUIV)      end as BalanceEkuiv from accounting.DAILYBALANCE db, accounting.ACCOUNTINSTANCE ai where ai.ACCOUNT_CODE = '4110101' and       ('F' = 'T' or ai.BRANCH_CODE = '001') and       ('F' = 'F' or ai.CURRENCY_CODE = '') and       ai.ACCOUNTINSTANCE_ID = db.ACCOUNTINSTANCE_ID and       (db.DATEVALUE >= TO_TIMESTAMP('2011-01-01','yyyy-mm-dd') and db.DATEVALUE < TO_TIMESTAMP('2011-01-06','yyyy-mm-dd')) group by db.DATEVALUE  order by db.DATEVALUE 


-- Update GL Interface Proyek
select * from transaction.glinterface a 
where interfacecode='PHP_INFAQ'
  and exists(
    select 1 from transaction.product b 
      where a.productid = b.productid 
      and producttype='J'
      and isdetail='T' 
      and upper(productname) like 'KEMITRAAN%');

update transaction.glinterface a set accountcode='4210101' ,accountname='Penerimaan Kemitraan'
where interfacecode='PHP_INFAQ'
  and exists(
    select 1 from transaction.product b 
      where a.productid = b.productid 
      and producttype='J'
      and isdetail='T' 
      and upper(productname) like 'KEMITRAAN%');

update transaction.glinterface a set accountcode='5210101' ,accountname='Penyaluran Kemitraan'
where interfacecode='PDG_INFAQ'
  and exists(
    select 1 from transaction.product b 
      where a.productid = b.productid 
      and producttype='J'
      and isdetail='T' 
      and upper(productname) like 'KEMITRAAN%');


update transaction.glinterface a set accountcode='4210103' ,accountname='Penerimaan Proyek'
where interfacecode='PHP_INFAQ'
  and exists(
    select 1 from transaction.product b 
      where a.productid = b.productid 
      and producttype='J'
      and isdetail='T' 
      and upper(productname) not like 'KEMITRAAN%');


update transaction.glinterface a set accountcode='5210103' ,accountname='Penyaluran Proyek'
where interfacecode='PDG_INFAQ'
  and exists(
    select 1 from transaction.product b 
      where a.productid = b.productid 
      and producttype='J'
      and isdetail='T' 
      and upper(productname) not like 'KEMITRAAN%');
      

select *,(select accountcode from 
   transaction.glinterface g, 
   transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
    where  a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and g.productid = c.productid
    and interfacecode='PHP_INFAQ')  from transaction.transactionitem i where 
exists (
  select 1 from transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
  where a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and c.producttype = 'J'
    and a.fundentity = 2
    and a.accounttitype='D');

select *,(select accountcode from 
   transaction.glinterface g, 
   transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
    where  a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and g.productid = c.productid
    and interfacecode='PDG_INFAQ')  from transaction.transactionitem i where 
exists (
  select 1 from transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
  where a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and c.producttype = 'J'
    and a.fundentity = 2
    and a.accounttitype='Z');
        
update transaction.transactionitem i  set accountcode=(select accountcode from 
   transaction.glinterface g, 
   transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
    where  a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and g.productid = c.productid
    and interfacecode='PHP_INFAQ') where 
exists (
  select 1 from transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
  where a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and c.producttype = 'J'
    and a.fundentity = 2
    and a.accounttitype='D');

update transaction.transactionitem i  set accountcode=(select accountcode from 
   transaction.glinterface g, 
   transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
    where  a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and g.productid = c.productid
    and interfacecode='PDG_INFAQ')  where 
exists (
  select 1 from transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
  where a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and c.producttype = 'J'
    and a.fundentity = 2
    and a.accounttitype='Z');
        
# *** UPDATE RISWAH DAN WAKAF
# *** RIZWAH defaultnya non halal dan tidak ada persentase
# *** wakaf tidak ada persentase untuk amil

update transaction.transactionitem i set accountcode=(select accountcode from 
   transaction.glinterface g, 
   transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
    where  a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and g.productid = c.productid
    and interfacecode='PHP_NONHALAL'),parameterjournalid=10 
where 
exists (
  select 1 from transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
  where a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and a.accounttitype='D'
    and c.productid in (125,126) );


update transaction.accounttransactionitem i  set fundentity=5,percentageofamil=0
where 
exists (
  select 1 from transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
  where a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and a.accounttitype='D'
    and c.productid in (125,126));

update transaction.transactionitem i  set parameterjournalid=10
where 
exists (
  select 1 from transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
  where a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and a.accounttitype='D'
    and c.productcode like '122%' );
    
update transaction.accounttransactionitem i  set percentageofamil=0
where 
exists (
  select 1 from transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
  where a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and a.accounttitype='D'
    and c.productcode like '122%' );

update transaction.product set  percentageofamilfunds =0 where productid = 125 and percentageofamilfunds > 0;
update transaction.product set  percentageofamilfunds =0 where productcode like '122%' and percentageofamilfunds > 0;

#******* Update Percentage Of Fund Collection

---- Update percentage zakat
update transaction.accounttransactionitem i set percentageofamil = 12.5
where (percentageofamil > 100 or percentageofamil=0)
and exists (
  select 1 from transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
  where a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and a.accounttitype='D'
    and fundentity = 1
    and (c.productid <> 125 and c.productcode not like '122%' )); 

update transaction.transactionitem i set parameterjournalid='C10Z'
where parameterjournalid='10' and
 exists (
  select 1 from transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
  where a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and a.accounttitype='D'
    and a.percentageofamil > 0
    and fundentity = 1
    and (c.productid <> 125 and c.productcode not like '122%' )); 

---- Update percentage infaq
update transaction.accounttransactionitem i set percentageofamil = 30
where (percentageofamil > 100 or percentageofamil is null or percentageofamil=0)
and exists (
  select 1 from transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
  where a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and a.accounttitype='D'
    and fundentity = 2
    and (c.productid <> 125 and c.productcode not like '122%' )); 

update transaction.transactionitem i set parameterjournalid='C10I'
where parameterjournalid='10' and
 exists (
  select 1 from transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
  where a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and a.accounttitype='D'
    and a.percentageofamil > 0
    and fundentity = 2
    and (c.productid <> 125 and c.productcode not like '122%' )); 


# ------- DAFTAR Transaksi yang kursnya masih salah
select * from transaction.transaction t 
where exists (
  select * from transaction.transactionitem i
  where currencycode <> '000' 
     and rate = 1 
     and description <> 'Saldo Awal'
     and t.transactionid=i.transactionid
);


# --------- Update Limit Transaksi User
select nextval('transaction.seq_limittransaksi');
drop sequence transaction.seq_limittransaksi;
create sequence transaction.seq_limittransaksi;

insert into enterprise.limittransaksi select nextval('transaction.seq_limittransaksi'),'O',50000000,50000000,100,id_user from enterprise.userapp where status_profil = 'A';

select * from enterprise.id_gen;

update enterprise.id_gen set last_id=60;


update enterprise.limittransaksi a set nilai_limit=10000000000,nilai_limit_akumulasi=10000000000
where exists(
select 1 from enterprise. listperanuser b where id_peran in ('ADM','SPV') and a.id_user=b.id_user)


#------------- Update Jurnal untuk uang muka
select * from transaction.transactionitem ti
where exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where mutationtype='D'
and t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.transactioncode='CA'
and t.branchcode='001'
and ti.transactionitemid=i.transactionitemid)

update transaction.accounttransactionitem ti set fundentity = 4
where exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where mutationtype='D'
and t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.transactioncode='CA'
and t.branchcode='001'
and fundentity is null
and ti.transactionitemid=i.transactionitemid);

update transaction.transactionitem ti set parameterjournalid = '10'
where exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where mutationtype='C'
and t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.transactioncode='CA'
and t.branchcode='001'
and ti.transactionitemid=i.transactionitemid);

update transaction.transactionitem ti set parameterjournalid = 'AK-Z'
where exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where mutationtype='D'
and t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.transactioncode='CA'
and t.branchcode='001'
and fundentity=1
and ti.transactionitemid=i.transactionitemid);

update transaction.transactionitem ti set parameterjournalid = 'AK-I'
where exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where mutationtype='D'
and t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.transactioncode='CA'
and t.branchcode='001'
and fundentity=2
and ti.transactionitemid=i.transactionitemid);

update transaction.transactionitem ti set parameterjournalid = 'AK-A2'
where exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where mutationtype='D'
and t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.transactioncode='CA'
and t.branchcode='001'
and fundentity=4
and ti.transactionitemid=i.transactionitemid);

update transaction.transactionitem ti set parameterjournalid = 'AK-N'
where exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where mutationtype='D'
and t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.transactioncode='CA'
and t.branchcode='001'
and fundentity=5
and ti.transactionitemid=i.transactionitemid);

-- Update Parameter Jurnal
update transaction.parameterjournalitem a set basesign = 'N'
where exists(
select 1 from transaction.parameterjournal b
where (b.journalcode like 'AK%')
and a.parameterjournalid =b.parameterjournalid
) and accountcode like '4%';

update transaction.parameterjournalitem a set basesign = 'P'
where exists(
select 1 from transaction.parameterjournal b
where (b.journalcode like 'AK%' )
and a.parameterjournalid =b.parameterjournalid
) and accountcode like '5%';

update transaction.parameterjournalitem a set basesign = 'P'
where exists(
select 1 from transaction.parameterjournal b
where (b.journalcode like 'PAK%')
and a.parameterjournalid =b.parameterjournalid
) and accountcode like '4%';


update transaction.parameterjournalitem a set basesign = 'N'
where exists(
select 1 from transaction.parameterjournal b
where (b.journalcode like 'PAK%')
and a.parameterjournalid =b.parameterjournalid
) and accountcode like '5%';

-- Tambah parameter corporate name di accounting
insert into accounting.parameter values('CorporateName',null,'Nama Korporat','PKPU');
  

-- UPDATE 
update transaction.transactionitem i  set accountcode = (select accountcode from 
   transaction.glinterface g, 
   transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
    where  a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and g.productid = c.productid
    and interfacecode='PHP_INFAQ') where 
exists (
  select 1 from transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
  where a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and a.fundentity = 2
    and a.accounttitype='D')
    and exists (select accountcode from 
   transaction.glinterface g, 
   transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
    where  a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and g.productid = c.productid
    and g.accountcode <> i.accountcode 
    and interfacecode='PHP_INFAQ');

   update transaction.transactionitem i  set accountcode = (select accountcode from 
   transaction.glinterface g, 
   transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
    where  a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and g.productid = c.productid
    and interfacecode='PDG_INFAQ') where 
exists (
  select 1 from transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
  where a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and a.fundentity = 2
    and a.accounttitype='Z')
    and exists (select accountcode from 
   transaction.glinterface g, 
   transaction.accounttransactionitem a,
    transaction.productaccount b,
    transaction.product c
    where  a.transactionitemid=i.transactionitemid
    and a.accountno = b.accountno
    and b.productid = c.productid
    and g.productid = c.productid
    and g.accountcode <> i.accountcode 
    and interfacecode='PDG_INFAQ');  


-- UPDATE ACCOUNT HIERARCHY
create sequence accounting.seq_hierarchy start with 6701;
insert into accounting.accounthierarchy select nextval('accounting.seq_hierarchy'), account_code,account_code from accounting.account ac where
is_detail='T' and
not exists
(select 1
from accounting.accounthierarchy ah
where ah.fl_parentaccountcode=ah.fl_childaccountcode and ah.fl_parentaccountcode=ac.account_code );
drop sequence accounting.seq_hierarchy;
update accounting.id_gen set last_id=(select max(accounthierarchy_id) from accounting.accounthierarchy) +1 where id_code='ACCOUNTHIERARCHY'

-- DAFTAR TRANSAKSI BERDASARKAN CPA ACCOUNT 
select A.FL_ACCOUNT,ac.account_name,sum(amount_debit * nilai_kurs),sum(amount_credit* nilai_kurs)
FROM
accounting.account ac,
accounting.JOURNAL b,
accounting.JOURNALITEM a
left outer join transaction.transaction c
on (c.journalblockid = a.id_journalblock)
WHERE a.fl_account = ac.account_code and A.FL_JOURNAL = B.JOURNAL_NO AND 
(B.JOURNAL_DATE >= '2011-01-01' AND B.JOURNAL_DATE < '2011-02-01' AND A.branch_code = '001')
and fl_cpa_accountcode in ('3150101')
group by A.FL_ACCOUNT, ac.account_name
order by A.FL_ACCOUNT    

-- Update Jurnal Piutang --> STATUS UPLOAD PRODUCTION = YES
update transaction.accounttransactionitem ti set fundentity=4
where fundentity is null and exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where mutationtype='D'
and t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and i.parameterjournalid='10'
and t.transactioncode='EAR'
and ti.transactionitemid=i.transactionitemid);

update transaction.transactionitem ti set parameterjournalid='AK-A1'
where parameterjournalid='10' and exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where mutationtype='D'
and t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.transactioncode='EAR'
and c.fundentity = 4
and ti.transactionitemid=i.transactionitemid)

-- Update Saldo FinancialAccount --> STATUS UPLOAD PRODUCTION = YES

update transaction.financialaccount fa 
set balance=coalesce((select sum(case when mutationtype='D' then ti.amount else (-1 * ti.amount) end) 
from transaction.transaction t, transaction.transactionitem ti,transaction.accounttransactionitem ac 
where t.transactionid=ti.transactionid and ac.accountno=fa.accountno and ac.transactionitemid=ti.transactionitemid
and authstatus='T'), 0)
where financialaccounttype='R' and accountno like 'EXT%'

-- DAFTAR TRANSAKSI ASET YANG BELUM MEMAKAI FORM ASET
select c.transactionno,c.actualdate,c.inputer,br.branchname,c.description,
sum(amount_debit * nilai_kurs),sum(amount_credit* nilai_kurs)
FROM
accounting.account ac,
accounting.JOURNAL b,
transaction.branch br,
accounting.JOURNALITEM a
left outer join transaction.transaction c
on (c.journalblockid = a.id_journalblock)
WHERE a.fl_account = ac.account_code and A.FL_JOURNAL = B.JOURNAL_NO AND 
(B.JOURNAL_DATE >= '2011-01-01' AND B.JOURNAL_DATE < '2012-01-01' )
and fl_account in ('1220101','1220102','1220103','1220104','1220201','1220202','1220203','1220204')
and c.transactioncode='CO'
and br.branchcode=c.branchcode
group by c.transactionno, c.actualdate,c.inputer,br.branchname,c.description
order by br.branchname, actualdate;

drop table transaction.listtransaction ;
create table transaction.listtransaction as
select c.transactionno
FROM
accounting.account ac,
accounting.JOURNAL b,
transaction.branch br,
accounting.JOURNALITEM a
left outer join transaction.transaction c
on (c.journalblockid = a.id_journalblock)
WHERE a.fl_account = ac.account_code and A.FL_JOURNAL = B.JOURNAL_NO AND 
(B.JOURNAL_DATE >= '2011-01-01' AND B.JOURNAL_DATE < '2012-01-01' )
and fl_account in ('1220101','1220102','1220103','1220104','1220201','1220202','1220203','1220204')
and c.transactioncode='CO'
and br.branchcode=c.branchcode ;
alter table transaction.listtransaction  owner to transaction ;

--Select journalitem group by transaction transactioncode

select c.transactioncode, sum(amount_debit * nilai_kurs), sum(amount_credit * nilai_kurs)
FROM
accounting.account ac,
accounting.accounthierarchy ah ,
accounting.JOURNAL b,
accounting.JOURNALITEM a
left outer join transaction.transaction c
on (c.journalblockid = a.id_journalblock)
WHERE a.fl_account = ac.account_code and A.FL_JOURNAL = B.JOURNAL_NO 
AND ah.fl_childaccountcode = a.fl_account
and (B.JOURNAL_DATE >= '2011-01-01' AND B.JOURNAL_DATE < '2011-02-01' AND A.branch_code = '001')
and ah.fl_parentaccountcode in ('111')
group by c.transactioncode;

select c.transactionno
--, sum(amount_debit * nilai_kurs), sum(amount_credit * nilai_kurs)
FROM
accounting.account ac,
accounting.accounthierarchy ah ,
accounting.JOURNAL b,
accounting.JOURNALITEM a
left outer join transaction.transaction c
on (c.journalblockid = a.id_journalblock)
WHERE a.fl_account = ac.account_code and A.FL_JOURNAL = B.JOURNAL_NO 
AND ah.fl_childaccountcode = a.fl_account
and (B.JOURNAL_DATE >= '2011-01-01' AND B.JOURNAL_DATE < '2011-02-01' AND A.branch_code = '001')
and ah.fl_parentaccountcode in ('111')
and c.transactioncode='DT'

-- UPDATE GL INTERFACE ASET KELOLAAN DI PRODUK
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIZAK4','Account Penambahan Aset Dari Zakat','4610101','GLI_ZAKAT','ASSET_FROM_ZAKAT');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIZAK5','Account Penambahan Aset Dari Infaq','4610201','GLI_ZAKAT','ASSET_FROM_INFAQ');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIZAK6','Account Penambahan Aset Dari Wakaf','4610301','GLI_ZAKAT','ASSET_FROM_WAKAF');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIZAK7','Account Penambahan Aset Dari Non Halal','4610501','GLI_ZAKAT','ASSET_FROM_NONHALAL');

insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIZAK8','Account Pengurangan Aset Dari Zakat','5610101','GLI_ZAKAT','ASSET_TO_ZAKAT');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIZAK9','Account Pengurangan Aset Dari Infaq','5610201','GLI_ZAKAT','ASSET_TO_INFAQ');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIZAK10','Account Pengurangan Aset Dari Wakaf','5610301','GLI_ZAKAT','ASSET_TO_WAKAF');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIZAK11','Account Pengurangan Aset Dari Non Halal','5610501','GLI_ZAKAT','ASSET_TO_NONHALAL');

insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROG15','Account Penambahan Aset Dari Zakat','4610101','GLI_PROGRAM','ASSET_FROM_ZAKAT');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROG16','Account Penambahan Aset Dari Infaq','4610201','GLI_PROGRAM','ASSET_FROM_INFAQ');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROG17','Account Penambahan Aset Dari Wakaf','4610301','GLI_PROGRAM','ASSET_FROM_WAKAF');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROG18','Account Penambahan Aset Dari Non Halal','4610501','GLI_PROGRAM','ASSET_FROM_NONHALAL');

insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROG19','Account Pengurangan Aset Dari Zakat','5610101','GLI_PROGRAM','ASSET_TO_ZAKAT');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROG20','Account Pengurangan Aset Dari Infaq','5610201','GLI_PROGRAM','ASSET_TO_INFAQ');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROG21','Account Pengurangan Aset Dari Wakaf','5610301','GLI_PROGRAM','ASSET_TO_WAKAF');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROG22','Account Pengurangan Aset Dari Non Halal','5610501','GLI_PROGRAM','ASSET_TO_NONHALAL');

insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROJ15','Account Penambahan Aset Dari Zakat','4610101','GLI_PROJECT','ASSET_FROM_ZAKAT');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROJ16','Account Penambahan Aset Dari Infaq','4610201','GLI_PROJECT','ASSET_FROM_INFAQ');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROJ17','Account Penambahan Aset Dari Wakaf','4610301','GLI_PROJECT','ASSET_FROM_WAKAF');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROJ18','Account Penambahan Aset Dari Non Halal','4610501','GLI_PROJECT','ASSET_FROM_NONHALAL');

insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROJ19','Account Pengurangan Aset Dari Zakat','5610101','GLI_PROJECT','ASSET_TO_ZAKAT');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROJ20','Account Pengurangan Aset Dari Infaq','5610201','GLI_PROJECT','ASSET_TO_INFAQ');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROJ21','Account Pengurangan Aset Dari Wakaf','5610301','GLI_PROJECT','ASSET_TO_WAKAF');
insert into transaction.parameterglobal (kode_parameter,deskripsi,nilai_parameter_string,tag,default_code)
values('GLIPROJ22','Account Pengurangan Aset Dari Non Halal','5610501','GLI_PROJECT','ASSET_TO_NONHALAL');

-- Update Transaction Penyerahan UM sumber dana amil jadi sumber dana infak
-- Untuk UM yang belum di LPJ kan dijadikan infaq semua kecuali Nama karyawan mbak fithri, silmi, rudi, amir
update transaction.transactionitem ti set parameterjournalid='AK-I'
where exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where mutationtype='D'
and t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.transactioncode='CA'
and t.branchcode='001'
and i.parameterjournalid = 'AK-A2'
and (c.returntransactionitemid is null or c.returntransactionitemid = 0)
and refaccountno not in ('CA.0109403','CA.0037563','CA.0102179','CA.0038070')
and ti.transactionitemid=i.transactionitemid);

update transaction.accounttransactionitem ti set fundentity=2
where exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where mutationtype='D'
and t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.transactioncode='CA'
and t.branchcode='001'
and c.fundentity = 4
and (c.returntransactionitemid is null or c.returntransactionitemid = 0)
and refaccountno not in ('CA.0109403','CA.0037563','CA.0102179','CA.0038070')
and ti.transactionitemid=i.transactionitemid);

-- UPDATE JURNAL LPJ UNTUK SUMBER DANA DARI AMIL

update transaction.transactionitem ti  set parameterjournalid='PAK-A2'
where exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where mutationtype='C'
and t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.transactioncode='CAR'
and i.parameterjournalid='PAK-A'
and t.isposted = 'F'
and actualdate between '2011-01-01' and '2011-12-31'
and ti.transactionitemid=i.transactionitemid);

-- Update data donatur yang masih salah
update transaction.transaction set donorid=82334 where donorno='00182334';
update transaction.accounttransactionitem ti set donorid=182334
where exists(
select 1 
from transaction.transactionitem i , transaction.transaction t, transaction.accounttransactionitem c
where mutationtype='C'
and t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and t.donorno='00182334'
and t.branchcode='001'
and ti.transactionitemid=i.transactionitemid)

-- Transaksi yang memiliki journalblockid redundan
drop table transaction.listtransaction;
create table transaction.listtransaction as
select journalblockid,count(*) from transaction.transaction 
where journalblockid is not null
group by journalblockid having count(*) > 1 ;
alter table transaction.listtransaction  owner to transaction;

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

select * from transaction.transactionbatch where description like '%SETIAINDAH_03/01/2011'

select * from transaction.transaction where batchid=8468