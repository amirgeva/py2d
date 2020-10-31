import sys

arguments = []
flags = {}


def flag(name, takes_param, callback):
    flags[name] = (takes_param, callback)


def parse():
    n = len(sys.argv)
    i = 1
    while i < n:
        if sys.argv[i][0]=='-':
            flag = sys.argv[i][1:]
            if flag not in flags:
                raise RuntimeError(f"Invalid flag {flag}")
            takes_param, cb = flags.get(flag)
            if takes_param:
                if i==(n-1):
                    raise RuntimeError(f"Missing param for flag -{flag}")
                i = i + 1
                cb(sys.argv[i])
            else:
                cb()
        else:
            arguments.append(sys.argv[i])
        i = i + 1
