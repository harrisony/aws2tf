# New session - 2026-03-31T08:40:51.614Z

**Session ID:** ses_2bcf27f61ffek5W5mJvYW4vHv7
**Created:** 3/31/2026, 7:40:51 PM
**Updated:** 3/31/2026, 7:46:18 PM

---

## User

Look at @code/common.py  its not great is it

---

## Assistant (Plan · glm-4.7 · 27.7s)

_Thinking:_

The user is asking me to look at `code/common.py` and saying "its not great is it". This is in plan mode, so I should read and analyze the file to identify issues, then present findings and a plan for improvement.

Let me first read the entire file to understand its structure and problems.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/harrisony/Labs/aws2tf/code/common.py",
  "offset": 1464
}
```

**Output:**
```
<path>/Users/harrisony/Labs/aws2tf/code/common.py</path>
<type>file</type>
<content>1464:                             log.debug("Could not parse terraform plan output: %s", e)
1465: 
1466:                     if (
1467:                         ctype == "aws_lb_listener"
1468:                         or ctype == "aws_cognito_user_pool_client"
1469:                         or ctype == "aws_bedrockagent_agent"
1470:                         or ctype == "aws_bedrockagent_agent_action_group"
1471:                         or force_destroy_only
1472:                     ):
1473:                         changeList.append(pe["change"]["resource"]["addr"])
1474:                         log.info(
1475:                             "Planned changes found in Terraform Plan for type: "
1476:                             + str(pe["change"]["resource"]["resource_type"])
1477:                             + " "
1478:                             + str(pe["change"]["resource"]["addr"])
1479:                         )
1480:                         allowedchange = True
1481:                         nallowedchanges = nallowedchanges + 1
1482:                     else:
1483:                         all_force_destroy_only = False
1484:                         log.warning(
1485:                             "Unexpected plan changes found in Terraform Plan for resource: "
1486:                             + str(pe["change"]["resource"]["addr"])
1487:                         )
1488:             if nchanges == nallowedchanges:
1489:                 log.info(
1490:                     "\n-->> plan will change "
1491:                     + str(nchanges)
1492:                     + " resources! - these are expected changes only (should be non-consequential)"
1493:                 )
1494:                 ci = 1
1495: 
1496:                 log.info(
1497:                     "-->> Check the planned changes in these resources listed below by running: terraform plan\n"
1498:                 )
1499: 
1500:                 for i in changeList:
1501:                     log.info(str(ci) + ": " + str(i))
1502:                     ci = ci + 1
1503:                 log.info("\n")
1504: 
1505:                 # Auto-accept if all changes are force_destroy only
1506:                 if all_force_destroy_only and nchanges > 0:
1507:                     log.info(
1508:                         "All changes are force_destroy only - automatically continuing"
1509:                     )
1510:                     context.expected = True
1511: 
1512:                 if context.expected is False:
1513:                     log.info(
1514:                         "You can check the changes by running 'terraform plan' in %s\n",
1515:                         context.path1,
1516:                     )
1517:                     log.info(
1518:                         "Then rerun the same ./aws2tf.py command and add the '-a' flag to accept these plan changes and continue to import"
1519:                     )
1520:                     log.info("exit 023")
1521:                     stop_timer()
1522:                     exit()
1523: 
1524:                 if context.debug is True:
1525:                     log.debug(
1526:                         "\n-->> Then if happy with the output changes for the above resources, run this command to complete aws2tf-py tasks:"
1527:                     )
1528:                     log.info("exit 024")
1529:                     stop_timer()
1530:                     log.info("terraform apply -no-color tfplan")
1531:                     exit()
1532:             else:
1533:                 log.error("-->> plan will change resources! - unexpected")
1534:                 log.error("-->> look at plan2.json - or run terraform plan")
1535:                 log.info("exit 025 %s", str(context.aws2tfver))
1536:                 stop_timer()
1537:                 exit()
1538: 
1539:         if zeroa != 0:
1540:             log.error("-->> plan will add resources! - unexpected")
1541:             log.error("-->> look at plan2.json - or run terraform plan")
1542:             log.info("exit 026")
1543:             stop_timer()
1544:             exit()
1545: 
1546:         log.debug("Plan complete")
1547:         ## if merging get .out files from imported ?
1548: 
1549:     ### validations checks
1550:     # import__ == aws_*.tf - and import number
1551:     #
1552:     if not context.merge:
1553:         if zeroi == awsf:
1554:             log.info("PASSED: import count = file counts = %s", str(zeroi))
1555:         else:
1556:             log.info(
1557:                 "INFO: import count " + str(zeroi) + " != file counts " + str(awsf)
1558:             )
1559:             if context.workaround == "":
1560:                 log.error(
1561:                     "\nLikely import error [2] - do the following and report errors in github issue"
1562:                 )
1563:                 log.info("cd " + context.path1)
1564:                 log.info("terraform plan -generate-config-out=resources.out")
1565:                 log.info("exit 027")
1566:                 stop_timer()
1567:                 exit()
1568:             else:
1569:                 log.info("INFO: Continuing due to workaround " + context.workaround)
1570: 
1571:     if context.merge:
1572:         log.info("Merge check")
1573:         if zeroi == 0:
1574:             log.info("Nothing to merge exiting ...")
1575:             log.info("exit 028")
1576:             stop_timer()
1577:             exit()
1578:         # get imported
1579:         x = glob.glob("imported/import__*.tf")
1580:         # log.debug("Imported files ="+str(x))
1581:         preimpf = len(x)
1582:         log.info("previous imports %s", str(preimpf))
1583:         # impf-preimpf  (num import* files - number import files in imported)
1584:         # toimp=impf-preimpf
1585:         toimp = awsf - preimpf
1586:         com = "terraform state list | grep ^aws_ | wc -l"
1587:         rout = rc(com)
1588:         stc = int(rout.stdout.decode().rstrip())
1589: 
1590:         if preimpf != stc:
1591:             log.error(
1592:                 "Miss-matched previous imports %s and state file resources %s exiting",
1593:                 str(preimpf),
1594:                 str(stc),
1595:             )
1596:             log.info("exit 029")
1597:             stop_timer()
1598:             exit()
1599:         else:
1600:             log.info("Existing import file = Existing state count = %s", str(stc))
1601:         if toimp != zeroi:
1602:             log.warning("Unexpected import number exiting")
1603:             # log.info("exit 030")
1604:             # stop_timer()
1605:             # exit()
1606:         else:
1607:             log.info("PASSED: importing expected number of resources = %s", str(toimp))
1608: 
1609:     if not os.path.isfile("tfplan"):
1610:         log.error("Plan - could not find expected tfplan file - exiting")
1611:         log.info("exit 031")
1612:         stop_timer()
1613:         sys.exit(1)
1614: 
1615:     # if context.merge:
1616:     #   exit()
1617:     #   log.info("merge - exit after plan2")
1618: 
1619: 
1620: def wrapup():
1621:     ### copy predefined import files
1622:     log.info("Stage 8 of 10, Final Terraform Validation")
1623:     context.tracking_message = "Stage 8 of 10, Final Terraform Validation"
1624:     com = "terraform validate -no-color"
1625:     rout = rc(com)
1626:     el = len(rout.stderr.decode().rstrip())
1627:     if el != 0:
1628:         errm = rout.stderr.decode().rstrip()
1629:         log.error(errm)
1630:     if "Success! The configuration is valid" not in str(rout.stdout.decode().rstrip()):
1631:         log.error(str(rout.stdout.decode().rstrip()))
1632:         log.info("exit 032")
1633:         stop_timer()
1634:         exit()
1635:     else:
1636:         log.info("PASSED: Valid Configuration.")
1637: 
1638:     if context.merge:
1639:         log.info("Pre apply merge check")
1640:         if not os.path.isfile("plan2.json"):
1641:             log.error(
1642:                 "ERROR: Could not find plan2.json, unexpected on merge - exiting ...."
1643:             )
1644:             log.info("exit 033")
1645:             stop_timer()
1646:             exit()
1647: 
1648:     log.info("Stage 9 of 10, Terraform import via apply of tfplan....")
1649:     context.tracking_message = "Stage 9 of 10, Terraform import via apply of tfplan...."
1650: 
1651:     # Use progress bar for terraform apply
1652:     rout = run_terraform_apply_with_progress("tfplan")
1653: 
1654:     zerod = False
1655:     zeroc = False
1656:     if "Error" in str(rout.stderr.decode().rstrip()):
1657:         log.error("ERROR: problem in apply ... further checks ....")
1658:         errs = str(rout.stderr.decode().rstrip())
1659:         ## Plan check
1660:         log.info("\nPost Error Import Plan Check .....")
1661:         com = "terraform plan -no-color -out tfplan"
1662:         rout = run_terraform_command_with_spinner(com, "Post-error validation")
1663: 
1664:         if "No changes. Your infrastructure matches the configuration" not in str(
1665:             rout.stdout.decode().rstrip()
1666:         ):
1667:             log.error(errs)
1668:             log.error("ERROR: unexpected final plan stuff - exiting")
1669: 
1670:             if "aws_bedrockagent_agent" not in errs:
1671:                 log.info("exit 034")
1672:                 stop_timer()
1673:                 exit()
1674:             else:
1675:                 log.warning("WARNING: aws_bedrockagent_agent - continuing")
1676:         else:
1677:             log.info("PASSED: No changes in plan")
1678:             patterns = ["import__aws_*.tf", "*.out", "*.json"]
1679:             files_to_move = [f for pattern in patterns for f in glob.glob(pattern)]
1680:             if files_to_move:
1681:                 for tf in tqdm(
1682:                     files_to_move,
1683:                     desc="Moving files to imported/",
1684:                     unit="file",
1685:                     leave=False,
1686:                 ):
1687:                     try:
1688:                         shutil.move(tf, f"imported/{tf}")
1689:                     except (FileNotFoundError, shutil.Error):
1690:                         pass
1691:             x = glob.glob("aws_*.tf")
1692:             if len(x) > 0:
1693:                 for tf in tqdm(x, desc=f"Moving files", unit="file", leave=False):
1694:                     try:
1695:                         shutil.copy(tf, f"imported/{tf}")
1696:                     except (FileNotFoundError, shutil.Error):
1697:                         pass  # File already moved or doesn't exist
1698: 
1699:             # Security Fix #7: Secure sensitive files after import
1700:             secure_terraform_files(".")
1701:             return
1702: 
1703:     log.info("\nStage 10 of 10, Post Import Plan Check .....")
1704:     context.tracking_message = "Stage 10 of 10, Post Import Plan Check ....."
1705:     com = "terraform plan -no-color -out tfplan -json > final.json"
1706:     # Get reference file size for progress estimation
1707:     plan2_size = os.path.getsize("plan2.json") if os.path.exists("plan2.json") else 0
1708: 
1709:     com = "terraform plan -no-color -out tfplan -json > final.json"
1710: 
1711:     # Run with progress bar based on file size
1712:     if plan2_size > 0 and not context.debug:
1713:         process = subprocess.Popen(
1714:             com, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
1715:         )
1716:         with tqdm(
1717:             total=100,
1718:             desc="Post-import validation",
1719:             unit="%",
1720:             bar_format="{desc}: {percentage:3.0f}%|{bar}| [{elapsed}]",
1721:         ) as pbar:
1722:             start_time = time.time()
1723:             max_wait = plan2_size / 50000
1724:             while process.poll() is None:
1725:                 elapsed = time.time() - start_time
1726:                 if os.path.exists("final.json"):
1727:                     current_size = os.path.getsize("final.json")
1728:                     size_progress = min(75, int((current_size / plan2_size) * 75))
1729:                     pbar.n = size_progress
1730:                 else:
1731:                     time_progress = min(50, int((elapsed / max_wait) * 50))
1732:                     pbar.n = time_progress
1733:                 pbar.refresh()
1734:                 time.sleep(0.5)
1735:             pbar.n = 100
1736:             pbar.refresh()
1737:         stdout, stderr = process.communicate()
1738: 
1739:         class Result:
1740:             def __init__(self, returncode, stdout, stderr):
1741:                 self.returncode = returncode
1742:                 self.stdout = stdout
1743:                 self.stderr = stderr
1744: 
1745:         rout = Result(process.returncode, stdout, stderr)
1746:     else:
1747:         rout = rc(com)
1748:     com = "sync"
1749:     rout = rc(com)
1750:     zeroi = 0
1751:     zeroa = 0
1752:     zeroc = 0
1753:     zerod = 0
1754:     planList = []
1755:     planDict = {}
1756:     changeList = []
1757:     with open("final.json", "r") as f:
1758:         for jsonObj in f:
1759:             planDict = json.loads(jsonObj)
1760:             planList.append(planDict)
1761:     with open("final.warn", "w") as f:
1762:         for pe in planList:
1763:             if pe["type"] == "change_summary":
1764:                 zeroi = int(pe["changes"]["import"])
1765:                 zeroa = int(pe["changes"]["add"])
1766:                 zeroc = int(pe["changes"]["change"])
1767:                 zerod = int(pe["changes"]["remove"])
1768:                 json.dump(pe, f, indent=2, default=str)
1769:             elif pe["type"] == "diagnostic":
1770:                 json.dump(pe, f, indent=2, default=str)
1771: 
1772:     log.info(
1773:         "Plan: %s to import, %s to add, %s to change, %s to destroy",
1774:         zeroi,
1775:         zeroa,
1776:         zeroc,
1777:         zerod,
1778:     )
1779:     nchged = zeroi + zeroa + zeroc + zerod
1780:     if nchged == 0:
1781:         context.tracking_message = (
1782:             "Stage 10 of 10, Passed post import check - No changes in plan"
1783:         )
1784:         log.info("Stage 10 of 10, Passed post import check - No changes in plan")
1785: 
1786:         # Move multiple file types in one operation
1787:         patterns = ["import__aws_*.tf", "*.out", "*.json"]
1788:         files_to_move = [f for pattern in patterns for f in glob.glob(pattern)]
1789:         if files_to_move:
1790:             for tf in tqdm(
1791:                 files_to_move,
1792:                 desc="Moving files to imported/",
1793:                 unit="file",
1794:                 leave=False,
1795:             ):
1796:                 try:
1797:                     shutil.move(tf, f"imported/{tf}")
1798:                 except (FileNotFoundError, shutil.Error):
1799:                     pass
1800: 
1801:         x = glob.glob("aws_*.tf")
1802:         if len(x) > 0:
1803:             for tf in tqdm(x, desc=f"Moving files", unit="file", leave=False):
1804:                 try:
1805:                     shutil.copy(tf, f"imported/{tf}")
1806:                 except (FileNotFoundError, shutil.Error):
1807:                     pass  # File already moved or doesn't exist
1808: 
1809:         # Security Fix #7: Secure sensitive files after import
1810:         secure_terraform_files(".")
1811: 
1812:     else:
1813:         log.error("ERROR: unexpected final plan failure")
1814:         out1 = str(rout.stdout.decode().rstrip())
1815:         log.error(out1)
1816:         # if "aws_bedrockagent_agent" in out1:
1817:         #   log.warning("WARNING: aws_bedrockagent_agent - continuing")"
1818:         log.error(str(rout.stderr.decode().rstrip()))
1819:         log.info("exit 035")
1820:         stop_timer()
1821:         exit()
1822: 
1823: 
1824: ######################################################################
1825: 
1826: 
1827: def rc(cmd):
1828:     """
1829:     Execute a command safely without shell=True.
1830: 
1831:     Args:
1832:         cmd: Either a string (for backwards compatibility, will be parsed)
1833:              or a list of command arguments
1834: 
1835:     Returns:
1836:         subprocess.CompletedProcess object
1837:     """
1838:     # If cmd is a string, parse it into a list for safe execution
1839:     if isinstance(cmd, str):
1840:         # For simple commands, split on spaces
1841:         # For complex commands with pipes/redirects, we need special handling
1842:         if ">" in cmd or "|" in cmd or "&&" in cmd or ";" in cmd:
1843:             # These require shell, but we'll use shell=True only for these cases
1844:             # and log a warning
1845:             if context.debug:
1846:                 log.debug(f"WARNING: Command requires shell features: {cmd[:100]}")
1847:             out = subprocess.run(cmd, shell=True, capture_output=True)
1848:         else:
1849:             # Safe to split and run without shell
1850:             import shlex
1851: 
1852:             try:
1853:                 cmd_list = shlex.split(cmd)
1854:                 out = subprocess.run(cmd_list, capture_output=True, shell=False)
1855:             except Exception as e:
1856:                 # Fallback to shell if parsing fails
1857:                 log.warning(f"Command parsing failed, using shell: {e}")
1858:                 out = subprocess.run(cmd, shell=True, capture_output=True)
1859:     else:
1860:         # cmd is already a list
1861:         out = subprocess.run(cmd, capture_output=True, shell=False)
1862: 
1863:     ol = len(out.stdout.decode("utf-8").rstrip())
1864:     el = len(out.stderr.decode().rstrip())
1865:     if el != 0:
1866:         errm = out.stderr.decode().rstrip()
1867:         # log.error(errm)
1868:         # exit(1)
1869: 
1870:     return out
1871: 
1872: 
1873: def fix_imports():
1874:     x = glob.glob("aws_*__*.tf")
1875:     context.esttime = len(x) / 4
1876:     awsf = len(x)
1877:     y = glob.glob("import__*.tf")
1878:     impf = len(y)
1879:     log.info("\nFix Import Intervention")
1880: 
1881:     # more import files than aws files - picked up via dependancies
1882:     # if impf > awsf:
1883:     for fil2 in y:  # all import files
1884:         impok = False
1885:         for fil in x:  # all aws_ files
1886:             tf = fil.split(".tf", 1)[0]
1887:             iseg = fil2.replace("import__", "").replace(".tf", "")
1888:             if tf == iseg:
1889:                 # com = "mv "+fil2+" imported/"+fil2
1890:                 # rc(com)
1891:                 impok = True
1892:                 break
1893: 
1894:         ## out of for loop
1895:         # got an import file we
1896:         if impok is False:
1897:             com = "mv " + fil2 + " " + fil2.replace(".tf", ".err")
1898:             log.warning(fil2.replace(".tf", ".err"))
1899:             rc(com)
1900: 
1901:     y = glob.glob("import__*.tf")
1902:     impf = len(y)
1903: 
1904: 
1905: def ctrl_c_handler(signum, frame):
1906:     log.info("Ctrl-C pressed.")
1907:     log.info("exit 036")
1908:     stop_timer()
1909:     exit()
1910: 
1911: 
1912: def check_python_version():
1913:     version = sys.version_info
1914:     major = version.major
1915:     minor = version.minor
1916:     bv = str(boto3.__version__)
1917:     log.info("boto3 version: %s", bv)
1918:     if major < 3 or (major == 3 and minor < 8):
1919:         log.error("This program requires Python 3.8 or later.")
1920:         sys.exit(1)
1921:     # check boto3 version
1922:     if boto3.__version__ < "1.42.16":
1923:         bv = str(boto3.__version__)
1924:         log.info("boto3 version: %s", bv)
1925:         vs = bv.split(".")
1926:         v1 = int(vs[0]) * 100000 + int(vs[1]) * 1000 + int(vs[2])
1927:         if v1 < 142016:
1928:             log.error("boto3 version: %s", bv)
1929:             log.error("This program requires boto3 1.42.16 or later.")
1930:             log.error("Try: pip install boto3  -or-  pip install boto3==1.42.16")
1931:             log.info("exit 037")
1932:             stop_timer()
1933:             sys.exit(1)
1934: 
1935: 
1936: def aws_tf(region, args):
1937:     # os.chdir(context.path1)
1938:     # if not os.path.isfile("aws.tf"):
1939: 
1940:     with open("provider.tf", "w") as f3:
1941:         f3.write("terraform {\n")
1942:         f3.write('  required_version = "> 1.10.4"\n')
1943:         f3.write("  required_providers {\n")
1944:         f3.write("    aws = {\n")
1945:         f3.write('      source  = "hashicorp/aws"\n')
1946:         # f3.write('      version = "5.48.0"\n')
1947:         f3.write('      version = "' + context.tfver + '"\n')
1948:         f3.write("    }\n")
1949:         f3.write("  }\n")
1950:         f3.write("}\n")
1951:         f3.write('provider "aws" {\n')
1952:         f3.write('  region                   = "' + region + '"\n')
1953:         if args.profile is not None:
1954:             f3.write('  profile                  = "' + context.profile + '"\n')
1955:         if not context.serverless:
1956:             f3.write('  shared_credentials_files = ["~/.aws/credentials"]\n')
1957:         f3.write("}\n")
1958: 
1959:     com = "cp provider.tf imported/provider.tf"
1960:     rout = rc(com)
1961:     if not os.path.isfile("data-aws.tf"):
1962:         with open("data-aws.tf", "w") as f3:
1963:             f3.write('data "aws_region" "current" {}\n')
1964:             f3.write('data "aws_caller_identity" "current" {}\n')
1965:             f3.write('data "aws_availability_zones" "az" {\n')
1966:             f3.write('state = "available"\n')
1967:             f3.write("}\n")
1968:     if not context.merge:
1969:         # log.info("terraform init")
1970:         com = "terraform init -no-color -upgrade"
1971:         rout = rc(com)
1972:         el = len(rout.stderr.decode().rstrip())
1973:         if el != 0:
1974:             log.error(rout.stdout.decode().rstrip())
1975:             log.error(str(rout.stderr.decode().rstrip()))
1976:     else:
1977:         log.info("skipping terraform init")
1978: 
1979: 
1980: # split resources.out
1981: def splitf_old(file):
1982:     lhs = 0
1983:     rhs = 0
1984:     if os.path.isfile(file):
1985:         if context.debug:
1986:             log.debug("split file:" + file)
1987:         with open(file, "r") as f:
1988:             Lines = f.readlines()
1989:         for tt1 in Lines:
1990:             if "{" in tt1:
1991:                 lhs = lhs + 1
1992:             if "}" in tt1:
1993:                 rhs = rhs + 1
1994:             if lhs > 1:
1995:                 if lhs == rhs:
1996:                     try:
1997:                         f2.write(tt1 + "\n")
1998:                         f2.close()
1999:                         lhs = 0
2000:                         rhs = 0
2001:                         continue
2002:                     except:
2003:                         pass
2004: 
2005:             if tt1.startswith("resource"):
2006:                 ttft = tt1.split('"')[1]
2007:                 taddr = tt1.split('"')[3]
2008:                 # if context.acc in taddr:
2009:                 #   a1=taddr.find(context.acc)
2010:                 #   taddr=taddr[:a1]+taddr[a1+12:]
2011: 
2012:                 f2 = open(ttft + "__" + taddr + ".out", "w")
2013:                 f2.write(tt1)
2014: 
2015:             elif tt1.startswith("#"):
2016:                 continue
2017:             elif tt1 == "" or tt1 == "\n":
2018:                 continue
2019:             else:
2020:                 try:
2021:                     f2.write(tt1)
2022:                 except:
2023:                     log.warning("tried to write to closed file: >" + tt1 + "<")
2024:     else:
2025:         log.error("could not find expected resources.out file")
2026: 
2027:     # moves resources.out to imported
2028:     f2.close()
2029:     shutil.move(file, "imported/" + file)
2030: 
2031: 
2032: #################################
2033: 
2034: 
2035: def splitf(input_file):
2036:     # Compile regex patterns for better performance
2037:     resource_pattern = re.compile(r'resource "(\w+)" "(.+?)"')
2038:     comment_pattern = re.compile(r"^\s*#")
2039:     if context.debug:
2040:         log.debug("split file: " + input_file)
2041:     # Read the entire file content at once
2042:     with open(input_file, "r") as f:
2043:         content = f.read()
2044: 
2045:     # Use a more efficient splitting method
2046:     resource_blocks = re.split(r'(?=\nresource ")', "\n" + content)
2047: 
2048:     for block in resource_blocks[1:]:  # Skip the first (empty) block
2049:         match = resource_pattern.search(block)
2050:         if match:
2051:             resource_type = match.group(1)
2052:             resource_name = match.group(2)
2053: 
2054:             # Create filename
2055:             resource_name_safe = resource_name.replace("/", "__")
2056:             # Security Fix #3: Sanitize filename
2057:             resource_name_safe = re.sub(r"[^\w\-\.]", "_", resource_name_safe)
2058:             filename = f"{resource_type}__{resource_name_safe}.out"
2059: 
2060:             # Use StringIO for efficient string operations
2061:             output = StringIO()
2062: 
2063:             for line in block.split("\n"):
2064:                 if not comment_pattern.match(line):
2065:                     output.write(line + "\n")
2066: 
2067:             # Write the filtered resource block to a new file
2068: 
2069:             if len(filename) > 255:
2070:                 filename = filename[:250] + ".out"
2071:             try:
2072:                 # Security Fix #3: Use safe file write
2073:                 safe_write_file(filename, output.getvalue().strip() + "\n")
2074:             except ValueError as e:
2075:                 log.error(f"ERROR: Path validation failed: {e}")
2076:                 log.info("exit 038")
2077:                 stop_timer()
2078:                 exit()
2079:             except Exception as e:
2080:                 log.error(f"ERROR: could not write to file: {filename} - {e}")
2081:                 log.info("exit 038")
2082:                 stop_timer()
2083:                 exit()
2084:     shutil.move(input_file, "imported/" + input_file)
2085: 
2086: 
2087: ################################
2088: 
2089: 
2090: # if type == "aws_vpc_endpoint": return "ec2","describe_vpc_endpoints","VpcEndpoints","VpcEndpointId","vpc-id"
2091: 
2092: 
2093: # generally pass 3rd param as None - unless overriding
2094: def write_import(type, theid, tfid):
2095:     try:
2096:         ## todo -  if theid starts with a number or is an od (but what if its hexdecimal  ?)
2097: 
2098:         if tfid is None:
2099:             tfid = (
2100:                 theid.replace("/", "_")
2101:                 .replace(".", "_")
2102:                 .replace(":", "_")
2103:                 .replace("|", "_")
2104:                 .replace("$", "_")
2105:                 .replace(",", "_")
2106:                 .replace("&", "_")
2107:                 .replace("#", "_")
2108:                 .replace("[", "_")
2109:                 .replace("]", "_")
2110:                 .replace("=", "_")
2111:                 .replace("!", "_")
2112:                 .replace(";", "_")
2113:                 .replace(" ", "_")
2114:                 .replace("*", "star")
2115:                 .replace("\\052", "star")
2116:                 .replace("@", "_")
2117:                 .replace("\\64", "_")
2118:             )
2119:         else:
2120:             tfid = (
2121:                 tfid.replace("/", "_")
2122:                 .replace(".", "_")
2123:                 .replace(":", "_")
2124:                 .replace("|", "_")
2125:                 .replace("$", "_")
2126:                 .replace(",", "_")
2127:                 .replace("&", "_")
2128:                 .replace("#", "_")
2129:                 .replace("[", "_")
2130:                 .replace("]", "_")
2131:                 .replace("=", "_")
2132:                 .replace("!", "_")
2133:                 .replace(";", "_")
2134:                 .replace(" ", "_")
2135:                 .replace("*", "star")
2136:                 .replace("\\052", "star")
2137:                 .replace("@", "_")
2138:                 .replace("\\64", "_")
2139:             )
2140: 
2141:         # catch tfid starts with number
2142:         if tfid[:1].isdigit():
2143:             tfid = "r-" + tfid
2144: 
2145:         # Security Fix #3: Additional sanitization to prevent path traversal
2146:         tfid = re.sub(r"\.\.", "_", tfid)  # Remove any remaining ..
2147:         tfid = tfid.replace("/", "_")  # Ensure no path separators
2148: 
2149:         if "!" in theid:
2150:             fn = "notimported/import__" + type + "__" + tfid + ".tf"
2151:             log.error("ERROR: Not importing " + type + " " + theid)
2152:             log.error("ERROR: Invalid character ! in name")
2153:         else:
2154:             fn = "import__" + type + "__" + tfid + ".tf"
2155: 
2156:         # fn=fn.replace(context.acc,"012345678912")
2157: 
2158:         if context.debug:
2159:             log.debug(fn)
2160: 
2161:             # check if file exists:
2162:             #
2163:         if context.merge:
2164:             # y = glob.glob("imported/import__*.tf")
2165:             if os.path.isfile("imported/" + fn):
2166:                 return
2167: 
2168:         if os.path.isfile(fn):
2169:             if context.debug:
2170:                 log.debug("File exists: " + fn)
2171:             pkey = type + "." + tfid
2172:             context.rproc[pkey] = True
2173:             return
2174: 
2175:         done_data = False
2176:         done_data = do_data(type, theid)
2177: 
2178:         if not done_data:
2179:             output = StringIO()
2180:             output.write("import {\n")
2181:             output.write("  to = " + type + "." + tfid + "\n")
2182:             output.write('  id = "' + theid + '"\n')
2183:             output.write("}\n")
2184: 
2185:             # Write the filtered resource block to a new file
2186: 
2187:             if len(fn) > 255:
2188:                 fn = fn[:250] + ".tf"
2189:             # if context.merge:   print("Merge import",fn)
2190:             try:
2191:                 # Security Fix #3: Use safe file write with path validation
2192:                 safe_write_file(fn, output.getvalue().strip() + "\n")
2193:             except ValueError as e:
2194:                 log.error(f"ERROR: Path validation failed: {e}")
2195:                 log.info("exit 039")
2196:                 stop_timer()
2197:                 exit()
2198:             except Exception as e:
2199:                 log.error(f"ERROR: could not write to file: {fn} - {e}")
2200:                 log.info("exit 039")
2201:                 stop_timer()
2202:                 exit()
2203: 
2204:         pkey = type + "." + tfid
2205:         context.rproc[pkey] = True
2206:         pkey = type + "." + theid
2207:         context.rproc[pkey] = True
2208: 
2209:     except Exception as e:
2210:         handle_error2(e, str(inspect.currentframe().f_code.co_name), id)
2211: 
2212:     return
2213: 
2214: 
2215: def do_data(type, theid):
2216:     if context.dnet:
2217:         if type == "aws_vpc" or type == "aws_subnet":
2218:             fn = "data-" + type + "_" + theid + ".tf"
2219:             with open(fn, "w") as f3:
2220:                 f3.write('data "' + type + '" "' + theid + '" {\n')
2221:                 f3.write(' id = "' + theid + '"\n')
2222:                 f3.write("}\n")
2223:             return True
2224: 
2225:     if context.dsgs:
2226:         if type == "aws_security_groups":
2227:             fn = "data-" + type + "_" + theid + ".tf"
2228:             with open(fn, "w") as f3:
2229:                 f3.write('data "' + type + '" "' + theid + '" {\n')
2230:                 f3.write(' id = "' + theid + '"\n')
2231:                 f3.write("}\n")
2232:             return True
2233:     if context.dkms:
2234:         if type == "aws_kms_key":
2235:             fn = "data-" + type + "_" + theid + ".tf"
2236:             with open(fn, "w") as f3:
2237:                 f3.write('data "' + type + '" "k-' + theid + '" {\n')
2238:                 f3.write(' key_id = "' + theid + '"\n')
2239:                 f3.write("}\n")
2240:             return True
2241:     if context.dkey:
2242:         if type == "aws_key_pair":
2243:             tfil = (
2244:                 theid.replace("/", "_")
2245:                 .replace(".", "_")
2246:                 .replace(":", "_")
2247:                 .replace("|", "_")
2248:                 .replace("$", "_")
2249:                 .replace(",", "_")
2250:                 .replace("&", "_")
2251:                 .replace("#", "_")
2252:                 .replace("[", "_")
2253:                 .replace("]", "_")
2254:                 .replace("=", "_")
2255:                 .replace("!", "_")
2256:                 .replace(";", "_")
2257:             )
2258:             fn = "data-" + type + "_" + tfil + ".tf"
2259:             with open(fn, "w") as f3:
2260:                 f3.write('data "' + type + '" "' + tfil + '" {\n')
2261:                 f3.write(' key_name = "' + theid + '"\n')
2262:                 f3.write("}\n")
2263:             return True
2264: 
2265:     return False
2266: 
2267: 
2268: #########################################################################################################################
2269: 
2270: 
2271: def getresource(type, id, clfn, descfn, topkey, key, filterid):
2272:     # for j in context.specials:
2273:     #   if type == j:
2274:     #      print(type + " in specials list returning ..")
2275:     #      return False
2276:     if context.debug:
2277:         log.debug(
2278:             "-1-> In getresource doing "
2279:             + type
2280:             + " with id "
2281:             + str(id)
2282:             + " clfn="
2283:             + clfn
2284:             + " descfn="
2285:             + descfn
2286:             + " topkey="
2287:             + topkey
2288:             + " key="
2289:             + key
2290:             + " filterid="
2291:             + filterid
2292:         )
2293: 
2294:     if type in str(context.types):
2295:         log.info("Found " + type + "in types skipping ...")
2296:         return True
2297:     try:
2298:         if id is not None:
2299:             pt = type + "." + id
2300:             if pt in context.rproc:
2301:                 if context.rproc[pt] is True:
2302:                     log.info("Found " + pt + " in processed skipping ...")
2303:                     return True
2304:         response = call_boto3(type, clfn, descfn, topkey, key, id)
2305:         if str(response) != "[]":
2306:             for item in response:
2307:                 if id is None or filterid == "":  # do it all
2308:                     if context.debug:
2309:                         log.debug("--" + str(item))
2310:                     try:
2311:                         if "aws-service-role" in str(item["Path"]):
2312:                             if context.debug:
2313:                                 log.debug("Skipping service role " + str(item[key]))
2314:                             continue
2315:                     except:
2316:                         pass
2317: 
2318:                     try:
2319:                         theid = item[key]
2320:                     except TypeError:
2321:                         log.error(
2322:                             "ERROR: getresource TypeError: "
2323:                             + str(response)
2324:                             + " key="
2325:                             + key
2326:                             + " type="
2327:                             + type,
2328:                             descfn,
2329:                         )
2330:                         with open("boto3-error.err", "a") as f:
2331:                             f.write(
2332:                                 "ERROR: getresource TypeError: type="
2333:                                 + type
2334:                                 + " key="
2335:                                 + key
2336:                                 + " descfn="
2337:                                 + descfn
2338:                                 + "\n"
2339:                                 + str(response)
2340:                                 + "\n"
2341:                             )
2342:                         continue
2343:                     pt = type + "." + theid
2344:                     if pt not in context.rproc:
2345:                         write_import(type, theid, None)
2346:                     else:
2347:                         if context.rproc[pt] is True:
2348:                             log.info("Found " + pt + " in processed skipping ...")
2349:                             continue
2350:                     # special_deps(type,theid)
2351: 
2352:                 #
2353:                 # id has something
2354:                 #
2355:                 else:
2356:                     if context.debug:
2357:                         log.debug(
2358:                             "-gr31-"
2359:                             + "filterid="
2360:                             + str(filterid)
2361:                             + " id="
2362:                             + str(id)
2363:                             + "  key="
2364:                             + key
2365:                         )
2366:                         log.debug(str(item))
2367:                     if "." not in filterid:
2368:                         try:
2369:                             if id == str(item[filterid]):
2370:                                 # if context.debug: print("-gr31 item-"+str(item))
2371:                                 theid = item[key]
2372:                                 # special_deps(type,theid)
2373:                                 write_import(type, theid, None)
2374:                             elif filterid != key:
2375:                                 if context.debug:
2376:                                     log.debug("id=" + id + " filterid=" + filterid)
2377:                                     log.debug("item=" + str(item))
2378:                                 theid = item[filterid]
2379:                                 write_import(type, theid, None)
2380:                         except Exception as e:
2381:                             log.error(f"{e=}")
2382:                             if context.mopup.get(type) is not None:
2383:                                 if id.startswith(context.mopup[type]):
2384:                                     write_import(type, id, None)
2385:                                     return True
2386: 
2387:                             else:
2388:                                 with open("missed-getresource.log", "a") as f4:
2389:                                     f4.write(
2390:                                         "Could have done write_import "
2391:                                         + type
2392:                                         + " id="
2393:                                         + id
2394:                                         + " filterid="
2395:                                         + filterid
2396:                                         + "/n"
2397:                                     )
2398:                                 return False
2399:                     else:
2400:                         ### There IS a dot in the filterid so we need to dig deeper
2401:                         log.debug(str(item))
2402:                         log.debug("id=" + id + " filterid=" + filterid)
2403:                         filt1 = filterid.split(".")[1]
2404:                         filt2 = filterid.split(".")[3]
2405:                         log.debug("filt1=" + filt1 + " filt2=" + filt2)
2406:                         dotc = len(item[filt1])
2407:                         log.debug("dotc=" + str(dotc))
2408: 
2409:                         for j in range(0, dotc):
2410:                             try:
2411:                                 val = str(item[filt1][j][filt2])
2412:                                 log.debug("val=" + val + " id=" + id)
2413:                                 if id == val:
2414:                                     theid = item[key]
2415:                                     if dotc > 1:
2416:                                         theid = id + "/" + item[key]
2417:                                     write_import(type, theid, None)
2418:                             except:
2419:                                 log.error("-------- error on processing")
2420:                                 log.error(str(item))
2421:                                 log.error("filterid=" + filterid)
2422:                                 log.error("----------------------------")
2423:                                 pass
2424:         else:
2425:             if id is not None:
2426:                 if context.debug:
2427:                     log.debug(
2428:                         "No " + type + " " + id + " found - empty response (common)"
2429:                     )
2430:                 pkey = type + "." + id
2431:                 context.rproc[pkey] = True
2432:             else:
2433:                 if context.debug:
2434:                     log.debug("No " + type + " found - empty response (common)")
2435:                 return True
2436: 
2437:     except Exception as e:
2438:         handle_error(
2439:             e, str(inspect.currentframe().f_code.co_name), clfn, descfn, topkey, id
2440:         )
2441: 
2442:     return True
2443: 
2444:     # tfplan(type)
2445: 
2446: 
2447: def special_deps(ttft, taddr):
2448:     """
2449:     if ttft == "aws_security_group":
2450:        print("##### special dep security group")
2451:        #add_known_dependancy("aws_security_group_rule",taddr)
2452:        #add_dependancy("aws_security_group_rule",taddr)
2453:     if ttft == "aws_subnet":
2454:        print("##### special dep subnet")
2455:        #add_known_dependancy("aws_route_table_association",taddr)
2456:        #add_dependancy("aws_route_table_association",taddr)
2457:     elif ttft == "aws_vpc":
2458:        print("##### special dep vpc")
2459:        #add_known_dependancy("aws_route_table_association",taddr)
2460:        #add_known_dependancy("aws_subnet",taddr)
2461:        #add_dependancy("aws_route_table_association",taddr)
2462:        #add_dependancy("aws_vpc_ipv4_cidr_block_association",taddr)
2463:        #add_dependancy("aws_vpc_endpoint", taddr)
2464: 
2465:     if ttft == "aws_vpclattice_service_network":
2466:        print("##### special lattice sn")
2467:        add_known_dependancy("aws_vpclattice_service",taddr)
2468:        add_known_dependancy("aws_vpclattice_service_network_vpc_association",taddr)
2469:        add_known_dependancy("aws_vpclattice_service_network_service_association",taddr)
2470:     """
2471:     return
2472: 
2473: 
2474: def get_test(type, id, clfn, descfn, topkey, key, filterid):
2475:     log.debug("in get_test")
2476:     log.debug("--> In get_test doing " + type + " with id " + str(id))
2477:     return
2478: 
2479: 
2480: def add_known_dependancy(type, id):
2481:     # check if we alredy have it
2482:     pkey = type + "." + id
2483:     if pkey not in context.rdep:
2484:         if context.debug:
2485:             log.debug("add_known_dependancy: " + pkey)
2486:         context.rdep[pkey] = False
2487:     return
2488: 
2489: 
2490: def add_dependancy(type, id):
2491:     # check if we alredy have it
2492:     if id is None:
2493:         log.warning("WARNING: add_dependancy: id is None")
2494:         return
2495:     try:
2496:         #   if type=="aws_kms_alias" and id=="k-817bb810-7154-4d9b-b582-7dbb62e77876":
2497:         #      raise Exception("aws_kms_alias")
2498:         if type == "aws_glue_catalog_database":
2499:             if ":" not in id:
2500:                 id = context.acc + ":" + id
2501:         pkey = type + "." + id
2502:         if pkey not in context.rproc:
2503:             if context.debug:
2504:                 log.debug("add_dependancy: " + pkey)
2505:             context.rproc[pkey] = False
2506:     except Exception as e:
2507:         handle_error(e, str(inspect.currentframe().f_code.co_name), type, id)
2508:     return
2509: 
2510: 
2511: ## TODO - always get all / paginate all - save in globals - filter on id in get_aws_ ??
2512: ## but in smaller use cases may be better to make filtered boto3 calls ?
2513: ## this call doesn't take the key
2514: 
2515: ## can't pass filterid - not possible to use for page in paginator.paginate(filterid=id)
2516: # TODO ? won't accept filter id as string param1 in paginate(param1,id) ??
2517: # hench working around using descfn - not ideal
2518: 
2519: 
2520: def call_boto3(type, clfn, descfn, topkey, key, id):
2521:     try:
2522:         if context.debug:
2523:             log.debug(
2524:                 "call_boto3 clfn="
2525:                 + clfn
2526:                 + " descfn="
2527:                 + descfn
2528:                 + " topkey="
2529:                 + topkey
2530:                 + " id="
2531:                 + str(id)
2532:             )
2533:         # if context.debug: print("pre-response")
2534:         # get any pre-saved response
2535:         # response=get_boto3_resp(descfn)  # sets response to [] if nothing saved
2536:         response = []
2537:         if response == []:
2538:             client = boto3.client(clfn)
2539:             # if context.debug: print("client")
2540:             try:
2541:                 paginator = client.get_paginator(descfn)
2542:                 # if context.debug: print("paginator")
2543: 
2544:                 if "apigatewayv2" in str(type):
2545:                     for page in paginator.paginate(ApiId=id):
2546:                         response.extend(page[topkey])
2547:                     pkey = type + "." + id
2548:                     context.rproc[pkey] = True
2549:                     # if response != []:
2550:                     #   print(str(response))
2551: 
2552:                 elif descfn == "describe_launch_templates":
2553:                     if id is not None:
2554:                         if id.startswith("lt-"):
2555:                             for page in paginator.paginate(LaunchTemplateIds=[id]):
2556:                                 response.extend(page[topkey])
2557:                         else:
2558:                             for page in paginator.paginate(LaunchTemplateNames=[id]):
2559:                                 response.extend(page[topkey])
2560:                     else:
2561:                         for page in paginator.paginate():
2562:                             response.extend(page[topkey])
2563: 
2564:                 elif descfn == "describe_instances":
2565:                     if id is not None:
2566:                         if "i-" in id:
2567:                             for page in paginator.paginate(InstanceIds=[id]):
2568:                                 response.extend(page[topkey][0]["Instances"])
2569:                     else:
2570:                         for page in paginator.paginate():
2571:                             if len(page[topkey]) == 0:
2572:                                 continue
2573:                             response.extend(page[topkey][0]["Instances"])
2574:                         # sav_boto3_rep(descfn,response)
2575: 
2576:                 elif (
2577:                     descfn == "describe_pod_identity_association"
2578:                     or descfn == "list_fargate_profiles"
2579:                     or descfn == "list_nodegroups"
2580:                     or descfn == "list_identity_provider_configs"
2581:                     or descfn == "list_addons"
2582:                 ):
2583:                     for page in paginator.paginate(clusterName=id):
2584:                         response.extend(page[topkey])
2585: 
2586:                 elif descfn == "list_access_keys" and id is not None:
2587:                     for page in paginator.paginate(UserName=id):
2588:                         response.extend(page[topkey])
2589: 
2590:                 elif clfn == "kms" and descfn == "list_aliases" and id is not None:
2591:                     if id.startswith("k-"):
2592:                         id = id[2:]
2593:                     for page in paginator.paginate(KeyId=id):
2594:                         response.extend(page[topkey])
2595:                     return response
2596: 
2597:                 elif clfn == "lambda" and descfn == "list_aliases" and id is not None:
2598:                     for page in paginator.paginate(FunctionName=id):
2599:                         response.extend(page[topkey])
2600:                     return response
2601: 
2602:                 elif clfn == "describe_config_rules" and id is not None:
2603:                     for page in paginator.paginate(ConfigRuleNames=id):
2604:                         response.extend(page[topkey])
2605:                     return response
2606: 
2607:                 elif clfn == "describe_log_groups" and id is not None:
2608:                     if "arn:" in id:
2609:                         ## arn filtering done in get_aws_cloudwatch_log_group()
2610:                         for page in paginator.paginate():
2611:                             response.extend(page[topkey])
2612:                         return response
2613:                     else:
2614:                         for page in paginator.paginate(logGroupNamePattern=id):
2615:                             response.extend(page[topkey])
2616:                         return response
2617: 
2618:                 else:
2619:                     if context.debug:
2620:                         log.debug("--1b")
2621:                     # main get all call - usually a list- describe- or get-
2622:                     for page in paginator.paginate():
2623:                         response.extend(page[topkey])
2624:                     # sav_boto3_rep(descfn,response)
2625: 
2626:                     if id is not None:
2627:                         fresp = response
2628:                         if context.debug:
2629:                             log.debug("--2")
2630:                         response = []
2631:                         if context.debug:
2632:                             log.debug(str(fresp))
2633:                         # get by id - useually a describe- or get-
2634:                         for i in fresp:
2635:                             if context.debug:
2636:                                 try:
2637:                                     log.debug("%s %s %s", i[key], id)
2638:                                 except TypeError:
2639:                                     log.debug("%s %s %s", i, id)
2640:                             try:
2641:                                 if id in i[key]:
2642:                                     response = [i]
2643:                                     break
2644:                             except TypeError:
2645:                                 if id in i:
2646:                                     response = [i]
2647:                                     break
2648:                         # get by filter - useually a list- describe- or get-
2649:                     # save a full paginate as we don't want to do it many times
2650: 
2651:             except botocore.exceptions.ParamValidationError as e:
2652:                 log.error(
2653:                     "ParamValidationError 1 in common.call_boto3: type="
2654:                     + type
2655:                     + " clfn="
2656:                     + clfn
2657:                 )
2658:                 exc_type, exc_obj, exc_tb = sys.exc_info()
2659:                 fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
2660:                 log.error(f"{e=} [pv1] %s %s", fname, exc_tb.tb_lineno)
2661:                 with open("boto3-error.err", "a") as f:
2662:                     f.write(
2663:                         "type="
2664:                         + type
2665:                         + " clfn="
2666:                         + clfn
2667:                         + " descfn="
2668:                         + descfn
2669:                         + " topkey="
2670:                         + topkey
2671:                         + " id="
2672:                         + str(id)
2673:                         + "\n"
2674:                     )
2675:                     f.write(f"{e=} [pv1] \n")
2676:                     f.write(f"{fname=} {exc_tb.tb_lineno=} [e2] \n")
2677:                     f.write(
2678:                         "-----------------------------------------------------------------------------\n"
2679:                     )
2680:                 return []
2681: 
2682:             except botocore.exceptions.OperationNotPageableError as err:
2683:                 if context.debug:
2684:                     log.debug(f"{err=}")
2685:                     log.debug(
2686:                         "calling non paginated fn " + str(descfn) + " id=" + str(id)
2687:                     )
2688:                 try:
2689:                     getfn = getattr(client, descfn)
2690:                     response1 = getfn()
2691:                     response1 = response1[topkey]
2692:                     if context.debug:
2693:                         log.debug("Non-pag response1=" + str(response1))
2694:                     if id is None:
2695:                         if context.debug:
2696:                             log.debug("id None")
2697:                         response = response1
2698:                         if context.debug:
2699:                             log.debug("Non-pag response no ID =" + str(response))
2700:                     else:  # try a match
2701:                         for j in response1:
2702:                             if id == j[key]:
2703:                                 response = [j]
2704:                                 if context.debug:
2705:                                     log.debug(
2706:                                         "Non-pag response with ID =" + str(response)
2707:                                     )
2708: 
2709:                 except botocore.exceptions.ParamValidationError as e:
2710:                     log.error(
2711:                         "ParamValidationError 2 in common.call_boto3: type="
2712:                         + type
2713:                         + " clfn="
2714:                         + clfn
2715:                     )
2716:                     exc_type, exc_obj, exc_tb = sys.exc_info()
2717:                     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
2718:                     log.error(f"{e=} [pv2] %s %s", fname, exc_tb.tb_lineno)
2719: 
2720:                     with open("boto3-error.err", "a") as f:
2721:                         f.write(
2722:                             "type="
2723:                             + type
2724:                             + " clfn="
2725:                             + clfn
2726:                             + " descfn="
2727:                             + descfn
2728:                             + " topkey="
2729:                             + topkey
2730:                             + " id="
2731:                             + str(id)
2732:                             + "\n"
2733:                         )
2734:                         f.write(f"{e=} [pv2] \n")
2735:                         f.write(f"{fname=} {exc_tb.tb_lineno=} [e2] \n")
2736:                         f.write(
2737:                             "-----------------------------------------------------------------------------\n"
2738:                         )
2739:                     return []
2740: 
2741:             except Exception as e:
2742:                 handle_error(
2743:                     e,
2744:                     str(inspect.currentframe().f_code.co_name),
2745:                     clfn,
2746:                     descfn,
2747:                     topkey,
2748:                     id,
2749:                 )
2750: 
2751:             rl = len(response)
2752:             if rl == 0:
2753:                 if context.debug:
2754:                     log.debug(
2755:                         "** zero response length for "
2756:                         + descfn
2757:                         + " in call_boto3 returning .. []"
2758:                     )
2759:                 return []
2760: 
2761:             if context.debug:
2762:                 log.debug("response length=" + str(len(response)))
2763: 
2764:                 for item in response:
2765:                     log.debug(item)
2766:                 log.debug("--------------------------------------")
2767: 
2768:         else:
2769:             return response
2770: 
2771:     except Exception as e:
2772:         handle_error(
2773:             e, str(inspect.currentframe().f_code.co_name), clfn, descfn, topkey, id
2774:         )
2775: 
2776:     return response
2777: 
2778: 
2779: """
2780: def sav_boto3_rep(descfn,response):
2781:    if str(descfn)=="describe_subnets" and context.aws_subnet_resp==[]: context.aws_subnet_resp=response  
2782:    elif str(descfn)=="describe_vpcs" and context.aws_vpc_resp==[]: context.aws_vpc_resp=response  
2783:    elif str(descfn)=="describe_route_tables" and context.aws_route_table_resp==[]: context.aws_route_table_resp=response  
2784:    elif str(descfn)=="list_aliases" and context.aws_kms_alias_resp==[]: context.aws_kms_alias_resp=response  
2785:    elif str(descfn)=="list_roles" and context.aws_iam_role_resp==[]: context.aws_iam_role_resp=response  
2786:    elif str(descfn)=="describe_instances" and context.aws_instance_resp==[]: context.aws_instance_resp=response  
2787:    return 
2788: 
2789: def get_boto3_resp(descfn):
2790:    response=[]
2791:    if str(descfn)=="describe_subnets" and context.aws_subnet_resp != []: response=context.aws_subnet_resp
2792:    elif str(descfn)=="describe_vpcs" and context.aws_vpc_resp != []: response=context.aws_vpc_resp
2793:    elif str(descfn)=="describe_route_tables" and context.aws_route_table_resp != []: response=context.aws_route_table_resp 
2794:    elif str(descfn)=="list_aliases" and context.aws_kms_alias_resp != []: response=context.aws_kms_alias_resp 
2795:    elif str(descfn)=="list_roles" and context.aws_iam_role_resp != []: response=context.aws_iam_role_resp
2796:    elif str(descfn)=="describe_instances" and context.aws_instance_resp != []: response=context.aws_instance_resp
2797:    return response
2798: """
2799: 
2800: 
2801: def handle_error(e, frame, clfn, descfn, topkey, id):
2802: 
2803:     exc_type, exc_obj, exc_tb = sys.exc_info()
2804:     exn = str(exc_type.__name__)
2805:     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
2806:     if exn == "EndpointConnectionError":

(Output capped at 50 KB. Showing lines 1464-2806. Use offset=2807 to continue.)
</content>
```

---

## Assistant (Plan · glm-4.7 · 21.2s)

_Thinking:_

The file is quite large. Let me read the rest of it to understand the full picture.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/harrisony/Labs/aws2tf/code/common.py",
  "offset": 2807
}
```

**Output:**
```
<path>/Users/harrisony/Labs/aws2tf/code/common.py</path>
<type>file</type>
<content>2807:         log.debug("No endpoint in this region for " + descfn + " - returning")
2808:         return
2809:     elif exn == "ClientError":
2810:         if "does not exist" in str(e):
2811:             log.warning(id + " does not exist " + fname + " " + str(exc_tb.tb_lineno))
2812:             return
2813:         log.debug("Exception message :" + str(e))
2814:         return
2815:     elif exn == "ForbiddenException":
2816:         log.debug("Call Forbidden exception for " + fname + " - returning")
2817:         return
2818:     elif (
2819:         exn == "ParamValidationError"
2820:         or exn == "ValidationException"
2821:         or exn == "InvalidRequestException"
2822:         or exn == "InvalidParameterValueException"
2823:         or exn == "InvalidParameterException"
2824:     ):
2825:         log.warning(str(exc_obj) + " for " + frame + " id=" + str(id) + " - returning")
2826:         return
2827:     elif exn == "BadRequestException" and clfn == "guardduty":
2828:         log.warning(str(exc_obj) + " for " + frame + " id=" + str(id) + " - returning")
2829:         return
2830: 
2831:     elif exn == "AccessDeniedException":
2832:         pkey = frame.split("get_")[1]
2833:         log.warning("AccessDeniedException exception for " + fname + " - returning")
2834:         return
2835: 
2836:     elif "NotFoundException" in exn:
2837:         if frame.startswith("get_"):
2838:             log.debug(
2839:                 "NOT FOUND: "
2840:                 + frame.split("get_")[1]
2841:                 + " "
2842:                 + str(id)
2843:                 + " check if it exists and what references it - returning"
2844:             )
2845:             pkey = frame.split("get_")[1] + "." + str(id)
2846:             if "aws_glue_catalog_database" in pkey:
2847:                 pkey = frame.split("get_")[1] + "." + context.acc + ":" + id
2848:             context.rproc[pkey] = True
2849:         else:
2850:             log.debug(
2851:                 "NOT FOUND: " + frame + " " + id + " check if it exists - returning"
2852:             )
2853:         return
2854: 
2855:     elif (
2856:         exn == "ResourceNotFoundException"
2857:         or exn == "EntityNotFoundException"
2858:         or exn == "NoSuchEntityException"
2859:         or exn == "NotFoundException"
2860:         or exn == "LoadBalancerNotFoundException"
2861:         or exn == "NamespaceNotFound"
2862:         or exn == "NoSuchHostedZone"
2863:     ):
2864:         if frame.startswith("get_"):
2865:             log.debug(
2866:                 "NOT FOUND: "
2867:                 + frame.split("get_")[1]
2868:                 + " "
2869:                 + str(id)
2870:                 + " check if it exists and what references it - returning"
2871:             )
2872:             pkey = frame.split("get_")[1] + "." + str(id)
2873:             context.rproc[pkey] = True
2874:         else:
2875:             log.debug(
2876:                 "RESOURCE NOT FOUND: "
2877:                 + frame
2878:                 + " "
2879:                 + str(id)
2880:                 + " check if it exists - returning"
2881:             )
2882:         return
2883: 
2884:     elif exn == "KeyError":
2885:         if "kms" in str(exc_obj):
2886:             log.warning(
2887:                 "KeyError can not find key for "
2888:                 + fname
2889:                 + " id="
2890:                 + str(id)
2891:                 + " - returning"
2892:             )
2893:             return
2894: 
2895:         if clfn == "sqs":
2896:             log.warning(
2897:                 "KeyError can not find queue url for "
2898:                 + fname
2899:                 + " id="
2900:                 + str(id)
2901:                 + " - returning"
2902:             )
2903:             return
2904: 
2905:     elif exn == "InvalidDocument":
2906:         if clfn == "ssm":
2907:             log.warning(
2908:                 "KeyError can not find ssm document for "
2909:                 + fname
2910:                 + " id="
2911:                 + str(id)
2912:                 + " - returning"
2913:             )
2914:             return
2915: 
2916:     elif (
2917:         exn == "AWSOrganizationsNotInUseException"
2918:         or exn == "OrganizationAccessDeniedException"
2919:     ):
2920:         log.warning(
2921:             "NO ORG: "
2922:             + frame
2923:             + " this account doesn't appear to be in an AWS Organisation (or you don't have org permissions) - returning"
2924:         )
2925:         return
2926: 
2927:     elif "NoSuch" in exn and clfn == "cloudfront":
2928:         log.warning(str(exc_obj) + " for " + frame + " id=" + str(id) + " - returning")
2929:         return
2930: 
2931:     elif "BadRequest" in exn:
2932:         if "The requested feature is not enabled for this AWS account" in str(exc_obj):
2933:             log.warning(
2934:                 descfn + " returned feature not enabled for this account - returning"
2935:             )
2936:             return
2937:         elif "Your account isn't authorized to call this operation" in str(exc_obj):
2938:             log.warning(
2939:                 descfn
2940:                 + " returned Your account isn't authorized to call this operation - returning"
2941:             )
2942:             return
2943:         log.error(exn)
2944:         log.error(str(exc_obj) + " for " + frame + " id=" + str(id) + " - exit")
2945:         log.info("exit 040")
2946:         # stop_timer() # as it is multi-threaded
2947:         exit()
2948: 
2949:     elif "InvalidAccessException" in exn:
2950:         if "is not subscribed" in str(exc_obj):
2951:             log.warning(descfn + " returned Not subscribed " + clfn + " - returning")
2952:             return
2953:         log.info("exit 041")
2954:         stop_timer()
2955:         exit()
2956: 
2957:     log.error(
2958:         "\nERROR: in "
2959:         + frame
2960:         + " clfn="
2961:         + clfn
2962:         + " descfn="
2963:         + descfn
2964:         + " topkey="
2965:         + topkey
2966:         + " id="
2967:         + str(id)
2968:     )
2969:     try:
2970:         log.error(f"{e=} [e1]")
2971:         log.error(f"{exn=} [e1]")
2972:         log.error("%s %s", fname, exc_tb.tb_lineno)
2973:     except:
2974:         log.error("except err")
2975:         pass
2976:     with open("boto3-error.err", "a") as f:
2977:         f.write(
2978:             "clfn="
2979:             + clfn
2980:             + " descfn="
2981:             + descfn
2982:             + " topkey="
2983:             + topkey
2984:             + " id="
2985:             + str(id)
2986:             + "\n"
2987:         )
2988:         f.write(f"{e=} [e1] \n")
2989:         f.write(f"{fname=} {exc_tb.tb_lineno=} [e1] \n")
2990:         f.write(
2991:             "-----------------------------------------------------------------------------\n"
2992:         )
2993:     log.error("stopping process ...")
2994:     # threading.
2995:     stop_timer()
2996:     sys.exit(1)
2997: 
2998: 
2999: def handle_error2(e, frame, id):
3000:     log.error("\nERROR: in " + frame)
3001:     log.error("id=" + str(id))
3002:     exc_type, exc_obj, exc_tb = sys.exc_info()
3003:     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
3004:     exn = str(exc_type.__name__)
3005:     if exn == "EndpointConnectionError":
3006:         log.debug("No endpoint in this region - returning")
3007:         return
3008:     log.error(f"{e=} [e2] %s %s", fname, exc_tb.tb_lineno)
3009:     with open("boto3-error.err", "a") as f:
3010:         f.write("id=" + str(id) + "\n")
3011:         f.write(f"{e=} [e2] ")
3012:         f.write(f"{fname=} {exc_tb.tb_lineno=} [e2] \n")
3013:         f.write(
3014:             "-----------------------------------------------------------------------------\n"
3015:         )
3016:     log.info("exit 042")
3017:     stop_timer()
3018:     sys.exit(1)
3019: 
3020: 
3021: def create_bucket_if_not_exists(bucket_name):
3022:     s3_client = boto3.client("s3")
3023: 
3024:     try:
3025:         s3_client.head_bucket(Bucket=bucket_name)
3026:         log.info(f"Bucket {bucket_name} already exists.")
3027:     except ClientError as e:
3028:         error_code = int(e.response["Error"]["Code"])
3029:         if error_code == 404:
3030:             log.info(f"Bucket {bucket_name} does not exist. Creating now...")
3031:             try:
3032:                 s3_client.create_bucket(
3033:                     Bucket=bucket_name,
3034:                     CreateBucketConfiguration={"LocationConstraint": context.region},
3035:                 )
3036:                 log.info(f"Bucket {bucket_name} created successfully.")
3037:             except ClientError as create_error:
3038:                 log.error(f"Error creating bucket {bucket_name}: {create_error}")
3039:                 return False
3040:         else:
3041:             log.error(f"Error checking bucket {bucket_name}: {e}")
3042:             return False
3043: 
3044:     return True
3045: 
3046: 
3047: def upload_directory_to_s3():
3048:     log.info("Uploading to S3...")
3049:     s3_client = boto3.client("s3")
3050:     local_directory = (
3051:         "/tmp/aws2tf/generated/tf-"
3052:         + context.pathadd
3053:         + context.acc
3054:         + "-"
3055:         + context.region
3056:     )
3057:     bucket_name = "aws2tf-" + context.acc + "-" + context.region
3058:     s3_prefix = ""
3059:     log.info("Calling create_bucket_if_not_exists for %s", bucket_name)
3060:     bret = create_bucket_if_not_exists(bucket_name)
3061:     if bret:
3062:         log.info("Upload files to s3 %s", bucket_name)
3063:         for root, dirs, files in os.walk(local_directory):
3064:             if ".terraform" in dirs:
3065:                 dirs.remove(".terraform")
3066:             if "tfplan" in files:
3067:                 files.remove("tfplan")
3068:             if ".terraform.lock.hcl" in files:
3069:                 files.remove(".terraform.lock.hcl")
3070:             for filename in files:
3071:                 local_path = os.path.join(root, filename)
3072: 
3073:                 # Calculate relative path
3074:                 relative_path = os.path.relpath(local_path, local_directory)
3075:                 s3_path = os.path.join(s3_prefix, relative_path).replace("\\", "/")
3076: 
3077:                 try:
3078:                     s3_client.upload_file(local_path, bucket_name, s3_path)
3079:                 except ClientError as e:
3080:                     log.error(f"Error uploading {local_path}: {e}")
3081:                     return False
3082:         log.info("Upload to S3 complete.")
3083:     else:
3084:         log.error(
3085:             "Upload to S3 failed - False return from create_bucket_if_not_exists for %s",
3086:             bucket_name,
3087:         )
3088:         return False
3089: 
3090: 
3091: def empty_and_delete_bucket():
3092:     bucket_name = "aws2tf-" + context.acc + "-" + context.region
3093:     s3 = boto3.resource("s3")
3094:     s3_client = boto3.client("s3")
3095:     bucket = s3.Bucket(bucket_name)
3096:     log.info("Emptying and deleting bucket... %s", bucket_name)
3097:     # Check if the bucket exists
3098:     try:
3099:         s3_client.head_bucket(Bucket=bucket_name)
3100:     except ClientError as e:
3101:         error_code = int(e.response["Error"]["Code"])
3102:         if error_code == 404:
3103:             log.info(f"Bucket {bucket_name} does not exist. Nothing to delete.")
3104:             return
3105:         else:
3106:             log.error(f"Error checking bucket {bucket_name}: {e}")
3107:             return
3108: 
3109:     # Empty the bucket
3110:     try:
3111:         bucket.objects.all().delete()
3112:         log.info(f"Bucket {bucket_name} emptied successfully.")
3113:     except ClientError as e:
3114:         log.error(f"Error emptying bucket {bucket_name}: {e}")
3115:         return
3116: 
3117:     # Delete the bucket
3118:     try:
3119:         bucket.delete()
3120:         log.info(f"Bucket {bucket_name} deleted successfully.")
3121:     except ClientError as e:
3122:         log.error(f"Error deleting bucket {bucket_name}: {e}")
3123:         return
3124: 
3125:     log.info(f"Bucket {bucket_name} has been emptied and deleted.")
3126: 
3127: 
3128: def download_from_s3():
3129:     log.info("Restore S3")
3130:     s3_client = boto3.client("s3")
3131:     local_directory = (
3132:         "/tmp/aws2tf/generated/tf-"
3133:         + context.pathadd
3134:         + context.acc
3135:         + "-"
3136:         + context.region
3137:     )
3138:     bucket_name = "aws2tf-" + context.acc + "-" + context.region
3139:     s3_prefix = ""
3140:     # Check if the bucket exists
3141:     try:
3142:         s3_client.head_bucket(Bucket=bucket_name)
3143:     except ClientError as e:
3144:         error_code = int(e.response["Error"]["Code"])
3145:         if error_code == 404:
3146:             log.error(f"Bucket {bucket_name} does not exist. Cannot download.")
3147:             return
3148:         else:
3149:             log.error(f"Error checking bucket {bucket_name}: {e}")
3150:             return
3151: 
3152:     # Create the local directory if it doesn't exist
3153:     os.makedirs(local_directory, exist_ok=True)
3154: 
3155:     # List objects in the bucket with the specified prefix
3156:     paginator = s3_client.get_paginator("list_objects_v2")
3157:     for page in paginator.paginate(Bucket=bucket_name, Prefix=s3_prefix):
3158:         if "Contents" not in page:
3159:             continue
3160: 
3161:         for obj in page["Contents"]:
3162:             # Skip the .terraform directory
3163:             if ".terraform" in obj["Key"]:
3164:                 continue
3165: 
3166:             # Get the relative path of the file
3167:             relative_path = os.path.relpath(obj["Key"], s3_prefix)
3168:             local_file_path = os.path.join(local_directory, relative_path)
3169: 
3170:             # Create the directory structure if it doesn't exist
3171:             os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
3172: 
3173:             # Download the file
3174:             try:
3175:                 s3_client.download_file(bucket_name, obj["Key"], local_file_path)
3176:             except ClientError as e:
3177:                 log.error(f"Error downloading {obj['Key']}: {e}")
3178: 
3179:     log.info(f"Download from {bucket_name}/{s3_prefix} to {local_directory} completed.")
3180: 
3181: 
3182: def trivy_check():
3183:     # Get current directory and extract the last two parts
3184:     mydir = os.getcwd()
3185:     mydir = "/".join(mydir.split("/")[-2:])
3186: 
3187:     # Check if jq is installed
3188:     if shutil.which("jq") is None:
3189:         log.warning("jq is not installed. skipping security report")
3190:         return
3191: 
3192:     # Check if trivy is installed
3193:     if shutil.which("trivy") is None:
3194:         log.warning("trivy is not installed. skipping security report")
3195:         return
3196: 
3197:     # Get trivy version
3198:     try:
3199:         trivy_version = subprocess.check_output(
3200:             ["trivy", "version"], universal_newlines=True
3201:         )
3202:         ver = int(
3203:             "".join(
3204:                 filter(str.isdigit, trivy_version.split("\n")[0].split(":")[1].strip())
3205:             )
3206:         )
3207:     except subprocess.CalledProcessError:
3208:         log.error("Error getting trivy version")
3209:         return
3210: 
3211:     if ver < 480:
3212:         log.warning("Please upgrade trivy to version v0.48.0 or higher")
3213:         return
3214: 
3215:     log.info("Generating trivy security report ....")
3216: 
3217:     with open("security-report.txt", "w") as report:
3218:         report.write("trivy security report\n")
3219: 
3220:         for severity in ["CRITICAL", "HIGH"]:
3221:             report.write(f"{severity}:\n")
3222:             try:
3223:                 output = subprocess.check_output(
3224:                     [
3225:                         "trivy",
3226:                         "fs",
3227:                         "--scanners",
3228:                         "misconfig",
3229:                         ".",
3230:                         "-s",
3231:                         severity,
3232:                         "--format",
3233:                         "json",
3234:                         "-q",
3235:                     ],
3236:                     universal_newlines=True,
3237:                 )
3238:                 results = json.loads(output)
3239:                 for result in results.get("Results", []):
3240:                     misconfigurations = result.get("Misconfigurations", [])
3241:                     if misconfigurations:
3242:                         for misconfig in misconfigurations:
3243:                             resource = misconfig.get("CauseMetadata", {}).get(
3244:                                 "Resource", ""
3245:                             )
3246:                             description = misconfig.get("Description", "")
3247:                             references = misconfig.get("References", [])
3248:                             report.write(
3249:                                 json.dumps([resource, description, references]) + "\n"
3250:                             )
3251:             except subprocess.CalledProcessError:
3252:                 log.error(f"Error running trivy for {severity} severity")
3253: 
3254:     log.info(f"Trivy security report: {mydir}/security-report.txt")
3255: 
3256: 
3257: def detect_aws_credentials(profile_name=None):
3258:     """
3259:     Detect the type of AWS credentials currently in use and check for SSO login.
3260: 
3261:     Args:
3262:         profile_name (str, optional): AWS profile to check. If None, uses default or AWS_PROFILE env var.
3263: 
3264:     Returns a dictionary with credential information.
3265:     """
3266:     result = {
3267:         "credential_type": None,
3268:         "is_sso": False,
3269:         "profile_name": None,
3270:         "details": {},
3271:         "status": "unknown",
3272:     }
3273: 
3274:     try:
3275:         # Get session for specific profile or default
3276:         if profile_name:
3277:             session = boto3.Session(profile_name=profile_name)
3278:         else:
3279:             session = boto3.Session()
3280: 
3281:         credentials = session.get_credentials()
3282: 
3283:         if not credentials:
3284:             result["status"] = "no_credentials"
3285:             return result
3286: 
3287:         result["status"] = "found"
3288: 
3289:         # Check current profile
3290:         actual_profile = (
3291:             session.profile_name
3292:             or profile_name
3293:             or os.environ.get("AWS_PROFILE", "default")
3294:         )
3295:         result["profile_name"] = actual_profile
3296: 
3297:         # Method 1: Check for ACTIVE SSO token cache that matches current session
3298:         sso_cache_dir = Path.home() / ".aws" / "sso" / "cache"
3299:         active_sso_tokens = []
3300:         current_session_uses_sso = False
3301: 
3302:         if sso_cache_dir.exists():
3303:             cache_files = list(sso_cache_dir.glob("*.json"))
3304:             if cache_files:
3305:                 # First, we'll collect all valid tokens but not assume they're for current session
3306:                 for cache_file in cache_files:
3307:                     try:
3308:                         with open(cache_file, "r") as f:
3309:                             token_data = json.load(f)
3310:                             expires_at_str = token_data.get("expiresAt", "")
3311:                             if expires_at_str:
3312:                                 expires_at = datetime.fromisoformat(
3313:                                     expires_at_str.replace("Z", "+00:00")
3314:                                 )
3315:                                 if expires_at > datetime.now(timezone.utc):
3316:                                     active_sso_tokens.append(
3317:                                         {
3318:                                             "file": cache_file.name,
3319:                                             "expires_at": expires_at.isoformat(),
3320:                                             "region": token_data.get(
3321:                                                 "region", "unknown"
3322:                                             ),
3323:                                             "start_url": token_data.get(
3324:                                                 "startUrl", "unknown"
3325:                                             ),
3326:                                         }
3327:                                     )
3328:                     except (json.JSONDecodeError, ValueError, KeyError):
3329:                         continue
3330: 
3331:                 # Store token info for debugging but don't use for detection yet
3332:                 result["details"]["available_sso_tokens"] = active_sso_tokens
3333: 
3334:         # Method 2: Check AWS config file for SSO settings (but don't assume active SSO)
3335:         config_file = Path.home() / ".aws" / "config"
3336:         sso_configured = False
3337:         if config_file.exists():
3338:             try:
3339:                 config = configparser.ConfigParser()
3340:                 config.read(config_file)
3341: 
3342:                 # Check current profile and default profile for SSO settings
3343:                 profiles_to_check = []
3344:                 if actual_profile != "default":
3345:                     profiles_to_check.append(f"profile {actual_profile}")
3346:                 else:
3347:                     profiles_to_check.append("default")
3348: 
3349:                 for profile_section in profiles_to_check:
3350:                     if profile_section in config:
3351:                         section = config[profile_section]
3352:                         if (
3353:                             "sso_start_url" in section
3354:                             or "sso_session" in section
3355:                             or "sso_account_id" in section
3356:                             or "sso_role_name" in section
3357:                         ):
3358:                             sso_configured = True
3359: 
3360:                             result["details"]["sso_config"] = {
3361:                                 "profile": profile_section,
3362:                                 "sso_start_url": section.get("sso_start_url"),
3363:                                 "sso_region": section.get("sso_region"),
3364:                                 "sso_account_id": section.get("sso_account_id"),
3365:                                 "sso_role_name": section.get("sso_role_name"),
3366:                                 "sso_session": section.get("sso_session"),
3367:                             }
3368:                             break
3369: 
3370:             except Exception as e:
3371:                 result["details"]["config_read_error"] = str(e)
3372: 
3373:         # Method 3: Check environment variables
3374:         env_vars = {
3375:             "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID"),
3376:             "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY"),
3377:             "AWS_SESSION_TOKEN": os.environ.get("AWS_SESSION_TOKEN"),
3378:             "AWS_PROFILE": os.environ.get("AWS_PROFILE"),
3379:             "AWS_REGION": os.environ.get("AWS_REGION"),
3380:         }
3381: 
3382:         if env_vars["AWS_ACCESS_KEY_ID"] and env_vars["AWS_SECRET_ACCESS_KEY"]:
3383:             if env_vars["AWS_SESSION_TOKEN"]:
3384:                 if result["credential_type"] is None:
3385:                     result["credential_type"] = "temporary_credentials"
3386:             else:
3387:                 if result["credential_type"] is None:
3388:                     result["credential_type"] = "static_credentials"
3389: 
3390:         result["details"]["environment_variables"] = {
3391:             k: "SET" if v else "NOT_SET" for k, v in env_vars.items()
3392:         }
3393: 
3394:         # Method 4: Check credential source using STS with the specified session
3395:         # This is the DEFINITIVE method - the ARN tells us exactly what we're using
3396:         try:
3397:             sts = session.client("sts")
3398:             caller_identity = sts.get_caller_identity()
3399: 
3400:             result["details"]["caller_identity"] = {
3401:                 "user_id": caller_identity.get("UserId"),
3402:                 "account": caller_identity.get("Account"),
3403:                 "arn": caller_identity.get("Arn"),
3404:             }
3405: 
3406:             # The ARN is the definitive source of truth
3407:             arn = caller_identity.get("Arn", "")
3408:             if ":assumed-role/AWSReservedSSO_" in arn:
3409:                 # This IS definitely SSO - the ARN proves it
3410:                 result["is_sso"] = True
3411:                 result["credential_type"] = "sso_assumed_role"
3412:                 current_session_uses_sso = True
3413: 
3414:                 # Now find the matching SSO token for this session
3415:                 matching_tokens = []
3416:                 for token in active_sso_tokens:
3417:                     # You could add more sophisticated matching here if needed
3418:                     matching_tokens.append(token)
3419:                 result["details"]["sso_tokens"] = matching_tokens
3420: 
3421:             elif ":assumed-role/" in arn:
3422:                 # Regular assumed role (not SSO)
3423:                 result["credential_type"] = "assumed_role"
3424:                 result["is_sso"] = False
3425:             elif ":user/" in arn:
3426:                 # IAM user - definitely not SSO for this session
3427:                 result["credential_type"] = "iam_user"
3428:                 result["is_sso"] = False
3429:             else:
3430:                 # Unknown ARN pattern
3431:                 result["credential_type"] = "unknown_arn_pattern"
3432:                 result["is_sso"] = False
3433: 
3434:         except Exception as e:
3435:             result["details"]["sts_error"] = str(e)
3436: 
3437:         # Method 5: Check credentials source metadata
3438:         if hasattr(credentials, "method"):
3439:             result["details"]["credentials_method"] = credentials.method
3440: 
3441:         # If still unknown, make best guess based on what we found
3442:         if result["credential_type"] is None:
3443:             if result["is_sso"]:
3444:                 result["credential_type"] = "sso"
3445:             elif sso_configured:
3446:                 result["credential_type"] = "sso_configured_but_inactive"
3447:             else:
3448:                 result["credential_type"] = "unknown"
3449: 
3450:         # Add notes about SSO configuration vs actual usage
3451:         if sso_configured and not result["is_sso"]:
3452:             result["details"]["note"] = (
3453:                 "SSO is configured but current session is not using SSO"
3454:             )
3455:         elif active_sso_tokens and not result["is_sso"]:
3456:             result["details"]["note"] = (
3457:                 "Valid SSO tokens exist but current session is not using SSO"
3458:             )
3459: 
3460:     except Exception as e:
3461:         result["status"] = "error"
3462:         result["details"]["error"] = str(e)
3463: 
3464:     return result
3465: 
3466: 
3467: def print_credentials_info(profile_name=None):
3468:     """Print a formatted report of AWS credentials information."""
3469:     info = detect_aws_credentials(profile_name)
3470: 
3471:     log.info("AWS Credentials Analysis")
3472:     log.info("=" * 40)
3473:     log.info(f"Status: {info['status']}")
3474:     log.info(f"Profile: {info['profile_name']}")
3475:     log.info(f"Credential Type: {info['credential_type']}")
3476:     log.info(f"Using SSO: {'Yes' if info['is_sso'] else 'No'}")
3477: 
3478:     if info["details"]:
3479:         log.info("Details:")
3480:         log.info("-" * 20)
3481: 
3482:         # Print caller identity if available
3483:         if "caller_identity" in info["details"]:
3484:             ci = info["details"]["caller_identity"]
3485:             log.info(f"Account ID: {ci.get('account', 'N/A')}")
3486:             log.info(f"User ARN: {ci.get('arn', 'N/A')}")
3487:             log.info(f"User ID: {ci.get('user_id', 'N/A')}")
3488: 
3489:         # Print SSO token info if available and relevant
3490:         if "sso_tokens" in info["details"] and info["is_sso"]:
3491:             tokens = info["details"]["sso_tokens"]
3492:             log.info(f"Active SSO Tokens for this session: {len(tokens)}")
3493:             for token in tokens:
3494:                 log.info(f"  - Expires: {token['expires_at']}")
3495:                 log.info(f"    Region: {token['region']}")
3496:         elif "available_sso_tokens" in info["details"]:
3497:             tokens = info["details"]["available_sso_tokens"]
3498:             log.info(
3499:                 f"Available SSO Tokens (not used by current session): {len(tokens)}"
3500:             )
3501: 
3502:         # Print SSO configuration if available
3503:         if "sso_config" in info["details"]:
3504:             sso_config = info["details"]["sso_config"]
3505:             log.info("SSO Configuration:")
3506:             log.info(f"  Profile: {sso_config.get('profile', 'N/A')}")
3507:             log.info(f"  Start URL: {sso_config.get('sso_start_url', 'N/A')}")
3508:             log.info(f"  Account ID: {sso_config.get('sso_account_id', 'N/A')}")
3509:             log.info(f"  Role Name: {sso_config.get('sso_role_name', 'N/A')}")
3510: 
3511:         # Print environment variables
3512:         if "environment_variables" in info["details"]:
3513:             env_vars = info["details"]["environment_variables"]
3514:             log.info("Environment Variables:")
3515:             for var, status in env_vars.items():
3516:                 log.info(f"  {var}: {status}")
3517: 
3518:         # Print any important notes
3519:         if "note" in info["details"]:
3520:             log.info(f"Note: {info['details']['note']}")
3521: 
3522:         # Print any errors
3523:         if "error" in info["details"]:
3524:             log.error(f"Error: {info['details']['error']}")
3525:         if "sts_error" in info["details"]:
3526:             log.error(f"STS Error: {info['details']['sts_error']}")

(End of file - total 3526 lines)
</content>
```

---

## Assistant (Plan · glm-4.7 · 78.4s)

_Thinking:_

Now I have the full picture of `code/common.py`. This is a 3526-line file that serves as a catch-all utility module. The user is asking me to look at it and saying "its not great is it" - clearly inviting me to identify problems and suggest improvements.

Let me analyze the issues:

## Major Issues Identified:

1. **God file / God class antipattern** - 3526 lines of mixed concerns in a single file
2. **Massive import block** (lines 614-720) - over 100 imports for AWS services
3. **Hardcoded module registry** (lines 724-841) - 100+ lines of manual module mappings
4. **Multiple responsibilities**:
   - Command execution (`rc`)
   - Progress tracking (`run_terraform_plan_with_progress`)
   - File operations (`safe_write_file`, `splitf`)
   - Security (`safe_filename`)
   - Terraform plan validation (`tfplan1`, `tfplan2`, `tfplan3`)
   - Resource discovery (`call_resource`, `getresource`)
   - Boto3 wrapping (`call_boto3`)
   - S3 operations
   - AWS credential detection
   - Error handling (`handle_error`, `handle_error2`)
   - And more...

5. **Poor error handling** - bare `except:` blocks without exception types (lines 883, 873, 1109, 1130)
6. **Commented out dead code** (lines 179-215, 2780-2798)
7. **Inconsistent naming** (`clfn`, `descfn`, `topkey` - abbreviated variables)
8. **Duplicated logic** - similar patterns in resource handling repeated many times
9. **Global state dependency** - heavy reliance on `context` module
10. **Type hints missing** - no type annotations anywhere
11. **Magic strings/numbers** - exit codes like "exit 016", "exit 037", etc.
 
I notice significant code smell and architectural challenges that demand immediate refactoring. The module represents a classic example of software design anti-patterns, with tight coupling, poor modularity, and significant technical debt. The code's complexity makes it nearly impossible to maintain, test, or extend effectively.

A comprehensive restructure is critical to transform this monolithic utility module into a clean, well-organized set of focused, single-responsibility components. This will improve code readability, maintainability, and overall system architecture.

You're right - `code/common.py` has significant issues. Let me analyze the problems:

## Critical Issues

**1. God File Anti-pattern (3,526 lines)**
- Mixed responsibilities: Terraform execution, file I/O, boto3 calls, security, progress tracking, S3 operations, error handling, AWS credential detection, and more
- No clear boundaries between domains

**2. Massive Hardcoded Registries (lines 614-841)**
- 100+ import statements for AWS services
- 100+ lines of manual module mappings (`AWS_RESOURCE_MODULES`)
- Should be auto-discovered or configured

**3. Poor Error Handling**
```python
except:  # Lines 883, 873, 1109, 1130 - bare except blocks
    pass
```

**4. Dead Code**
- Commented-out functions (lines 179-215, 2780-2798)
- Unused `splitf_old()` function

**5. Inconsistent Naming**
- `clfn`, `descfn`, `topkey` - cryptic abbreviations
- `sr`, `rr` - meaningless booleans

**6. Duplicated Logic**
- Similar resource handling patterns repeated across `call_resource`, `getresource`, `call_boto3`
- Progress tracking code duplicated between `tfplan1`, `tfplan2`, `tfplan3`

**7. Heavy Global State Dependency**
- Everything depends on `context.*` global variables
- Makes testing and modular reuse impossible

**8. Magic Exit Codes**
- `"exit 016"`, `"exit 037"` scattered throughout - what do they mean?

**9. No Type Hints**
- Zero type annotations in 3,500+ lines

## Recommended Refactoring Strategy

**Tool: question**

**Input:**
```json
{
  "questions": [
    {
      "question": "How aggressively should we refactor common.py? This affects risk and timeline.",
      "header": "Refactor Scope",
      "options": [
        {
          "label": "Incremental (low risk)",
          "description": "Extract 1-2 modules at a time (e.g., terraform.py, security.py). Test after each extraction."
        },
        {
          "label": "Moderate (balanced)",
          "description": "Split into 6-8 focused modules (terraform.py, boto3.py, fileops.py, security.py, etc.) in one pass."
        },
        {
          "label": "Aggressive (high risk)",
          "description": "Complete restructure: new package structure with proper interfaces, dependency injection, testable components."
        }
      ],
      "multiple": false
    }
  ]
}
```

**Output:**
```
User has answered your questions: "How aggressively should we refactor common.py? This affects risk and timeline."="Aggressive (high risk)". You can now continue with the user's answers in mind.
```

---

## Assistant (Plan · glm-4.7 · 110.5s)

_Thinking:_

The user wants an aggressive refactoring approach. This is a significant undertaking that will involve:

1. Creating a new package structure
2. Breaking down the 3526-line file into focused modules
3. Proper interfaces and dependency injection
4. Making components testable

I should create a comprehensive plan that:
- Defines the new package structure
- Identifies all the modules to create
- Details what goes into each module
- Addresses the major issues identified
- Maintains backward compatibility during transition

Let me create a detailed refactoring plan.

## Aggressive Refactoring Plan

### New Package Structure
```
code/
├── common/
│   ├── __init__.py           # Public API exports
│   ├── terraform.py          # Terraform operations (plan, apply, validate)
│   ├── boto3_client.py       # Boto3 wrapper, pagination, error handling
│   ├── fileops.py           # File I/O, safe writes, path operations
│   ├── security.py           # Path validation, file permissions, sanitization
│   ├── progress.py           # Progress bars, adaptive rate tracking
│   ├── resource.py           # Resource discovery, dependency tracking
│   ├── registry.py          # Auto-discovered module registry (no hardcoded lists)
│   ├── credentials.py       # AWS credential detection
│   ├── s3_ops.py           # S3 upload/download operations
│   └── errors.py           # Centralized error handling
└── common.py (legacy, for transition)
```

### Module Breakdown

| Module | Lines From `common.py` | Purpose |
|--------|----------------------|---------|
| `terraform.py` | 1027-1577, 1620-1821 | `tfplan1/2/3`, `wrapup`, all terraform commands |
| `boto3_client.py` | 2271-2777 | `call_boto3`, `getresource`, pagination logic |
| `fileops.py` | 1981-2213 | `splitf`, `write_import`, `do_data` |
| `security.py` | 397-610 | `safe_filename`, `safe_write_file`, `secure_terraform_files` |
| `progress.py` | 42-394 | `run_terraform_plan_with_progress`, adaptive rate tracking |
| `resource.py` | 844-1025, 2480-2508 | `call_resource`, `add_dependancy`, `add_known_dependancy` |
| `registry.py` | 614-841 | Auto-discovery of AWS resource modules |
| `credentials.py` | 2574-3526 | `detect_aws_credentials`, `print_credentials_info` |
| `s3_ops.py` | 3021-3180 | `upload_directory_to_s3`, `download_from_s3`, bucket operations |
| `errors.py` | 2801-3018 | `handle_error`, `handle_error2` |

### Key Improvements

**1. Auto-Discovery Registry** (no hardcoded modules)
```python
# code/common/registry.py
def discover_resource_modules():
    """Auto-discover all get_aws_resources modules."""
    modules = {}
    for module_file in Path("code/get_aws_resources").glob("aws_*.py"):
        module_name = module_file.stem.replace("aws_", "")
        modules[module_name] = importlib.import_module(f"get_aws_resources.aws_{module_name}")
    return modules
```

**2. Proper Error Handling**
```python
# code/common/errors.py
class AWS2TFError(Exception):
    """Base exception for aws2tf errors."""
    pass

class ResourceNotFoundError(AWS2TFError):
    """Resource not found in AWS."""
    pass

class CredentialError(AWS2TFError):
    """AWS credential issues."""
    pass
```

**3. Type Hints Throughout**
```python
# code/common/boto3_client.py
def call_boto3(
    type: str,
    clfn: str,
    descfn: str,
    topkey: str,
    key: str,
    id: Optional[str]
) -> List[Dict[str, Any]]:
    """Call boto3 with pagination."""
```

**4. Remove Global State**
```python
# Instead of context.rproc, context.rdep
class ResourceTracker:
    def __init__(self):
        self._processed: Dict[str, bool] = {}
        self._pending: Dict[str, bool] = {}
    
    def mark_processed(self, resource_type: str, resource_id: str) -> None:
        self._processed[f"{resource_type}.{resource_id}"] = True
```

**5. Exit Code Constants**
```python
# code/common/constants.py
class ExitCode:
    SUCCESS = 0
    PLAN_ERROR = 18
    VALIDATION_FAILED = 20
    PLAN_CHANGES = 23
    # ... all magic numbers named
```

### Migration Strategy

**Phase 1**: Create new package structure, copy functions with imports
**Phase 2**: Add type hints and fix error handling (ruff/pyright)
**Phase 3**: Remove global state, inject dependencies
**Phase 4**: Delete dead code, consolidate duplicates
**Phase 5**: Write unit tests for each module
**Phase 6**: Update imports across codebase, delete `common.py`

### Risk Mitigation

1. **Keep `common.py` as shim** during transition
2. **Run full test suite** after each module extraction
3. **Git checkpoint** at each phase
4. **Gradual imports** - old code uses new modules incrementally

**Tool: question**

**Input:**
```json
{
  "questions": [
    {
      "header": "Testing",
      "multiple": false,
      "options": [
        {
          "description": "Write tests as we extract each module. Slower but catches issues early.",
          "label": "Test-first extraction"
        },
        {
          "description": "Extract all modules, then write comprehensive tests. Faster, riskier.",
          "label": "Test-last"
        },
        {
          "description": "Add tests only for critical modules (terraform, boto3_client, security).",
          "label": "Partial coverage"
        }
      ],
      "question": "What's your approach to testing during this aggressive refactor?"
    },
    {
      "header": "Timeline",
      "multiple": false,
      "options": [
        {
          "description": "Work on this aggressively. I want it done.",
          "label": "One sprint (~1 week)"
        },
        {
          "description": "Spread over multiple sprints with checkpoints.",
          "label": "Two sprints (~2 weeks)"
        },
        {
          "description": "Even more gradual to minimize disruption.",
          "label": "Three sprints (~3 weeks)"
        }
      ],
      "question": "What's your preferred timeline?"
    }
  ]
}
```

**Output:**
```
User has answered your questions: "What's your approach to testing during this aggressive refactor?"="we cant test", "What's your preferred timeline?"="Three sprints (~3 weeks)". You can now continue with the user's answers in mind.
```

---

## Assistant (Plan · glm-4.7 · 88.7s)

_Thinking:_

Interesting - "we cant test" is the answer. This suggests either:
1. No existing tests for common.py
2. Lack of testing infrastructure
3. Or they mean testing during the refactor specifically

Given they want a 3-week timeline and aggressive refactor without testing, I should:
1. Focus on structural improvements without test coverage
2. Emphasize validation through running the actual tool
3. Add defensive programming since tests won't catch regressions
4. Be extra careful about preserving behavior

Let me adjust the plan to be test-less but still maintainable and safe.

## Updated Plan (No Testing, 3-Week Timeline)

### Week 1: Structure & Core Modules
**Goal**: Extract low-risk, self-contained modules

- Day 1-2: Create `code/common/` package, extract `security.py`, `fileops.py`, `constants.py`
- Day 3-4: Extract `progress.py`, `errors.py`, `registry.py`
- Day 5: Validate by running `./aws2tf.py -t vpc` (smoke test)

### Week 2: AWS & Resource Modules
**Goal**: Extract AWS-facing code

- Day 1-2: Extract `boto3_client.py` (highest risk - core functionality)
- Day 3-4: Extract `resource.py`, `credentials.py`, `s3_ops.py`
- Day 5: Validate by running full import on a test VPC

### Week 3: Terraform & Cleanup
**Goal**: Finish extraction and cleanup

- Day 1-2: Extract `terraform.py` (complex - plan/apply logic)
- Day 3: Add `__init__.py` with clean public API
- Day 4: Update all imports across codebase to use new modules
- Day 5: Delete `common.py`, run full validation

### Validation Strategy (No Tests)
Since we can't test, we validate via:

1. **Smoke Test After Each Extraction**
   ```bash
   ./aws2tf.py -t vpc  # Simple, known-good case
   ```

2. **Ruff Type/Lint Check**
   ```bash
   ruff check . && ruff check --select ANN .
   ```

3. **Real-World Validation**
   - Week 1: Import 1 VPC with subnets
   - Week 2: Import complex stack (EC2 + IAM + Security Groups)
   - Week 3: Full account scan of small test account

### Risk Mitigation (Test-Less)

**1. Don't Change Behavior, Just Move**
```python
# Bad - changes logic
if resource_id is not None:
    pass

# Good - exact copy, then add type hints
def add_dependency(type: str, id: Optional[str]) -> None:
    if id is None:
        log_warning("WARNING: add_dependancy: id is None")
        return
    # ... rest unchanged
```

**2. Preserve All Exports in `common/__init__.py`**
```python
# Makes old imports still work during transition
from code.common.security import *
from code.common.fileops import *
# ... etc
```

**3. Keep Global `context` Access Initially**
```python
# Phase 1: Keep using context
from context import rproc

# Phase 2 (later): Inject as parameter
class ResourceTracker:
    def __init__(self, context: Context):
        self.context = context
```

**4. Detailed Commit Messages**
```
Extract fileops.py from common.py
- Moved: splitf, write_import, do_data
- Added type hints
- No behavior changes
- Validated: ./aws2tf.py -t vpc passes
```

### What NOT to Do Yet
- ❌ Remove global state (breaks too much at once)
- ❌ Rename abbreviated variables (`clfn` → `client_function`)
- ❌ Consolidate error handling patterns
- ❌ Add dependency injection

These are "Phase 2" improvements after the structural refactor is complete.

**Tool: question**

**Input:**
```json
{
  "questions": [
    {
      "header": "Start Now?",
      "multiple": false,
      "options": [
        {
          "description": "Start Week 1: Create package and extract security/fileops modules",
          "label": "Yes, begin Week 1"
        },
        {
          "description": "Need to discuss something else first",
          "label": "No, wait"
        }
      ],
      "question": "Ready to begin the 3-week refactoring plan?"
    }
  ]
}
```

**Output:**
```
User has answered your questions: "Ready to begin the 3-week refactoring plan?"="No, wait". You can now continue with the user's answers in mind.
```

---

## User

Write this to a common_refactor.md

---

## Assistant (Plan · glm-4.7)

---

