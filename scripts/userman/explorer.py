import os, ConfigParser
from stat import *
from time import *

def sz_kb(file_sz):
  dm_val = divmod(file_sz, 1024)
  ret_sz = dm_val[0]
  if dm_val[1] > 0:
    ret_sz = ret_sz + 1
  
  return ret_sz

def get_dirconfig(config):
  cfgparser = ConfigParser.ConfigParser()
  appini_filename = config.HomeDir + 'application.ini'
  cfgparser.readfp(open(appini_filename))
  root_dir = cfgparser.get('SERVER_DIRECTORY', 'ROOT')
  enable_vdir = cfgparser.get('SERVER_DIRECTORY', 'ENABLEVIRTUALDIR')
  
  return [root_dir, enable_vdir]

def browsedir(pathstr):
  lof = os.listdir(pathstr)
  lof.sort()
  listfile = []
  listdir = []
  for fname in lof:
    is_dir = 0
    is_zip = 0
    pathname = '%s/%s' % (pathstr, fname)
    rstat = os.stat(pathname)
    sz = rstat[ST_SIZE]
    mode = rstat[ST_MODE]
    if S_ISDIR(mode):
      md_type = 'File Folder'
      is_dir = 1
    elif S_ISREG(mode) and (os.path.splitext(fname)[1]=='.zip'):
      md_type = '%s File' % (os.path.splitext(fname)[1])
      is_zip=1
    else:
      md_type = 'Unknown'
    mod_time = localtime(rstat[ST_MTIME])
    str_time = strftime('%m/%d/%Y %I:%M:%S %p', mod_time)
    ftuple = [fname, sz, md_type, is_dir, str_time]
    if is_dir == 1:
      listdir = listdir + [ftuple]
    else:
      listfile = listfile + [ftuple]

  return listdir + listfile
