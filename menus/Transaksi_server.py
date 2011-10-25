import com.ihsan.foundation.pobjecthelper as phelper

def OnLoadMenu(config, menu):
    helper = phelper.PObjectHelper(config)
    userid = config.SecurityContext.userid

    if userid.upper() == 'ROOT':
        statusmsg = ' [SUPERUSER]'
    else:
        corporate = helper.CreateObject('Corporate')
        login_context = corporate.LoginContext

        statusmsg = ' [%s]  cabang: %s[%s]' % (
            login_context.Nama_User,
            login_context.Kode_Cabang,
            login_context.Nama_Cabang)


    str_today = config.FormatDateTime('dddd, dd mmmm yyyy', \
        config.ModLibUtils.Now())
    wholeMessage = statusmsg + '   tanggal: ' + str_today

    #nambah nama file config/basisdata yang sedang dipakai
    namaConfig = config.GetGlobalSetting('ConfigName')
    if namaConfig == 'DEV':
      namaConfig = '[DEMO]'
    if namaConfig == 'DEFAULT':
      namaConfig = '[PRODUCTION]'
    wholeMessage = wholeMessage + '  konfigurasi: ' + namaConfig

    #expressing the live....
    menu.StatusBarMessage = wholeMessage
