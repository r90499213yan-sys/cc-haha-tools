import winreg
HKCU = winreg.HKEY_CURRENT_USER

# 1. Delete BagMRU value 43
try:
    with winreg.OpenKey(HKCU, r'Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\BagMRU\2\1', 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE) as key:
        try:
            winreg.DeleteValue(key, '43')
            print('Deleted: BagMRU value 43')
        except OSError as e:
            print(f'BagMRU value 43: {e}')
except OSError as e:
    print(f'BagMRU key: {e}')

# 2. Delete TileProperties
def del_tree(base_key, path):
    with winreg.OpenKey(base_key, path, 0, winreg.KEY_ALL_ACCESS) as k:
        j = 0
        children = []
        while True:
            try:
                children.append(winreg.EnumKey(k, j))
                j += 1
            except OSError:
                break
        for child in children:
            del_tree(base_key, f'{path}\\{child}')
    winreg.DeleteKey(base_key, path)

try:
    del_tree(HKCU, r'Software\Microsoft\Windows\CurrentVersion\Start\TileProperties\W~com.aionui.app')
    print('Deleted: TileProperties')
except OSError as e:
    print(f'TileProperties: {e}')

# 3. CloudStore entries
cloud_keys = [
    r'Software\Microsoft\Windows\CurrentVersion\CloudStore\Store\DefaultAccount\Cloud\{c0e8bc6f-529d-4cca-b307-4b2962a40aba}$windows.data.apps.appleveltileinfo$appleveltilelist\windows.data.apps.appleveltileinfo$w~com.aionui.app',
    r'Software\Microsoft\Windows\CurrentVersion\CloudStore\Store\DefaultAccount\Current\{c0e8bc6f-529d-4cca-b307-4b2962a40aba}$windows.data.apps.appleveltileinfo$appleveltilelist\windows.data.apps.appleveltileinfo$w~com.aionui.app',
]
for ck in cloud_keys:
    try:
        del_tree(HKCU, ck)
        short = ck[-50:] if len(ck) > 50 else ck
        print(f'Deleted CloudStore: ...{short}')
    except OSError as e:
        print(f'CloudStore: {e}')

# 4. Classes\aionui - try recursive delete
try:
    del_tree(HKCU, r'Software\Classes\aionui')
    print('Deleted: Software\\Classes\\aionui')
except OSError as e:
    print(f'Classes\\aionui: {e} (needs admin)')

print('\nDone.')
