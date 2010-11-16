""" async example """
import nmap
nma = nmap.PortScannerAsync()
def callback_result(host, scan_result):
    print '------------------'
    print host, scan_result

nma.scan(hosts='10.0.2.15', arguments='-sP', callback=callback_result)
while nma.still_scanning():
    print("Waiting >>>")
    nma.wait(2)   # you can do whatever you want but I choose to wait after the end of the scan

