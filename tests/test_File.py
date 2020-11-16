"""
Created on Jul 14 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from brs_utils import file_length, \
                      read_dict, \
                      download, \
                      compress_tar_gz, \
                      extract_gz, extract_tar_gz, extract_gz_to_string, \
                      download_and_extract_tar_gz
from tempfile  import NamedTemporaryFile, TemporaryDirectory
from filecmp   import cmp, cmpfiles
from pathlib   import Path
from hashlib   import sha256
from json      import dumps as json_dumps
from os        import path  as os_path
from os        import remove
from shutil    import copyfile

class Test_File(TestCase):

    DOWNLOAD_URL    = 'https://github.com/brsynth/brs-utils/raw/master/tests/data/data.tar.gz'
    DOWNLOAD_HASH   = '451f23622ee6df7b96648039db374e7baa8c41495e4dbf91dbf232950db65a13'
    DOWNLOAD_HASHES = {'test_rpSBML.py':    '2031eefaf7305428e10f5a3c6ab485085d69979b8be6a1e3b2e375349ec7b9bd',
                       'test_TotalSize.py': '6a81f09015f516b8cfed8f39badbac3380e758df625c0ce3b9c87a79745813e2',
                       'test_Download.py':  '504676268634b8c340a11e202b4d9c7cc08f9daea749f4c9cf5db9294772bc39'}
    TAR_GZ_FILE     = os_path.join('data', 'data.tar.gz')

    def test_empty_file(self):
        self.assertEqual(file_length('data/empty_file.txt'), 0)

    def test_1l_file(self):
        self.assertEqual(file_length('data/1l_file.txt'), 1)

    def test_100l_file(self):
        self.assertEqual(file_length('data/100l_file.txt'), 100)

    _d = {'a': 1, 'b': 2}

    def _create_file_from_dict(self, filename, dict):
        with open(filename, 'w') as f:
            f.write(json_dumps(dict))

    def test_readdict_ok(self):
        with TemporaryDirectory() as tempd:
            filename = tempd+'/dict'
            self._create_file_from_dict(filename, self._d)
            dict = read_dict(filename)
            self.assertDictEqual(dict, self._d)

    def test_download_with_filename(self):
        with NamedTemporaryFile() as tempf:
            download(Test_File.DOWNLOAD_URL,
                     tempf.name)
            self.assertEqual(
                sha256(Path(tempf.name).read_bytes()).hexdigest(),
                       Test_File.DOWNLOAD_HASH)

    def test_download_without_filename(self):
        oufile = download(Test_File.DOWNLOAD_URL)
        self.assertEqual(
            sha256(Path(oufile).read_bytes()).hexdigest(),
                   Test_File.DOWNLOAD_HASH)

    def test_compress_tar_gz_file(self):
        infile = os_path.join('data', '100l_file.txt')
        oufile = compress_tar_gz(infile,
                                 NamedTemporaryFile().name+'.tar.gz',
                                 delete=False)
        # Check if the original file still exists
        self.assertTrue(os_path.isfile(infile))
        # Check if extracted file is equal to original one
        with TemporaryDirectory() as tempd:
            extract_tar_gz(oufile, tempd)
            self.assertTrue(cmp(infile, os_path.join(tempd, '100l_file.txt')))
        remove(oufile)

    def test_compress_tar_gz_file_wo_outfile(self):
        infile = NamedTemporaryFile().name
        copyfile(os_path.join('data', '100l_file.txt'), infile)
        oufile = compress_tar_gz(infile,
                                 delete=False)
        # Check if the original file still exists
        self.assertTrue(os_path.isfile(infile))
        # Check if extracted file is equal to original one
        with TemporaryDirectory() as tempd:
            extract_tar_gz(oufile, tempd)
            self.assertTrue(cmp(infile, os_path.join(tempd, os_path.basename(infile))))
        remove(infile)
        remove(oufile)

    def test_compress_tar_gz_dir(self):
        # Create a temporary folder
        with TemporaryDirectory() as tempd:
            # Create a temporay file inside the temporary folder
            temp_file = NamedTemporaryFile(dir=tempd, delete=False)
            # Compress the temporary folder into a temporary tar.gz file
            oufile = compress_tar_gz(tempd,
                                     NamedTemporaryFile().name+'.tar.gz',
                                     delete=False)
            # Check if the original folder still exists
            self.assertTrue(os_path.isdir(tempd))
            # Check if extracted folder is equal to original one
            with TemporaryDirectory() as tempd_2:
                # Extract the arcive in a temporary folder
                extract_tar_gz(oufile, tempd_2)
                # Set some variables for readness
                indir        = tempd
                outdir       = os_path.join(tempd_2, os_path.basename(tempd))
                files_to_cmp = [os_path.join(outdir, os_path.basename(temp_file.name))]
                # Compare files within both original and extracted folders
                cmp_result  = cmpfiles(indir, outdir, files_to_cmp)
                # The first element is the list of files that match,
                # so it must be equal to list of files passed to 'cmpfiles()'
                self.assertEqual(cmp_result[0], files_to_cmp)
        remove(oufile)

    def test_compress_tar_gz_dir_delete(self):
        # Create a temporary folder
        with TemporaryDirectory() as tempd:
            # Create a temporay file inside the temporary folder
            temp_file = NamedTemporaryFile(dir=tempd, delete=False)
            # Compress the temporary folder into a temporary tar.gz file
            oufile = compress_tar_gz(tempd,
                                     NamedTemporaryFile().name+'.tar.gz',
                                     delete=True)
            # Check if the original folder does not exist anymore
            self.assertFalse(os_path.isdir(tempd))
        remove(oufile)

    def test_download_and_extract_tar_gz(self):
        with TemporaryDirectory() as tempd:
            download_and_extract_tar_gz(Test_File.DOWNLOAD_URL, tempd)
            for member in Test_File.DOWNLOAD_HASHES:
                self.assertEqual(Test_File.DOWNLOAD_HASHES[member],
                                 sha256(Path(os_path.join(tempd,member)).read_bytes()).hexdigest())

    def test_download_and_extract_tar_gz_member(self):
        _member = 'test_rpSBML.py'
        with TemporaryDirectory() as tempd:
            download_and_extract_tar_gz(Test_File.DOWNLOAD_URL, tempd, _member)
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
