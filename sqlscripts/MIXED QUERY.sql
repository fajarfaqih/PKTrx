select * from transaction.transaction where transactionid in (
select transactionid from transaction.transactionitem where amount=ekuivalenamount and currencycode != '000' and amount != 0
)

SELECT A.TRANSACTIONITEMID,C.TRANSACTIONNO
FROM
transaction.ACCOUNTTRANSACTIONITEM A,
transaction.TRANSACTIONITEM B,
transaction.TRANSACTION C
WHERE A.TransactionItemId = B.TransactionItemId AND 
B.TRANSACTIONID = C.TRANSACTIONID AND 
(A.ACCOUNTNO = 'BC.001.411' AND C.TRANSACTIONCODE = 'TB')


select sum(case when i.mutationtype='D' then i.EkuivalenAmount                            
    else -i.EkuivalenAmount                       end) as Total         
    from transaction.accounttransactionitem a,  transaction.cashaccount c, transaction.financialaccount f, 
    transaction.transaction t , transaction.transactionitem i         
  where a.TransactionItemId = i.TransactionItemId           
     and i.TransactionId = t.TransactionId           
     and f.accountno = c.accountno 
     and .accountno = c.accountno           
     and t.ActualDate < '2011-01-01'           and f.BranchCode = '001'


select a.*,
  (select volunteername 
    from transaction.volunteertransaction vt , 
         transaction.volunteer v
     where v.volunteerid = vt.volunteerid
        and vt.transactionitemid = a.transactionitemid
  ) as volunteername
from transaction.transactionitem a 
where not exists 
  ( select 1 from transaction.volunteertransaction vt 
    where vt.transactionitemid = a.transactionitemid 
    ) limit 1

select sum(i.ekuivalenamount) as BeginBalance     
from transactionitem i, 
 accounttransactionitem a, 
 transaction t , 
 branch b , 
 productaccount p     
 where i.transactionitemid = a.transactionitemid       
 and i.transactionid = t.transactionid       
 and p.accountno = a.accountno       
 and a.FundEntity = 5       
 and t.actualdate < '2011-01-01'       and i.mutationtype = 'C'       and b.branchcode = i.branchcode       and a.Accounttitype = 'D'    and i.BranchCode='001' 

select * from transaction.bsz

select * from transaction.bsztransaction where bszid=16

select * from transaction.transaction where transactionid=1760
select * from transaction.transactionitem where transactionitemid=3710

select * from transaction.transactionbatch where inputer='OP001'
select * from transaction.transaction where batchid=6779

select * from sdm_employee where id=44485