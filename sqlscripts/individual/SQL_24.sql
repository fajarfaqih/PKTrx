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
  , p.ProductId
  , d.NilaiAwal
  , d.TotalPenyusutan
  , c.GLIContainerId
  , (fi.SellAmount - d.NilaiSisa) as ProfitAmount
  , (d.NilaiSisa - fi.SellAmount) as LostAmount
  , fi.SellAmount
FROM
  Transaction t,
  TransactionItem i,
  AccountTransactionItem a,
  DepreciableAsset d,
  FixedAsset f,
  AssetCategory c,
  ProductAccount p,
  FixedAssetTransactInfo fi 
WHERE
  t.TransactionId = i.TransactionId
  and i.TransactionItemId = a.TransactionItemId
  and i.TransactionItemId = %(TransactionItemId)d
  and a.AccountNo = d.AccountNo
  and d.AccountNo = f.AccountNo
  and f.AssetCategoryId = c.AssetCategoryId
  and p.AccountNo = d.AccountNoProduct
  and fi.TransactionItemId = a.TransactionItemId