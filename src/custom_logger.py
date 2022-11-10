import logging


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    log_form_def = '[%(levelname)s] :: %(name)s ::  %(message)s'
    log_form_ext = '%(asctime)s  [%(levelname)s] :: %(name)s :: %(funcName)s:%(lineno)d :: %(message)s'
    # format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + log_form_ext + reset,
        logging.INFO: grey + log_form_ext + reset,
        logging.WARNING: yellow + log_form_def + reset,
        logging.ERROR: red + log_form_def + reset,
        logging.CRITICAL: bold_red + log_form_def + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def customize_logger(logger:logging.Logger, level_ch, level_fh, file_fh):
    if file_fh and level_fh is not None:
        x = 1
    if level_ch is not None:
        ch = logging.StreamHandler()
        ch_cfm = CustomFormatter()
        if level_ch == 'debug':
            ch.setLevel(logging.DEBUG)
        elif level_ch == 'info':
            ch.setLevel(logging.INFO)
        elif level_ch == 'warning':
            ch.setLevel(logging.WARNING)
        elif level_ch == 'error':
            ch.setLevel(logging.ERROR)
        elif level_ch == 'critical':
            ch.setLevel(logging.CRITICAL)
        ch.setFormatter(ch_cfm)
        logger.addHandler(ch)

        logger.setLevel(logging.DEBUG)
        logger.propagate = False



