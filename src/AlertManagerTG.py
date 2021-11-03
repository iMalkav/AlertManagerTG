# -*- coding: utf-8 -*-
import logging
import signal
import time
import sys

from app.config.settings import _config
from app.webapp.MainHandler import *




def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if raw_input("\nReally quit? (y/n)> ").lower().startswith('y'):
            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)

    # restore the exit gracefully handler here    
    signal.signal(signal.SIGINT, exit_gracefully)

def main():
    logging.basicConfig(format="%(asctime)s %(levelname)s\t%(name)s:%(message)s", level= _config._settings['global']['log_level'])
    logging.getLogger("server.worker").setLevel(_config.logLevel)
    app = make_app()
    app.listen(_config.webport)
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt as e:
      logging.warn("caught {}, stopping".format(str(e)))
      tornado.ioloop.IOLoop.instance().stop()

    


if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    main()