#!/usr/bin/env python3

import os
import subprocess
import sys
import zipfile

infilename, sign_key = sys.argv[1:]

def ExtractFingerprint(cert):
    cmd = ['openssl', 'x509', '-sha256', '-fingerprint', '-noout', '-in', cert]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE)
    return proc.stdout.decode('utf-8').split('=')[1].replace(':', '')

def patch_trichrome(infilename, sign_key):
    orig_certdigest = "32a2fc74d731105859e5a85df16d95f102d85b22099b8064c5d8915c61dad1e0"
    new_certdigest = ExtractFingerprint(sign_key).lower().rstrip()

    with zipfile.ZipFile(infilename, 'r') as zin, zipfile.ZipFile(infilename + ".patched", 'w') as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == 'AndroidManifest.xml':
                # Make sure we can find the certdigest
                data.rindex(orig_certdigest.encode('utf-16-le'))
                # Replace it
                data = data.replace(orig_certdigest.encode('utf-16-le'), new_certdigest.encode('utf-16-le'))
            zout.writestr(info, data)

    # Delete the original file
    os.remove(infilename)

    # Rename the output file to the original file name
    os.rename(infilename + ".patched", infilename)

if "Browser_" in infilename or "BrowserWebView_" in infilename:
    patch_trichrome(infilename, sign_key)
