#! /usr/bin/env python
"""
Southern California Earthquake Center Broadband Platform
Copyright 2010-2016 Southern California Earthquake Center

These are acceptance tests for the bbcoda2.py
$Id: test_uc_site.py 1736 2016-09-13 19:11:24Z fsilva $
"""
from __future__ import division, print_function

# Import Python modules
import os
import shutil
import unittest

# Import Broadband modules
import cmp_bbp
import seqnum
import bband_utils
from install_cfg import InstallCfg
from uc_site_cfg import UCSiteCfg
from uc_site import UCSite

class TestUCSite(unittest.TestCase):
    """
    Acceptance Test for UC_site. This assumes the acceptance test calling
    script runs the basic executable.
    """

    def setUp(self):
        """
        Set up unit test
        """
        self.install = InstallCfg()
        self.r_velocity = "labasin.vel"
        self.r_stations = "one_stat.txt"
        self.r_src = "test_wh_ucsb.src"
        self.r_srf = "test_ucsb.srf"
        self.sim_id = int(seqnum.get_seq_num())
        a_indir = os.path.join(self.install.A_IN_DATA_DIR, str(self.sim_id))
        a_tmpdir = os.path.join(self.install.A_TMP_DATA_DIR, str(self.sim_id))
        a_outdir = os.path.join(self.install.A_OUT_DATA_DIR, str(self.sim_id))
        a_logdir = os.path.join(self.install.A_OUT_LOG_DIR, str(self.sim_id))

        #
        # Make sure output directories exist
        #
        bband_utils.mkdirs([a_indir, a_tmpdir, a_outdir, a_logdir],
                           print_cmd=False)

        # Copy files
        a_refdir = os.path.join(self.install.A_TEST_REF_DIR, "ucsb")

        # Copy seismogram
        shutil.copy2(os.path.join(a_refdir, "s01.3comp"), a_tmpdir)

        # Copy other input files
        shutil.copy2(os.path.join(a_refdir, self.r_stations), a_indir)
        shutil.copy2(os.path.join(a_refdir, self.r_velocity), a_indir)
        shutil.copy2(os.path.join(a_refdir, self.r_src), a_indir)
        shutil.copy2(os.path.join(a_refdir, self.r_srf), a_indir)

        # Change directory to tmpdir
        os.chdir(a_tmpdir)

    def tearDown(self):
        os.chdir(self.install.A_TEST_DIR)

    def test_site_amp(self):
        a_ref_dir = os.path.join(self.install.A_TEST_REF_DIR, "ucsb")
        a_res_dir = os.path.join(self.install.A_TMP_DATA_DIR, str(self.sim_id))

        site_obj = UCSite(self.r_velocity, self.r_src,
                          self.r_stations, sim_id=self.sim_id)
        site_obj.run()

        # Now compare results
        a_ref_file = os.path.join(a_ref_dir, "s01.site.3comp")
        a_newfile = os.path.join(a_res_dir, "s01.3comp")
        # Headers will be different;  need to ignore
        a_ref_file_no_header = os.path.join(a_res_dir,
                                            "ref_file_01_no_header")
        ref_file_in_fp = open(a_ref_file, 'r')
        ref_file_out_fp = open(a_ref_file_no_header, 'w')
        ref_file_data = ref_file_in_fp.readlines()
        ref_file_in_fp.close()
        for line in ref_file_data:
            line = line.strip()
            # Skip comments
            if line.startswith('%') or line.startswith('#'):
                continue
            ref_file_out_fp.write(line)
        ref_file_out_fp.flush()
        ref_file_out_fp.close()

        test_file_no_header = os.path.join(a_res_dir,
                                           "test_file_01_no_header")
        test_file_in_fp = open(a_newfile, 'r')
        test_file_out_fp = open(test_file_no_header, 'w')
        test_file_data = test_file_in_fp.readlines()
        test_file_in_fp.close()
        for line in test_file_data:
            line = line.strip()
            # Skip comments
            if line.startswith('%') or line.startswith('#'):
                continue
            test_file_out_fp.write(line)
        test_file_out_fp.flush()
        test_file_out_fp.close()

        errmsg = ("Output file %s does not match reference file %s" %
                  (a_newfile, a_ref_file))
        self.failIf(cmp_bbp.cmp_bbp(a_ref_file_no_header,
                                    test_file_no_header,
                                    tolerance=0.035) != 0, errmsg)
        cmd = "rm %s %s" % (a_ref_file_no_header, test_file_no_header)
        bband_utils.runprog(cmd)

if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestUCSite)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
