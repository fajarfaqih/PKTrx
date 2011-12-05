select * from (select transactionid,transactionno,
  (select sum(ekuivalenamount) from transaction.transactionitem b
    where a.transactionid=b.transactionid and mutationtype = 'D') debet,
  (select sum(ekuivalenamount) from transaction.transactionitem b
    where a.transactionid=b.transactionid and mutationtype = 'C') credit
from transaction.transaction a ) as transactiontotal
where debet <> credit

select * from 

  (select sum(ekuivalenamount) from transaction.transactionitem b
    where a.transactionid=b.transactionid and mutationtype = 'D') debet,
  (select sum(ekuivalenamount) from transaction.transactionitem b
    where a.transactionid=b.transactionid and mutationtype = 'C') credit
select transactionid,transactionno,transactioncode,branchcode
from transaction.transaction a   where transactioncode='CAR'


create table transaction.transactiontotal as 
select transactionid,
    sum(case when mutationtype = 'D' then ekuivalenamount else 0.0 end) as debet,
    sum(case when mutationtype = 'C' then ekuivalenamount else 0.0 end) as credit
    from transaction.transactionitem b
    group by transactionid
    

select * from transaction.transactionitem where transactionid=115732    

select transactioncode,
       transactionno,
       a.transactionid,
       description,
       debet,credit,
       actualdate,
       transactiondate,
       inputer
from transaction.transaction a , transaction.transactiontotal b where a.transactionid=b.transactionid and debet <> credit
and transactioncode not in ('CAR','FA','INVC') order by inputer,actualdate

select * from transaction.transaction where transactionno='KM-2011-001-KKP01-0001421'

select * from transaction.cashadvancereturninfo where sourcetransactionid=15183

select * from enterprise.userapp where kode_cabang='111'

select * from enterprise.userapp where id_user='RIZKANADYA'
update enterprise.userapp set status_profil='A' where id_user='RIZKANADYA'

select* from transaction.transactiontype where transactioncode not in (
select kodeinbox from transaction.parameterinbox)

select * from transaction.parameterinbox
insert into transaction.parameterinbox values()

select * from transaction.transactionitem where transactionid=11853
