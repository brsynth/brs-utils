"""
Created on June 16 2020

@author: Joan Hérisson
"""

from brs_utils.misc import (
    total_size,
    check_nb_args
)
from brs_utils.file import (
    download,
    compress_tar_gz,
    compress_gz,
    extract_gz,
    extract_tar_gz,
    extract_gz_to_string,
    download_and_extract_gz,
    download_and_extract_tar_gz,
    file_length,
    read_dict,
    chown_r,
    check_sha,
    check_file_size
)
from brs_utils.print import (
    print_OK,
    print_FAILED,
    print_start,
    print_progress,
    print_end
)
from brs_utils.list import (
    insert_and_or_replace_in_sorted_list,
    diff
)
from brs_utils.logger import (
    create_logger,
    add_arguments as add_logger_args,
)
from brs_utils._version import (
    __version__
)


# __all__ = (
#     'total_size', 'check_nb_args',
#     'file_length', 'download', 'read_dict',
#     'compress_tar_gz', 'compress_gz',
#     'extract_gz', 'extract_tar_gz', 'extract_gz_to_string',
#     'download_and_extract_gz', 'download_and_extract_tar_gz',
#     'print_OK', 'print_FAILED',
#     'insert_and_or_replace_in_sorted_list',
#     'create_logger'
# )
