# The module of functions for logging.

from datetime import datetime
import re
import logging
from pathlib import Path, PurePath

from config_py import dir_name, LogCommonSettings, LogSpecificSettings


logger: logging.Logger | None = None    # Global variable for save only one instance of the logger
                                        # the command for use the logger in another module:
                                        #   <from logger import logger>

format_line = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class ColoredFormatter(logging.Formatter):
    '''
    Color illumination of the console logger
    '''
    COLORS = {'DEBUG': '\033[94m', 'INFO': '\033[92m', 'WARNING': '\033[93m',
              'ERROR': '\033[91m', 'CRITICAL': '\033[95m'}

    def format(self, record):
        log_fmt = f"{self.COLORS.get(record.levelname, '')}{format_line}\033[0m"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def _init_logging(log_common_set: LogCommonSettings, log_specific_set: LogSpecificSettings) -> str :
    '''
    Deploying the infrastructure for file logging
    :param log_common_set: settings applied to the logger from the common section of the configuration file
    :param log_specific_set: settings applied to the logger from the specific section of the configuration file
    :return: the file path and name for file logging
    '''
    prefix_name= log_specific_set.file_name_prefix
    path = PurePath.joinpath(dir_name, log_common_set.logs_folder_path)
    max_num_files = log_common_set.max_num_log_files

    new_log_name = (prefix_name + datetime.now().strftime('%Y-%m-%d_%H-%M') + '.log')

    if not Path(path).is_dir() :
        # Creating a log folder if it doesn't exist yet
        Path.mkdir(path)

    # Reading a log folder
    # Compiling "re"-pattern for the name of log
    regexp = re.compile(rf'{prefix_name}'+r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log')
    # Finding all of logs files
    list_logs = []
    for el in Path(path).iterdir() :
        if regexp.match(el.name, 0) :
            list_logs.append(el)
    # Sorting the log list by file creation time in reverse order
    list_logs.sort(reverse=True)
    if new_log_name in list_logs[:max_num_files] :
        start_pos = max_num_files
    else :
        start_pos = max_num_files - 1
    if list_logs[start_pos :] :
        for f in list_logs[start_pos :] :
            Path.unlink(f)

    return PurePath.joinpath(path, new_log_name)


def set_logger(log_common_set: LogCommonSettings, log_specific_set: LogSpecificSettings) -> logging.Logger :
    '''
    Logger instance creation function
    :param log_common_set: settings applied to the logger from the common section of the configuration file
    :param log_specific_set: settings applied to the logger from the specific section of the configuration file
    :return: logger instance
    '''
    global logger
    # Only one, the first launch
    if logger is None:
        # we get the basic logger
        logger = logging.getLogger(log_specific_set.name)

        # setting the logger level
        logger.setLevel(log_common_set.level)

        # configuring logger output to the console
        handler = logging.StreamHandler()
        formatter = ColoredFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        if log_common_set.to_file :
            # adding configuring logger output to the file (if specified)
            handler = logging.FileHandler(_init_logging(log_common_set, log_specific_set), encoding='utf-16')
            formatter = logging.Formatter(format_line)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    return logger

# set_logger(level=settings.logging.level_logging, to_file=settings.logging.to_file)
# logger.debug('Loading <config_py> module')
# logger.debug('Loading <logger> module')