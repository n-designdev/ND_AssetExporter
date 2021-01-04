import subprocess
from subprocess import PIPE
order_str = "Y:\\tool\\MISC\\Python2710_amd64_vs2010\\python.exe main.py"
output_file = r"Y:\tool\ND_Tools\DCC\ND_AssetExporter\log\result_text.txt"
proc = subprocess.run("cat {} | cat -n >{}".format(order_str, output_file), shell=True, input=order_str, stdout=output_file)