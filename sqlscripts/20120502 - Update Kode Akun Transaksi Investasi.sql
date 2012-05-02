alter table transaction.investmentcategory rename gliontainerid to glicontainerid;

select transactioncode, t.description, ti.accountcode, t.actualdate, ac.accountno,
(select glm.accountcode from 
    transaction.investment i,
    transaction.investmentcategory ic,
    transaction.glinterfacecontainer gli,
    transaction.glinterfacemember glm
    where  i.accountno = ac.accountno
    and ic.InvestmentCatId = i.InvestmentCatId
    and gli.GLIContainerId = ic.GLIContainerId
    and glm.GLIContainerId = gli.GLIContainerId
    and glm.GLIMemberCode='INVEST_ACC')
from transaction.transaction t
, transaction.transactionitem ti
, transaction.accounttransactionitem ac
where t.transactionid = ti.transactionid
and ti.transactionitemid = ac.transactionitemid
and ti.accountcode='1170201' ;

update transaction.transactionitem ti set 
accountcode = 
(select glm.accountcode from 
    transaction.accounttransactionitem ac,
    transaction.investment i,
    transaction.investmentcategory ic,
    transaction.glinterfacecontainer gli,
    transaction.glinterfacemember glm
    where  ti.transactionitemid = ac.transactionitemid
    and i.accountno = ac.accountno
    and ic.InvestmentCatId = i.InvestmentCatId
    and gli.GLIContainerId = ic.GLIContainerId
    and glm.GLIContainerId = gli.GLIContainerId
    and glm.GLIMemberCode='INVEST_ACC')
where ti.accountcode='1170201' ;