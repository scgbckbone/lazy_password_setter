import logging


def get_me_logger(name, path, form=None, stream=False, level=40):
    l = logging.getLogger(name)
    l.setLevel(logging.DEBUG)
    fh = logging.FileHandler(path)
    fh.setLevel(level)
    if not format:
        frmtr = '%(asctime)s %(levelname)s %(message)s'
    else:
        frmtr = form
    formatter = logging.Formatter(frmtr)

    fh.setFormatter(formatter)
    l.addHandler(fh)

    if stream:
        sh = logging.StreamHandler()
        sh.setFormatter(frmtr)
        sh.setLevel(logging.DEBUG)
        l.addHandler(sh)

    return l
