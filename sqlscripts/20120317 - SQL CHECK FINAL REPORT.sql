-- KASUS KESALAHAN USER
-- * Menginput transaksi penyaluran dan penerimaan amil salah peruntukannya

-- Kasus yang perlu di cek
-- * journalblockid di transaksi yang double
-- * transaksi yang status isposted = 'T' tapi belum ada jurnalnya
-- * jurnal accounting yang tidak ada sumber data transaksinya
-- * mungkin ada amount jurnal yang ga sinkron dengan transaksinya
-- * Cek Transaksi yang nomor jurnalnya ga sama dengan batch transaksi
-- * Cek Transaksi yang nomor jurnalnya ga sama dengan batch transaksi
-- * Cek Transaksi yang belum digenerate jurnalnya
-- * Cek Tranasksi yang ekuivalenamountnya 0
-- * Cek transaksi amil yang melibatkan detail transaksi kas
-- * Cek Transaksi Temporary account

--## Cek Transaksi yang memiliki journalblockid redundan
select journalblockid,count(*) from transaction.transaction 
where journalblockid is not null
group by journalblockid having count(*) > 1 ;

--## Cek transaksi yang sudah posting tapi ga ada jurnalnya
select 
t.transactionno, ti.mutationtype ,
sum(case when ti.mutationtype ='D' then ti.ekuivalenamount else (-1 * ti.ekuivalenamount) end) as saldo
from transaction.financialaccount f,
    transaction.cashaccount c,
    transaction.accounttransactionitem ac,
    transaction.transactionitem ti,
    transaction.transaction t,
    transaction.transactiontype ty
where financialaccounttype = 'C'
and f.accountno = c.accountno
and ac.accountno = f.accountno
and ti.transactionitemid = ac.transactionitemid
and t.transactionid = ti.transactionid
and ty.transactioncode = t.transactioncode
and t.actualdate < '2012-01-01'
and c.cashaccounttype = 'A'
and t.isposted = 'T'
and t.transactionno not like 'BB%'
and not exists(
select 1 from accounting.journalitem ji where ji.id_journalblock=t.journalblockid)
group by
t.transactionno
,ti.mutationtype 

--## Cek Jurnal yang memiliki tidak memiliki sumber transaksi
select * from accounting.journalitem a where 
not exists (
select 1 from transaction.transaction c where c.journalblockid = a.id_journalblock
) and fl_journal not like '%MGR%';  

--hapus jurnal
delete from accounting.journalitem a where 
not exists (
select 1 from transaction.transaction c where c.journalblockid = a.id_journalblock
) and fl_journal not like '%MGR%';  


--## Cek Jumlah mutasi yang tidak cocok antara transaksi dan accounting
select 
     ji.description, ji.id_journalblock,ji.valuta_code,
     (ji.amount_debit * nilai_kurs) as debit,
     (ji.amount_credit * nilai_kurs) as credit
from 
      accounting.account ac, 
      accounting.accountinstance ai, 
      accounting.journal j, 
      accounting.journalitem ji ,
      accounting.accounthierarchy ah 
  where ai.accountinstance_id=ji.accountinstance_id 
    and ac.account_code = ai.account_code 
    and j.journal_no = ji.fl_journal 
    and ah.fl_childaccountcode=ai.account_code 
    and ah.fl_parentaccountcode in ('1110201' )
    and j.journal_date >= '2011-01-01'  and j.journal_date < '2011-01-31' 
    and ai.branch_code='001'
    and exists(
      select 1 from transaction.transactionitem ti
       where ti.transactionitemid = ji.source_key_id 
       and (ti.ekuivalenamount) <> (abs(ji.amount_debit - ji.amount_credit) * ji.nilai_kurs)
       and ti.accountcode='1110201'
     )
group by ji.source_key_id       
    
--## Cek Transaksi yang nomor jurnalnya ga sama dengan batch transaksi
drop table transaction.listtransaction ;
create table transaction.listtransaction as
select 
t.transactionno, ti.mutationtype ,
sum(case when ti.mutationtype ='D' then ti.ekuivalenamount else (-1 * ti.ekuivalenamount) end) as saldo
from transaction.financialaccount f,
    transaction.cashaccount c,
    transaction.accounttransactionitem ac,
    transaction.transactionitem ti,
    transaction.transaction t,
    transaction.transactiontype ty,
    transaction.transactionbatch tb
where tb.batchid = t.batchid
and financialaccounttype = 'C'
and f.accountno = c.accountno
and ac.accountno = f.accountno
and ti.transactionitemid = ac.transactionitemid
and t.transactionid = ti.transactionid
and ty.transactioncode = t.transactioncode
and t.isposted = 'T'
and t.transactionno not like 'BB%'
and not exists(
select 1 from accounting.journalitem ji where ji.id_journalblock=t.journalblockid
  and ji.fl_journal=tb.batchno)
group by
t.transactionno
,ti.mutationtype ;
alter table transaction.listtransaction  owner to transaction ;

-- ## Cek Transaksi yang belum digenerate jurnalnya
select * from transaction.transaction where isposted='F' and actualdate >= '2011-01-01' and actualdate < '2012-01-01';

-- ## Cek Transaksi yang ekuivalen amountnya 0
update transaction.transactionitem  set rate=1,ekuivalenamount=amount where rate = 0

-- ## Cek Transaksi yang melibatkan Kas di detail transaksi
select t.transactionno, t.description, br.branchname, t.inputer  from 
  transaction.transaction t, 
  transaction.branch br
where t.branchcode = br.branchcode
   and transactioncode = 'CO'
   and exists (
    select 1 from transaction.transactionitem ti
      where ti.transactionid = t.transactionid
        and transactionitemtype ='G'     
        and accountcode in ('1110101','1110201') 
        and mutationtype = 'D')     
order by t.branchcode   ;   

select t.transactionno, t.description, br.branchname, t.inputer  from 
  transaction.transaction t, 
  transaction.branch br
where t.branchcode = br.branchcode
   and transactioncode = 'CI'
   and exists (
    select 1 from transaction.transactionitem ti
      where ti.transactionid = t.transactionid
        and transactionitemtype ='G'     
        and accountcode in ('1110101','1110201') 
        and mutationtype = 'C')     
order by t.branchcode   ;  

-- ## CEK TRANSAKSI TEMPORARY ACCOUNT
select t.transactionno, t.description, br.branchname, t.inputer  from 
  transaction.transaction t, 
  transaction.branch br
where t.branchcode = br.branchcode
   and transactioncode = 'GT'
   and exists (
    select 1 from transaction.transactionitem ti
      where ti.transactionid = t.transactionid
        and transactionitemtype ='G'     
        and accountcode in ('9999999')
        )     
order by t.branchcode   ;  

--------------------------------------------------------------------

select c.transactioncode, sum(amount_debit * nilai_kurs), sum(amount_credit * nilai_kurs)
FROM
accounting.account ac,
accounting.accounthierarchy ah ,
accounting.JOURNAL b,
accounting.JOURNALITEM a,
transaction.transaction c
WHERE c.journalblockid = a.id_journalblock 
and a.fl_account = ac.account_code 
and A.FL_JOURNAL = B.JOURNAL_NO 
AND ah.fl_childaccountcode = a.fl_account
and (B.JOURNAL_DATE >= '2011-01-01' AND B.JOURNAL_DATE < '2011-12-31' AND A.branch_code = '001')
and ah.fl_parentaccountcode in ('1110101')
group by c.transactioncode;

--- QUERY DAFTAR SALDO KAS / BANK  UNTUK CABANG TERTENTU DAN RANGE TANGGAL TERTENTU
select 
--f.accountno,f.accountname, 
--sum(case when ti.mutationtype ='D' then ti.ekuivalenamount else (-1 * ti.ekuivalenamount) end) as saldo
t.transactioncode,ty.description,
sum (case when ti.mutationtype ='D' then ti.ekuivalenamount else 0.0 end) as saldo_debit,
sum (case when ti.mutationtype ='C' then ti.ekuivalenamount else 0.0 end) as saldo_credit
from transaction.financialaccount f,
    transaction.cashaccount c,
    transaction.accounttransactionitem ac,
    transaction.transactionitem ti,
    transaction.transaction t,
    transaction.transactiontype ty
where financialaccounttype = 'C'
and f.accountno = c.accountno
and ac.accountno = f.accountno
and ti.transactionitemid = ac.transactionitemid
and t.transactionid = ti.transactionid
and ty.transactioncode = t.transactioncode
and t.actualdate < '2011-01-01'
and f.branchcode='001'
--and f.currencycode = '000'
and c.cashaccounttype = 'A'
group by
--f.accountno,f.accountname
t.transactioncode,ty.description
order by 
f.accountno

select ti.* from transaction.transaction t, transaction.transactionitem ti
where t.transactionid=ti.transactionid 
and transactionno='KK-2011-112-BSM13-0000051';

-- QUERY DAFTAR SALDO DAILY BALANCE
select 
  /*
  ah.fl_parentaccountcode as account_code, 
	ai.accountinstance_id, ai.currency_code,
	d1.datevalue,
            case when BalanceCumulative is null then 0.0 
              else BalanceCumulative 
            end as BalanceCumulative, 
            case when BalanceCumulative_Ekuiv is null then 0.0 
              else BalanceCumulative_Ekuiv 
            end as BalanceCumulative_Ekuiv */
  sum (case when BalanceCumulative_Ekuiv is null then 0.0 
              else BalanceCumulative_Ekuiv 
            end) as BalanceCumulative_Ekuiv            
  from accounting.DailyBalance d1, (
    select  
      AccountInstance_ID, max(DateValue) as Tanggal
    from accounting.DailyBalance 
    where DateValue < '2012-01-01' 
    group by AccountInstance_ID 
  ) d2 , accounting.accountinstance ai , 
  accounting.account ac, accounting.accounthierarchy ah 
  where 
    ai.AccountInstance_ID = d1.AccountInstance_ID and 
    ac.account_code = ai.account_code and 
    ah.fl_childaccountcode=ai.account_code and 
    d1.AccountInstance_ID = d2.AccountInstance_ID and 
    d1.DateValue = d2.Tanggal and
    branch_code = '001' and
    ah.fl_parentaccountcode = '1110201'
group by ah.fl_parentaccountcode 
-- '2011-12-31'


-- Query mutasi akun untuk range tanggal tertentu
select sum(CASE 
                WHEN ac.account_type in ('A', 'X') THEN (ji.amount_debit - ji.amount_credit) * nilai_kurs
                  ELSE (ji.amount_credit - ji.amount_debit) * nilai_kurs 
              END )AS net_amount 
from 
      accounting.account ac, 
      accounting.accountinstance ai, 
      accounting.journal j, 
      accounting.journalitem ji ,
      accounting.accounthierarchy ah 
  where ai.accountinstance_id=ji.accountinstance_id 
    and ac.account_code = ai.account_code 
    and j.journal_no = ji.fl_journal 
    and ah.fl_childaccountcode=ai.account_code 
    and ah.fl_parentaccountcode in ('1110201')
    --and ai.branch_code='001'
    and j.journal_date < '2011-02-01';

22141539966.1754
20936387033.6054

select 
sum(case when ti.mutationtype ='D' then ti.ekuivalenamount else (-1 * ti.ekuivalenamount) end) as saldo
from transaction.financialaccount f,
    transaction.cashaccount c,
    transaction.accounttransactionitem ac,
    transaction.transactionitem ti,
    transaction.transaction t,
    transaction.transactiontype ty
where financialaccounttype = 'C'
and f.accountno = c.accountno
and ac.accountno = f.accountno
and ti.transactionitemid = ac.transactionitemid
and t.transactionid = ti.transactionid
and ty.transactioncode = t.transactioncode
and t.actualdate < '2011-02-01'
--and ti.branchcode='001'
and c.cashaccounttype = 'A'


select 
--transactionno ,
--f.accountno,f.accountname, 
--t.transactionno, ti.mutationtype ,
sum(case when ti.mutationtype ='D' then ti.ekuivalenamount else (-1 * ti.ekuivalenamount) end) as saldo
--t.transactioncode,ty.description,
--sum (case when ti.mutationtype ='D' then ti.ekuivalenamount else 0.0 end) as saldo_debit,
--sum (case when ti.mutationtype ='C' then ti.ekuivalenamount else 0.0 end) as saldo_credit
from transaction.financialaccount f,
    transaction.cashaccount c,
    transaction.accounttransactionitem ac,
    transaction.transactionitem ti,
    transaction.transaction t,
    transaction.transactiontype ty
where financialaccounttype = 'C'
and f.accountno = c.accountno
and ac.accountno = f.accountno
and ti.transactionitemid = ac.transactionitemid
and t.transactionid = ti.transactionid
and ty.transactioncode = t.transactioncode
and t.actualdate < '2011-03-01'
and ti.branchcode='001'
--and f.currencycode = '000'
and c.cashaccounttype = 'A'
group by
--f.accountno,f.accountname
transactionno
order by 
transactionno

select 
tran.transactionno,ekuivalenamount, 
(CASE 
		WHEN ac.account_type in ('A', 'X') THEN (ji.amount_debit - ji.amount_credit) * nilai_kurs
		  ELSE (ji.amount_credit - ji.amount_debit) * nilai_kurs 
	      END )AS net_amount 
from 
      accounting.account ac, 
      accounting.accountinstance ai, 
      accounting.journal j, 
      accounting.accounthierarchy ah ,
      accounting.journalitem ji      
      left outer join (
       select t.transactionid,t.transactionno, 
	  ti.amount,ti.ekuivalenamount, t.journalblockid,
	  ti.transactionitemid
       from transaction.transaction t, transaction.transactionitem ti
       where t.transactionid = ti.transactionid) tran
      on (ji.source_key_id = tran.transactionitemid)
  where ai.accountinstance_id=ji.accountinstance_id 
    and ac.account_code = ai.account_code 
    and j.journal_no = ji.fl_journal 
    and ah.fl_childaccountcode=ai.account_code 
    and ah.fl_parentaccountcode in ('1110201')
    and ai.branch_code='001'
    and j.journal_date < '2011-03-01'
    and not exists (select 1 from transaction.listtran l where l.transactionno=tran.transactionno)
  order by transactionno
    ;

select * from transaction.listtran
create table transaction.listtran as 
select 
ti.accountcode,
t.transactioncode,
--transactionno,
--f.accountno,f.accountname, 
--t.transactionno, ti.mutationtype ,
sum(case when ti.mutationtype ='D' then ti.ekuivalenamount else (-1 * ti.ekuivalenamount) end) as saldo
--t.transactioncode,ty.description,
--sum (case when ti.mutationtype ='D' then ti.ekuivalenamount else 0.0 end) as saldo_debit,
--sum (case when ti.mutationtype ='C' then ti.ekuivalenamount else 0.0 end) as saldo_credit
from transaction.financialaccount f,
    transaction.cashaccount c,
    transaction.accounttransactionitem ac,
    transaction.transactionitem ti,
    transaction.transaction t,
    transaction.transactiontype ty
where financialaccounttype = 'C'
and f.accountno = c.accountno
and ac.accountno = f.accountno
and ti.transactionitemid = ac.transactionitemid
and t.transactionid = ti.transactionid
and ty.transactioncode = t.transactioncode
and t.actualdate < '2011-02-01'
--and f.branchcode='001'
--and f.currencycode = '000'

select * from transaction.transaction
and c.cashaccounttype = 'A'
group by
--f.accountno,f.accountname
--transactionno
ti.accountcode,
t.transactioncode

---- TRANSAKSI RAK YANG ACCOUNTCODENYA SALAH
select 
ti.transactionitemid,ti.mutationtype, t.transactionno,t.transactioncode,transactiondate,actualdate, f.accountname,t.inputer
--sum (case when ti.mutationtype ='D' then ti.ekuivalenamount else 0.0 end) as saldo_debit,
--sum (case when ti.mutationtype ='C' then ti.ekuivalenamount else 0.0 end) as saldo_credit
from transaction.financialaccount f,
    transaction.cashaccount c,
    transaction.accounttransactionitem ac,
    transaction.transactionitem ti,
    transaction.transaction t,
    transaction.transactiontype ty
where financialaccounttype = 'C'
and f.accountno = c.accountno
and ac.accountno = f.accountno
and ti.transactionitemid = ac.transactionitemid
and t.transactionid = ti.transactionid
and ty.transactioncode = t.transactioncode
and c.cashaccounttype = 'A'
and ti.accountcode <> '1110201'
order by ac.transactionitemid

select * 
from 
  transaction.accounttransactionitem ac
where exists
( select 1 from  
  transaction.transaction t,
  transaction.transactionitem t,


select * from transaction.transactionitem ti
where exists(
select 1 
from 
  transaction.transactionitem i , 
  transaction.transaction t, 
  transaction.accounttransactionitem c,
  transaction.cashaccount ca
where t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and c.accountno=ca.accountno
and mutationtype='D'
and t.transactioncode = 'TB'
--and t.transactionno = 'KK-2011-001-KKP01-0002215'
and ti.transactionitemid=i.transactionitemid
and ca.cashaccounttype = 'A')
order by ti.transactionitemid  

update transaction.transactionitem ti set accountcode = '1110201'
where exists(
select 1 
from 
  transaction.transactionitem i , 
  transaction.transaction t, 
  transaction.accounttransactionitem c,
  transaction.cashaccount ca
where t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and c.accountno=ca.accountno
and mutationtype='D'
and t.transactioncode = 'DT'
and ti.transactionitemid=i.transactionitemid
and ca.cashaccounttype = 'A')

select * from transaction.transactionitem where transactionitemid=370276


select 
  ji.fl_account ,
  ai.branch_code,
  sum(CASE 
                WHEN ac.account_type in ('A', 'X') THEN (ji.amount_debit - ji.amount_credit) * nilai_kurs
                  ELSE (ji.amount_credit - ji.amount_debit) * nilai_kurs 
              END )AS net_amount 
from 
      accounting.account ac, 
      accounting.accountinstance ai, 
      accounting.journal j, 
      accounting.journalitem ji ,
      accounting.accounthierarchy ah 
  where ai.accountinstance_id=ji.accountinstance_id 
    and ac.account_code = ai.account_code 
    and j.journal_no = ji.fl_journal 
    and ah.fl_childaccountcode=ai.account_code 
    and ah.fl_parentaccountcode in ('1110101','1110201')
    and j.journal_date < '2011-01-01'
 group by ji.fl_account ,ai.branch_code;




select br.branchcode,branchname, tran.saldo from transaction.branch br
left outer join (
select f.branchcode ,
sum(case when ti.mutationtype ='D' then ti.ekuivalenamount else (-1 * ti.ekuivalenamount) end) as saldo
from transaction.financialaccount f,
    transaction.cashaccount c,
    transaction.accounttransactionitem ac,
    transaction.transactionitem ti,
    transaction.transaction t    
where financialaccounttype = 'C'
and f.accountno = c.accountno
and ac.accountno = f.accountno
and ti.transactionitemid = ac.transactionitemid
and t.transactionid = ti.transactionid
and t.actualdate < '2011-02-01'
and c.cashaccounttype = 'A'
group by f.branchcode) tran
on (tran.branchcode = br.branchcode)
order by branchcode



and exists(
select 

select * from transaction.accounttransactionitem ti
where accountno='BA.001.501.00238.15'
and exists(
select 1 
from 
  transaction.transactionitem i , 
  transaction.transaction t, 
  transaction.accounttransactionitem c,
  transaction.cashaccount ca
where t.transactionid=i.transactionid
and i.transactionitemid=c.transactionitemid
and c.accountno=ca.accountno
and ti.transactionitemid=i.transactionitemid
and actualdate < '2011-01-01')
order by ti.transactionitemid  

select * from transaction.transaction where transactioncode ='TB' and branchcode='112'
update transaction.transaction set actualdate='2010-12-31' where transactionno='BB-CB-000-112'
select * from transaction.transactionitem where transactionid = 8060 and refaccountno='BA.001.501.00238.15'
grant select on accounting.branchlocation to transaction
--- CEK MUTASI ACCOUNTING 
	select 
	tran.transactioncode,tran.trandescription, ji.branch_code, br.branchname,
	--tran.transactionno, tran.transactionid ,
	--ac.account_code,journal_no,ji.journalitem_no,
	sum(ji.amount_debit * nilai_kurs) as debit ,
	sum(ji.amount_credit * nilai_kurs) as credit
	from 
	      accounting.account ac, 
	      accounting.accountinstance ai, 
	      accounting.journal j, 
	      accounting.accounthierarchy ah ,
	      accounting.branchlocation br,
	      accounting.journalitem ji 	      
	      left outer join (
	       select t.transactionid,t.transactionno,t.transactioncode, 
		  ti.amount,ti.ekuivalenamount, t.journalblockid,
		  ti.transactionitemid, ty.description as trandescription
	       from transaction.transaction t, transaction.transactionitem ti,
		  transaction.transactiontype ty
	       where t.transactionid = ti.transactionid
		  and ty.transactioncode = t.transactioncode
	       ) tran
	      on (ji.source_key_id = tran.transactionitemid)
	  where ai.accountinstance_id=ji.accountinstance_id 
	    and ac.account_code = ai.account_code 
	    and j.journal_no = ji.fl_journal 
	    and ah.fl_childaccountcode=ai.account_code 
	    and br.branch_code = ji.branch_code
	    and ah.fl_parentaccountcode in ('1110201','1110101')
	    and j.journal_date >= '2011-01-01' and j.journal_date < '2012-01-01'
	    --and tran.transactioncode ='CO'
	    --and ji.amount_debit > 0.0
	    --and not exists ( select 1 from transaction.transactiontype typ where typ.transactioncode=tran.transactioncode)
	  --group by tran.transactionno , tran.transactionid order by tran.transactionno  
	  group by tran.transactioncode,tran.trandescription,ji.branch_code,br.branchname 
	  order by ji.branch_code, tran.transactioncode
	  --group by ac.account_code,journal_no,ji.journalitem_no
    ;	

-- CEK MUTASI TRANSAKSI
        
	select 
	t.transactioncode,ty.description,
	--t.transactionno,
	sum (case when ti.mutationtype ='D' then ti.ekuivalenamount else 0.0 end) as saldo_debit,
	sum (case when ti.mutationtype ='C' then ti.ekuivalenamount else 0.0 end) as saldo_credit
	from transaction.financialaccount f,
	    transaction.cashaccount c,
	    transaction.accounttransactionitem ac,
	    transaction.transactionitem ti,
	    transaction.transaction t,
	    transaction.transactiontype ty
	where financialaccounttype = 'C'
	and f.accountno = c.accountno
	and ac.accountno = f.accountno
	and ti.transactionitemid = ac.transactionitemid
	and t.transactionid = ti.transactionid
	and ty.transactioncode = t.transactioncode
	and t.actualdate >= '2011-01-01' and t.actualdate < '2012-01-01'
	and ti.branchcode = '001'
	--and t.transactioncode ='CAR'
	--and t.transactionno='KK-2011-101-KBD01-0000363'
	--and mutationtype ='D'
	--and c.cashaccounttype = 'A'
	--group by t.transactionno order by t.transactionno
	group by t.transactioncode,ty.description order by t.transactioncode;

 select               t.transactioncode, ty.description, ti.branchcode, br.branchname,               sum (case when ti.mutationtype ='D' then ti.ekuivalenamount else 0.0 end) as saldo_debit,               sum (case when ti.mutationtype ='C' then ti.ekuivalenamount else 0.0 end) as saldo_credit               from transaction.financialaccount f,                   transaction.cashaccount c,                   transaction.accounttransactionitem ac,                   transaction.transactionitem ti,                   transaction.transaction t,                   transaction.transactiontype ty,                   transaction.branch br               where financialaccounttype = 'C'               and f.accountno = c.accountno               and ac.accountno = f.accountno               and ti.transactionitemid = ac.transactionitemid               and t.transactionid = ti.transactionid               and ty.transactioncode = t.transactioncode               and ti.branchcode = br.branchcode               and t.actualdate >= '2011-01-01' and t.actualdate < '2012-01-01'               group by ti.branchcode, t.transactioncode,ty.description,br.branchname               order by ti.branchcode, t.transactioncode       


select
  ai.ACCOUNT_CODE as AccountCode,
  case
    when sum(ji.AMOUNT_DEBIT) is null then 0.0
    else sum(ji.AMOUNT_DEBIT)
  end as sumdebit,
  case 
    when sum(ji.AMOUNT_CREDIT) is null then 0.0
    else sum(ji.AMOUNT_CREDIT)
  end as sumcredit,
  case 
    when sum(ji.AMOUNT_DEBIT * ji.NILAI_KURS) is null then 0.0
    else sum(ji.AMOUNT_DEBIT * ji.NILAI_KURS)
  end as sumdebit_ekuiv,
  case 
    when sum(ji.AMOUNT_CREDIT * ji.NILAI_KURS) is null then 0.0
    else sum(ji.AMOUNT_CREDIT * ji.NILAI_KURS)
  end as sumcredit_ekuiv
from 
  accounting.ACCOUNT ac,
  accounting.ACCOUNTINSTANCE ai,
  accounting.JOURNAL j,
  accounting.JOURNALITEM ji
where 
  ai.ACCOUNT_CODE >= '1110101'
  and ai.ACCOUNT_CODE <= '1120101'
  and ai.BRANCH_CODE = '001'
  and ai.ACCOUNT_CODE = ac.ACCOUNT_CODE
  and ac.IS_DETAIL = 'T'
  and ai.ACCOUNTINSTANCE_ID = ji.ACCOUNTINSTANCE_ID
  and ji.FL_JOURNAL = j.JOURNAL_NO
  and j.JOURNAL_DATE  >= '2011-01-01'
  and j.JOURNAL_DATE  < '2012-02-01'
group by 
  ai.ACCOUNT_CODE
order by 
  ai.ACCOUNT_CODE
)

select * from transaction.transaction where isposted='F' and actualdate >= '2011-01-01' and actualdate < '2012-01-01';

select * from accounting.journal where journal_no='IST.2011.01.0000054';
select * from accounting.journalitem where fl_journal='IST.2011.01.0000054';
"1110101";"IST.2011.01.0000054";11;0;1325000

select * from transaction.transactionitem where transactionitemid=4600;
select * from transaction.transaction where transactionid=2143
select * from transaction.transactiontype where transactioncode = 'TM'
select * from transaction.transaction where transactioncode = 'TM'
update transaction.transaction set transactioncode = 'GT' where transactioncode = 'TM'

select t.actualdate,t.transactionno, ti.* from 
  transaction.transaction t,
  transaction.transactionitem ti
where t.transactionid = ti.transactionid
and ti.Transactionitemtype = 'G' 
and glnumber='1110201'

select * from transaction.transactionbatch where batchid=2021
select * from transaction.transaction where transactionno='KK-2011-101-KBD01-0000363';
select * from transaction.transactionitem where transactionid = 42341


select * from transaction.transactionitem where transactionitemid=351271

select * from transaction.transaction where transactionid=42341

select * from transaction.transaction where journalblockid=38491
select * from accounting.journalitem where id_journalblock=72215
select * from transaction.transactiontype where transactioncode ='CAB'
update transaction.transactiontype  set transactioncode ='CARB' where transactioncode ='CAB';
update transaction.parameterinbox  set kodeinbox='CARB' where kodeinbox='CAB';
select * from transaction.parameterinbox 
delete from transaction.transactiontype  where transactioncode ='CARB';
insert into transaction.transactiontype values('CARB','PENGEMBALIAN UANG MUKA DENGAN REIMBURSE','KM',null);
insert into transaction.parameterinbox values('CARB','PENGEMBALIAN UANG MUKA DENGAN REIMBURSE','fCashAdvanceReturn','

select * from transaction.transactiontype 


select * from accounting.journalblock where id_journalblock = 74440
update accounting.journalblock set journal_no='IST.2011.05.0000337' where id_journalblock = 74440

select * from accounting.journalitem where fl_journal= 'IST.2011.10.0000646' and journalitem_no=5



select * from 
 transaction.transaction t,
 transaction.transactionitem ti
where t.transactionid=ti.transactionid
 and t.actualdate between '2011-01-01' and '2011-01-31'
 and ti.parameterjournalid = 'AK-Z'


select           ac.account_code, ac.account_name,           
	tran.transactioncode,tran.trandescription,            
	ji.branch_code, br.branchname,           
	sum(ji.amount_debit * nilai_kurs) as debit ,           
	sum(ji.amount_credit * nilai_kurs) as credit         
from                
   accounting.account ac,                
   accounting.accountinstance ai,                
   accounting.journal j,                
   accounting.accounthierarchy ah ,               
   accounting.branchlocation br,               
   accounting.journalitem ji               
   left outer join (                
      select t.transactionid,t.transactionno,t.transactioncode,              
         ti.amount,ti.ekuivalenamount, t.journalblockid,             
         ti.transactionitemid, ty.description as trandescription                
      from transaction.transaction t, transaction.transactionitem ti,             
         transaction.transactiontype ty                
      where t.transactionid = ti.transactionid             
        and ty.transactioncode = t.transactioncode                ) tran               
      on (ji.source_key_id = tran.transactionitemid)           
where ai.accountinstance_id=ji.accountinstance_id              
   and ac.account_code = ai.account_code              
   and j.journal_no = ji.fl_journal             
   and ah.fl_childaccountcode=ai.account_code             
   and br.branch_code = ji.branch_code             
   and j.journal_date >= '2011-01-01' and j.journal_date < '2011-02-01'              
   and ji.branch_code = '001'                  
   and exists ( select 1 from accounting.account where                               
   fl_CPA_AccountCode = '3110101'                               
   and account_code =ah.fl_parentaccountcode )            
group by tran.transactioncode, tran.trandescription,                    ji.branch_code, br.branchname,                    ac.account_code, ac.account_name           order by ji.branch_code, account_code, tran.transactioncode 

select * from accounting.journalitem where fl_account='5110102'
   and branch_code='001'
select * from accounting.accounthierarchy where fl_parentaccountcode='5110101'
   
select * from accounting.journal where journal_no='IST.2011.03.0000166'   
select * from accounting.account where                               
   fl_CPA_AccountCode = '3110101' 

select aci.ashnaf,sum(amount_debit) as amount from       accounting.journal j,       accounting.journalitem ji,       accounting.accountinstance ac,       accounting.journalblock jb,       transaction.transaction tr,       transaction.transactionitem ti,       transaction.accounttransactionitem aci     where  j.journal_no = ji.fl_journal         and ji.accountinstance_id = ac.accountinstance_id         and jb.id_journalblock=ji.id_journalblock         and jb.id_journalblock=tr.journalblockid         and tr.transactionid=ti.transactionid         and ti.mutationtype='D'         and aci.transactionitemid=ti.transactionitemid         and j.journal_date_posting between '2011-01-01' and '2011-02-01'         and ac.account_code = '5110101'         and aci.ashnaf is not null          and ac.branch_code='001'      group by ashnaf 

select ji.*,tr.transactionno from 
      accounting.journal j, 
      accounting.journalitem ji, 
      accounting.accountinstance ac, 
      accounting.journalblock jb, 
      transaction.transaction tr, 
      transaction.transactionitem ti, 
      transaction.accounttransactionitem aci 
    where  j.journal_no = ji.fl_journal 
        and ji.accountinstance_id = ac.accountinstance_id 
        and jb.id_journalblock=ji.id_journalblock 
        and jb.id_journalblock=tr.journalblockid 
        and tr.transactionid=ti.transactionid 
        and aci.transactionitemid=ti.transactionitemid 
        and j.journal_date_posting between '2011-01-01' and '2011-01-31' 
        and ac.account_code = '4510302' 
        and ac.branch_code='001'
select * from transaction.product where productcode='11901'
