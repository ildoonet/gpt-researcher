import signal


def handler(signum, frame):
    raise Exception("Timed out")

def run_with_timeout(func, timeout, *args):
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)
    try:
        result = func(*args)
    except Exception as e:
        raise e
    finally:
        signal.alarm(0)
    return result
