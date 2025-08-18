#!/usr/bin/python
# coding=utf8
import logging
import logging.handlers

import re
import socket

BASIC_FORMAT = "%(asctime)s:%(levelname)s - %(lineno)s: %(message)s"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
__LOG_FORMAT__ = '%(node)s - %(asctime)s - %(process)s:%(thread)s - %(name)s - %(levelname)s - %(lineno)s: %(message)s'
__loggers__ = dict()

# __log_server = "http://192.168.100.44:8998/executor/log/write"
# __log_server = "http://192.168.1.19:8998/executor/log/write"
# __log_server = "http://192.168.1.19:3000/executor/log/write"
# __executor_node = "192.168.1.19:8080"
__log_server = None
__executor_node = None
log = logging.getLogger("common_log")
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())


class NodeFilter(logging.Filter):

    def __init__(self, name='', node=None):
        super(NodeFilter, self).__init__(name)
        self.node = node

    def filter(self, record):
        record.node = self.node
        return True


def getLogger(name):
    """
    proxy to log
    :param name: file name
    :return: logger
    """
    logger = logging.getLogger(name)
    if logger.getEffectiveLevel() == 30:
        logger.setLevel(logging.INFO)
    formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
    chlr = logging.StreamHandler()
    chlr.setFormatter(formatter)
    logger.addHandler(chlr)
    return logger


def getLogger2(namespace):
    """
    log config for algorithm, only one log for every namespace
    :param namespace: algorithm __name__
    :return: logger    
    """
    _logger = __loggers__.get(namespace)
    if _logger is not None:
        return _logger
    _logger = logging.getLogger(namespace)
    _logger.addFilter(NodeFilter(node=__executor_node))
    _logger.propagate = False
    # stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(__LOG_FORMAT__))
    _logger.addHandler(stream_handler)
    # http handler
    __addHttpHandler(_logger, __log_server)
    _logger.setLevel(logging.INFO)
    __loggers__[namespace] = _logger
    # _logger = logging.LoggerAdapter(_logger, extra={'node': __executor_node})
    return _logger


def __addHttpHandler(logger, log_server):
    http_handler = None
    for hand in logger.handlers:
        if type(hand) is HTTPHandler:
            http_handler = hand
            break

    if log_server is not None:
        m = re.search(r'((\d{1,4}.){3}.\d{1,4}:\d+)', log_server)
        if m:
            ip = m.group()
            if __check_http_status(ip):
                if http_handler is None :
                    http_handler = HTTPHandler(
                        host=ip,  # '127.0.0.1:3000',
                        url=log_server.split(ip)[1],  # '/log',
                        method='POST' # method='POST'
                    )
                    logger.addHandler(http_handler)
                    log.info("create http handler for:" + logger.name)
                else:
                    # 是否需要断开重连
                    log.info ("exist http handler.")
    else:
        log.info ("log_server is None.")


def __check_http_status(log_server):
    """
    check log server is ok
    :param log_server: ip and prot, eg: 127.0.0.1:3000
    :return: boolean
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex((log_server.split(':')[0], int(log_server.split(':')[1])))
        if result == 0:
            return True
    except:
        pass
    return False


def check():
    """
    check handler and filter
    :return: None
    """
    for name in __loggers__:
        log.info ("check log of algorithm:" + name)
        _log = __loggers__.get(name)
        for ft in _log.filters:
            if type(ft) is NodeFilter:
                ft.node = __executor_node
        __addHttpHandler(_log, __log_server)


def debug(name, debug=False):
    _log = logging.getLogger(name)
    if debug is True or debug == 'true':
        _log.setLevel(logging.DEBUG)
    else:
        _log.setLevel(logging.INFO)


def debug2(name, debug=False):
    log.info ("update logger level[{}] on algorithm:".format(debug) + name)
    logger = __loggers__.get(name)
    if logger is None:
        log.info ("not found logger for " + name)
        return
    if debug is True or debug == 'true':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


def logging_config(disable=False):
    if disable:
        log.info("disable all algorithm logging.")
        for lg in __loggers__:
            lg.disabled = True
    else:
        log.info("enable all algorithm logging.")
        for lg in __loggers__:
            lg.disabled = False

class HTTPHandler(logging.Handler):
    """
    A class which sends records to a Web server, using either GET or
    POST semantics.
    """
    def __init__(self, host, url, method="GET", secure=False, credentials=None,
                 context=None):
        """
        Initialize the instance with the host, the request URL, and the method
        ("GET" or "POST")
        """
        logging.Handler.__init__(self)
        method = method.upper()
        if method not in ["GET", "POST"]:
            raise ValueError("method must be GET or POST")
        self.host = host
        self.url = url
        self.method = method
        self.secure = secure
        self.credentials = credentials
        self.context = context

    def mapLogRecord(self, record):
        """
        Default implementation of mapping the log record into a dict
        that is sent as the CGI data. Overwrite in your class.
        Contributed by Franz Glasner.
        """
        return record.__dict__

    def emit(self, record):
        """
        Emit a record.

        Send the record to the Web server as a percent-encoded dictionary
        """
        try:
            import requests
            requests.post("http://" + self.host + self.url, self.mapLogRecord(record))
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
