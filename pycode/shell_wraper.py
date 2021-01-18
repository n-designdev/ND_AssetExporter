import subprocess
from subprocess import PIPE
order_str = "Y:\\tool\\MISC\\Python2710_amd64_vs2010\\python.exe Y:\\tool\\ND_Tools\\DCC\\ND_AssetExporter\\pycode\\main.py"
output_file = "Y:\\tool\\ND_Tools\\DCC\\ND_AssetExporter\\log\\result_text.txt"
current_dir = "Y:\\tool\\ND_Tools\\DCC\\ND_AssetExporter\\pycode"
with open(output_file, "w+")as f:
    proc = subprocess.Popen(order_str, shell=True,stdout=f, cwd=current_dir)
    
