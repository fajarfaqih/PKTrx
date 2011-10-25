SELECT
  i.AccountCode
  , i.BranchCode
  , i.CurrencyCode
  , i.MutationType
  , i.Rate
  , i.Amount
  , i.Amount * ((100-a.PercentageOfAmil)/100) as PHPAmount
  , i.Amount * (a.PercentageOfAmil/100) as AmilAmount
  , i.Amount * i.Rate as EkuivAmount
  , i.Amount * ((100-a.PercentageOfAmil)/100) * i.Rate as EkuivPHPAmount
  , i.Amount * (a.PercentageOfAmil/100) * i.Rate as EkuivAmilAmount
  , p.ProductId
FROM
  Transaction t,
  TransactionItem i,
  AccountTransactionItem a,
  ProductAccount p
WHERE
  t.TransactionId = i.TransactionId
  and i.TransactionItemId = a.TransactionItemId
  and i.TransactionItemId = %(TransactionItemId)d
  and a.AccountNo = p.AccountNo

