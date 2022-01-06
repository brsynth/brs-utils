"""
Created on Jul 14 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from brs_utils import (
    file_length,
    read_dict,
    download,
    compress_tar_gz, compress_gz,
    extract_gz, extract_tar_gz, extract_gz_to_string,
    download_and_extract_tar_gz,
    download_and_unzip
)
from brs_utils.file import (
    compare_dir
)
from tempfile  import (
    NamedTemporaryFile,
    TemporaryDirectory,
    mkdtemp
)
from filecmp   import (
    cmp,
    cmpfiles,
    dircmp
)
from pathlib   import Path
from hashlib   import sha256
from json      import dumps as json_dumps
from os import (
    path as os_path,
    remove,
    stat
)
from shutil import (
    copyfile
)

class Test_File(TestCase):

    DOWNLOAD_TARGZ_URL    = 'https://github.com/brsynth/brs-utils/raw/master/tests/data/data.tar.gz'
    DOWNLOAD_ZIP_URL = 'https://github.com/brsynth/brs-utils/raw/master/tests/data/100l_file.txt.zip'
    DOWNLOAD_HASH   = '451f23622ee6df7b96648039db374e7baa8c41495e4dbf91dbf232950db65a13'
    DOWNLOAD_HASHES = {'test_rpSBML.py':    '2031eefaf7305428e10f5a3c6ab485085d69979b8be6a1e3b2e375349ec7b9bd',
                       'test_TotalSize.py': '6a81f09015f516b8cfed8f39badbac3380e758df625c0ce3b9c87a79745813e2',
                       'test_Download.py':  '504676268634b8c340a11e202b4d9c7cc08f9daea749f4c9cf5db9294772bc39'}
    DATA_FOLDER     = os_path.join(
        os_path.dirname(os_path.realpath(__file__)),
        'data'
    )
    TAR_GZ_FILE     = os_path.join(DATA_FOLDER, 'data.tar.gz')
    file_0l = os_path.join(DATA_FOLDER, 'empty_file.txt')
    file_1l = os_path.join(DATA_FOLDER, '1l_file.txt')
    file_100l = os_path.join(DATA_FOLDER, '100l_file.txt')

    def test_empty_file(self):
        self.assertEqual(file_length(self.file_0l), 0)

    def test_1l_file(self):
        self.assertEqual(file_length(self.file_1l), 1)

    def test_100l_file(self):
        self.assertEqual(file_length(self.file_100l), 100)

    _d = {'a': 1, 'b': 2}

    def _create_file_from_dict(self, filename, dict):
        with open(filename, 'w') as f:
            f.write(json_dumps(dict))

    def test_readdict_ok(self):
        with TemporaryDirectory() as tempd:
            filename = os_path.join(tempd, 'dict')
            self._create_file_from_dict(filename, self._d)
            dict = read_dict(filename)
            self.assertDictEqual(dict, self._d)

    def test_download_with_filename(self):
        download_f = download(
            Test_File.DOWNLOAD_TARGZ_URL
        )
        self.assertEqual(
            sha256(
                Path(download_f).read_bytes()).hexdigest(),
                Test_File.DOWNLOAD_HASH
            )
        remove(download_f)

    def test_download_without_filename(self):
        outfile = download(Test_File.DOWNLOAD_TARGZ_URL)
        self.assertEqual(
            sha256(
                Path(outfile).read_bytes()).hexdigest(),
                Test_File.DOWNLOAD_HASH
            )
        remove(outfile)

    def test_compress_tar_gz_file(self):
        infile = self.file_100l
        infile_t = os_path.basename(infile)
        oufile = compress_tar_gz(
            infile,
            NamedTemporaryFile().name+'.tar.gz',
            delete=False
        )
        # Check if the original file still exists
        self.assertTrue(os_path.isfile(infile))
        # Check if extracted file is equal to original one
        with TemporaryDirectory() as tempd:
            extract_tar_gz(oufile, tempd)
            self.assertTrue(
                cmp(
                    infile,
                    os_path.join(tempd, infile_t)
                )
            )
        remove(oufile)

    def test_compress_tar_gz_file_wo_outfile(self):
        infile = NamedTemporaryFile().name
        copyfile(self.file_100l, infile)
        oufile = compress_tar_gz(
            infile,
            delete=False
        )
        # Check if the original file still exists
        self.assertTrue(os_path.isfile(infile))
        # Check if extracted file is equal to original one
        with TemporaryDirectory() as tempd:
            extract_tar_gz(oufile, tempd)
            self.assertTrue(
                cmp(
                    infile,
                    os_path.join(
                        tempd,
                        os_path.basename(infile)
                    )
                )
            )
        remove(infile)
        remove(oufile)

    def test_compress_tar_gz_dir(self):
        oufile = compress_tar_gz(
            self.DATA_FOLDER,
            delete=False
        )
        # Check if the original folder still exists
        self.assertTrue(self.DATA_FOLDER)
        # Check if extracted folder is equal to original one
        with TemporaryDirectory() as tempd:
            # Extract the arcive in a temporary folder
            extract_tar_gz(
                file=oufile,
                dir=tempd,
                delete=False
            )
            comp = dircmp(
                os_path.join(
                    tempd,
                    os_path.basename(self.DATA_FOLDER)
                ),
                self.DATA_FOLDER
            )
            self.assertListEqual(
                [],
                comp.diff_files
            )
        remove(oufile)

    def test_compress_tar_gz_dir_delete(self):
        tempdir = mkdtemp()
        # Compress the temporary folder into a temporary tar.gz file
        outfile = compress_tar_gz(
            tempdir,
            delete=True
        )
        # Check if the original folder does not exist anymore
        self.assertFalse(os_path.exists(tempdir))
        remove(outfile)

    def test_compress_gz(self):
        infile = self.file_100l
        infile_t = os_path.basename(infile)
        infile_temp = NamedTemporaryFile().name
        copyfile(infile, infile_temp)
        outfile     = compress_gz(infile_temp)
        # Check if the original file still exists
        self.assertTrue(os_path.isfile(infile_temp))
        # Check if outfile is well named
        self.assertEqual(outfile, infile_temp+'.gz')
        # Check if extracted file is equal to original one
        with TemporaryDirectory() as tempd:
            self.assertTrue(cmp(infile, extract_gz(outfile, tempd)))
        remove(outfile)
        remove(infile_temp)

    def test_compress_gz_delete(self):
        infile = self.file_100l
        infile_t = os_path.basename(infile)
        infile_temp = NamedTemporaryFile().name
        copyfile(infile, infile_temp)
        outfile     = compress_gz(infile_temp, delete=True)
        # Check if the original file does not exist anymore
        self.assertTrue(not os_path.isfile(infile_temp))
        # Check if outfile is well named
        self.assertEqual(outfile, infile_temp+'.gz')
        # Check if extracted file is equal to original one
        with TemporaryDirectory() as tempd:
            self.assertTrue(cmp(infile, extract_gz(outfile, tempd)))
        remove(outfile)

    def test_compress_gz_with_outFile(self):
        infile = self.file_100l
        infile_t = os_path.basename(infile)
        outfile_temp = NamedTemporaryFile().name
        outfile      = compress_gz(infile, outfile_temp)
        # Check if the original file still exists
        self.assertTrue(os_path.isfile(infile))
        # Check if outfile is well named
        self.assertEqual(outfile, outfile_temp)
        # Check if extracted file is equal to original one
        with TemporaryDirectory() as tempd:
            self.assertTrue(cmp(infile, extract_gz(outfile, tempd)))
        remove(outfile)

    def test_download_and_unzip(self):
        with TemporaryDirectory() as tempd:
            download_and_unzip(Test_File.DOWNLOAD_ZIP_URL, tempd)
            self.assertEqual(
                2300,
                stat(os_path.join(tempd, '100l_file.txt')).st_size
            )

    def test_download_and_extract_tar_gz(self):
        with TemporaryDirectory() as tempd:
            download_and_extract_tar_gz(Test_File.DOWNLOAD_TARGZ_URL, tempd)
            for member in Test_File.DOWNLOAD_HASHES:
                self.assertEqual(
                    Test_File.DOWNLOAD_HASHES[member],
                    sha256(Path(os_path.join(tempd,member)).read_bytes()).hexdigest()
                )

    def test_download_and_extract_tar_gz_member(self):
        _member = 'test_rpSBML.py'
        with TemporaryDirectory() as tempd:
            download_and_extract_tar_gz(Test_File.DOWNLOAD_TARGZ_URL, tempd, _member)
            for member in Test_File.DOWNLOAD_HASHES:
                m = os_path.join(tempd, member)
                if member == _member:
                    self.assertEqual(Test_File.DOWNLOAD_HASHES[_member],
                                     sha256(Path(m).read_bytes()).hexdigest())
                else:
                    self.assertFalse(Path(m).exists())

    def test_extract_gz(self):
        with TemporaryDirectory() as tempd:
            extract_gz(Test_File.TAR_GZ_FILE, tempd)
            self.assertEqual(
                sha256(Path(os_path.join(tempd, 'data.tar')).read_bytes()).hexdigest(),
                'd3eb1c4b3604e6863fb4c4da930b4df74217fcf95c78439bc721ea83ce280f19'
                            )

    def test_extract_gz_to_string(self):
        s = extract_gz_to_string(Test_File.TAR_GZ_FILE)
        self.assertEqual(
            sha256(s.encode()).hexdigest(),
            'd3eb1c4b3604e6863fb4c4da930b4df74217fcf95c78439bc721ea83ce280f19'
                        )

    def test_extract_tar_gz_file(self):
        with TemporaryDirectory() as tempd:
            extract_tar_gz(Test_File.TAR_GZ_FILE, tempd, 'test_rpSBML.py')
            self.assertEqual(
                sha256(Path(os_path.join(tempd, 'test_rpSBML.py')).read_bytes()).hexdigest(),
                '2031eefaf7305428e10f5a3c6ab485085d69979b8be6a1e3b2e375349ec7b9bd'
                            )
            self.assertFalse(Path(os_path.join(tempd, 'test_Download.py')).exists())

    def test_extract_tar_gz(self):
        with TemporaryDirectory() as tempd:
            extract_tar_gz(Test_File.TAR_GZ_FILE, tempd)
            self.assertEqual(
                sha256(Path(os_path.join(tempd, 'test_Download.py')).read_bytes()).hexdigest(),
                '504676268634b8c340a11e202b4d9c7cc08f9daea749f4c9cf5db9294772bc39'
                            )

    def test_compare_dir(self):
        self.assertTrue(
            compare_dir(
                os_path.join(self.DATA_FOLDER, 'dir.a'),
                os_path.join(self.DATA_FOLDER, 'dir.a'),
                recursive=True
            )
        )
        self.assertTrue(
            compare_dir(
                os_path.join(self.DATA_FOLDER, 'dir.b'),
                os_path.join(self.DATA_FOLDER, 'dir.b'),
                recursive=True
            )
        )
        self.assertTrue(
            compare_dir(
                os_path.join(self.DATA_FOLDER, 'dir.b'),
                os_path.join(self.DATA_FOLDER, 'dir.c'),
                recursive=False
            )
        )
        self.assertFalse(
            compare_dir(
                os_path.join(self.DATA_FOLDER, 'dir.b'),
                os_path.join(self.DATA_FOLDER, 'dir.c'),
                recursive=True
            )
        )
        self.assertFalse(
            compare_dir(
                os_path.join(self.DATA_FOLDER, 'dir.b'),
                os_path.join(self.DATA_FOLDER, 'dir.d'),
                recursive=True
            )
        )
