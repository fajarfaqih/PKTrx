import com.ihsan.foundation.pobjecthelper as phelper

# GLOBALS
corporate = None

def BeforeLogin(config, appid, userid, password):
    global corporate
    
    helper = phelper.PObjectHelper(config)
    corporate = helper.CreateObject('Corporate', 1)
    corporate.SetAutoResponseError()
    corporate.Login(str(userid).upper(), password)
    #corporate.Login(userid, password)
    #corporate.LocalLogin(userid, password)

    return 1

def AfterSuccessfulLogin(config, reclogin, password):
    global corporate

    corporate.AfterLogin()
    reclogin.dpcompress = 1
        
    if corporate.LoginContext.Status_Password == 0:
        reclogin.requirenewpassword = 1
    
    '''
    appObject = config.AppObject
    aVersion = appObject.GetClientVersionInfo()
    aValidVersion = (
        aVersion[0] > 3 or aVersion[0] == 3 and (
            aVersion[1] > 5 or aVersion[1] == 5 and (
                aVersion[2] > 0 or aVersion[2] == 0 and 
                    aVersion[3] > 15
            )
        )
    )
    
    if not aValidVersion:
        reclogin.WarnUserLevel = 1
        reclogin.WarnUserMessage = "Untuk optimasi aplikasi \n" \
            "anda direkomendasikan mendownload versi aplikasi client terbaru.\n"\
            "Hubungi kantor pusat."
    '''
    #langsung assign dengan menu Transaksi
    reclogin.autoinstallmenu = 1
    reclogin.automenuname = 'Transaksi'
    
def BeforeLogout(config): pass
    # Clear SessionBLOB table for this session

def OnGetUserInfo(config, userid, userinfo):
    helper = phelper.PObjectHelper(config)
    corporate = helper.CreateObject('Corporate')
    
    login_context = corporate.LoginContext
    userinfo[1] = login_context.Nama_User
    userinfo[2] = str(login_context.BranchId)
    userinfo[3] = login_context.Nama_Departemen
    userinfo[4] = login_context.Kode_Cabang
    userinfo[5] = login_context.Nama_Cabang
    userinfo[6] = '\n'.join(login_context.Ls_PeranUser)
    userinfo[7] = login_context.Tanggal_Perbarui
    #userinfo[7] = config.Now()

def AfterFailedLogin(config, appid, userid, password): pass
def BeforeChangePassword(config, new_password, confirm_password):
    helper = phelper.PObjectHelper(config)
    corporate = helper.CreateObject('Corporate')
    corporate.ChangeMyPassword(new_password)
    
    return 0
    
def AfterChangePassword(config, new_password): pass

def BeforeRestoreSession(config, sessionName):
    appObj = config.GetAppObject()
    if appObj.lookuprsession(sessionName):
        return

    helper = phelper.PObjectHelper(config)
    corporate = helper.CreateObject('Corporate')
    Password = 'a' #config.ModLibUtils.DecodeStr('aWtpcGFzc3dvcmQ=')
    if sessionName == 'corporate': 
        appObj.rlogin(
            config.GetGlobalSetting('RLOGIN_CORPORATE_HOST'), 
            config.GetGlobalSetting('RLOGIN_CORPORATE_APP'), 
            config.SecurityContext.UserId, 
            Password, 
            'corporate')
    
    elif sessionName == 'accounting':
        appObj.rlogin(
            config.GetGlobalSetting('RLOGIN_ACC_HOST'),
            config.GetGlobalSetting('RLOGIN_ACC_APP'), 
            config.SecurityContext.UserId, 
            Password, 
            'accounting')
