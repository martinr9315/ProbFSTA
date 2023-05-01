from parsing import investigate_parse, split_bank
import os

directory = 'CHILDESTreebank/hslld-hv1-er/'
filenames = ['CHILDESTreebank/brown-adam.parsed','CHILDESTreebank/valian+animacy+theta.parsed','CHILDESTreebank/brown-eve+animacy+theta.parsed']
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if os.path.isfile(f):
        filenames.append(f)
filenames.remove('CHILDESTreebank/hslld-hv1-er/.DS_Store')
for f in filenames:
    print(f)
    CHILDES_bank = investigate_parse([f])
    print('\n\n')
