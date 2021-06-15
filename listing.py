import os
from termcolor import colored
from time import sleep


with open('listing.txt', 'w') as listing:
    for r, _, _f in os.walk('.'):
        for f in _f:
            if r[0:3] == './.' or f[0] == '.' or f.endswith('.pyc') or f.endswith('.db'):
                continue

            with open(os.path.join(r, f), 'r') as file:
                try:
                    content = ['-' * 80, '\n', os.path.join(r, f), '\n'] + list(i for i in file.readlines() if i != '')
                except Exception as e:
                    print(colored(str(e) + os.path.join(r, f), 'red'))
                    continue

            listing.writelines(content)

