"""Entrée du seul binaire Windows ; le lancement depuis les sources est inchangé."""
import ctypes
from ctypes import wintypes

# Inno demande une fermeture normale tant que ce processus existe. Le handle
# reste ouvert jusqu'à la fin du processus, sans arrêter d'autre instance.
kernel32=ctypes.WinDLL('kernel32',use_last_error=True)
kernel32.CreateMutexW.argtypes=(wintypes.LPVOID,wintypes.BOOL,wintypes.LPCWSTR)
kernel32.CreateMutexW.restype=wintypes.HANDLE
running_mutex=kernel32.CreateMutexW(None,False,'Local\\Trucabule.MonGPT.Running')
if not running_mutex:
    raise ctypes.WinError(ctypes.get_last_error())

from mon_gpt.__main__ import main

raise SystemExit(main())
