-- ## Cek Transaksi yang melibatkan Kas di detail transaksi
create table transaction.listtransa
select t.transactionno, t.actualdate, t.transactiondate, 
      t.description, br.branchname, t.inputer, ty.description, 
      refaccountno, refaccountname,
      accountcode, mutationtype, ti.description,
      ti.ekuivalenamount
from 
  transaction.transaction t, 
  transaction.branch br,
  transaction.transactiontype ty,
  transaction.transactionitem ti
where ty.transactioncode = t.transactioncode
   and t.branchcode = br.branchcode
   and ty.transactioncode = t.transactioncode
   and t.transactionid = ti.transactionid
   and t.transactioncode in ('CO', 'CI', 'GT') 
   and exists(
         select 1 from transaction.transactionitem ti
         where t.transactionid = ti.transactionid
          and transactionitemtype ='G'
          and (
             accountcode like '1%'
             or accountcode like '2%'
             --or accountcode like '113%'
           )
        )
order by t.branchcode, t.transactionno, accountcode ;

select * from transaction.MapAccount where oldaccount='11401';

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





