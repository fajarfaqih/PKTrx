-- Kasus yang perlu di cek
-- * journalblockid di transaksi yang double
-- * transaksi yang status isposted = 'T' tapi belum ada jurnalnya
-- * jurnal accounting yang tidak ada sumber data transaksinya
-- * mungkin ada amount jurnal yang ga sinkron dengan transaksinya


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