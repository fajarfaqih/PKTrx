SELECT
  i.AccountCode
  , i.BranchCode
  , i.CurrencyCode
  , i.MutationType
  , i.Rate
  , i.Amount
  , t.Amount as TransactAmount
  , (t.Amount - i.Amount) as TransactToItemAmount
  , (i.Amount - t.Amount) as ItemToTransactAmount
  , (i.Amount - f.UangMuka) as Hutang
--  , p.ProductId
  , d.NilaiAwal
  , d.TotalPenyusutan
  , c.GLIContainerId
  , f.UangMuka
FROM
  Transaction t,
  TransactionItem i,
  AccountTransactionItem a,
  DepreciableAsset d,
  FixedAsset f,
  AssetCategory c
--  ProductAccount p
WHERE
  t.TransactionId = i.TransactionId
  and i.TransactionItemId = a.TransactionItemId
  and i.TransactionItemId = %(TransactionItemId)d
  and a.AccountNo = d.AccountNo
  and d.AccountNo = f.AccountNo
  and f.AssetCategoryId = c.AssetCategoryId
--  and p.AccountNo = d.AccountNoProduct