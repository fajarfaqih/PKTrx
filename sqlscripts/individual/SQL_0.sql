SELECT
    Kode_Account
    , Kode_Cabang
    , Kode_Cabang_Transaksi
    , Kode_Valuta
    , Kode_Valuta_RAK
    , Jenis_Mutasi
    , Kode_Kurs
    , Nilai_Kurs_Manual
    , Nilai_Mutasi
FROM
    DetilTransaksi D 
    , Transaksi T 
WHERE
    D.Id_Transaksi = T.Id_Transaksi 
    AND D.Id_Detil_Transaksi = %(ID_DETIL_TRANSAKSI)s
    
