import server as ws
import subprocess
import csv
import os
from os import walk
import json
import sys
import urllib.request
import zipfile
import tarfile
import platform

# Detect OS
OS = platform.system()


def findPGN():

    for (dirpath, dirnames, filenames) in walk('PGN/'):
        for pgn in filenames:
            fname, fext = os.path.splitext(pgn)
            if fext == '.pgn':
                return True

    return False


def downloadTARGZ(url, inPath, inFile, outPath, outFile):

    if not os.path.isfile(os.path.join(outPath, outFile)):
        urllib.request.urlretrieve(url, 'tmp.tar.gz')

        with tarfile.open('tmp.tar.gz') as tar:
            with open(os.path.join(outPath, outFile), 'wb') as f:
                f.write(tar.extractfile(inFile).read())

        os.remove('tmp.tar.gz')


def downloadZip(url, inPath, inFile, outPath, outFile):

    if not os.path.isfile(os.path.join(outPath, outFile)):
        urllib.request.urlretrieve(url, 'tmp.zip')

        # Decompress and save individually
        with zipfile.ZipFile('tmp.zip') as z:
            with open(os.path.join(outPath, outFile), 'wb') as f:
                f.write(z.read(os.path.join(inPath, inFile)))

        os.remove('tmp.zip')


def installTool():

    if OS == 'Windows':
        inPath = 'ordo-1.2.6-win/'
        inFile = 'ordo-win64.exe'
        outPath = ''
        outFile = 'ordo.exe'
        url = 'https://github.com/michiguel/Ordo/releases/download/v1.2.6/ordo-1.2.6-win.zip'
        downloadZip(url, inPath, inFile, outPath, outFile)
    else:
        inPath = '/'
        inFile = 'ordo-linux64'
        outPath = ''
        outFile = 'ordo'
        url = 'https://github.com/michiguel/Ordo/releases/download/v1.2.6/ordo-1.2.6.tar.gz'
        downloadTARGZ(url, inPath, inFile, outPath, outFile)


def initGUI():

    if findPGN():
        # IF there are PGN files in folder, then hide overlay
        ws.GUI['welcome-overlay']['visible'] = False
    else:
        # If there are no PGN files, show overlay
        ws.GUI['welcome-overlay']['visible'] = True
        return

    # Load last saved GUI
    try:
        with open('GUI.json') as f:
            tmp = json.load(f)
            if tmp != {}:
                ws.GUI = tmp
    except:
        pass

    # Parse PGN directory and get all PGN files
    ws.GUI['select-pgn']['options'] = []
    for (dirpath, dirnames, filenames) in walk('PGN/'):
        for pgn in filenames:
            # Load all files into combo box
            s = ''
            if len(dirpath) > 4:
                s = '/'
            ws.GUI['select-pgn']['options'].append(dirpath[4:]+s+pgn)


def testPGN():
    # Try PGN in Ordo to see if it is valid
    # Output a minimal CSV file with the players' names
    pgn = 'PGN/'+ws.GUI['select-pgn']['value']
    subprocess.call(['ordo.exe', '-U 0', '-s1',
                     '-p',  pgn, '-c', 'test.csv'])

    # Load all players from PGNs from CSV file into combo box
    ws.GUI['select-anchor']['options'] = []
    with open("test.csv", "r") as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
            if i == 0:
                continue
            ws.GUI['select-anchor']['options'].append(line[1])

    # Select first item in the GUI combo box
    ws.GUI['select-anchor']['selected'] = 0
    ws.GUI['select-anchor']['value'] = ws.GUI['select-anchor']['options'][0]


def analyse():
    print('Analizing...')
    pgn = 'PGN/'+ws.GUI['select-pgn']['value']
    anchor = ws.GUI['select-anchor']['value']
    anchorRating = ws.GUI['input-rating']['value']
    subprocess.call(
        ['ordo.exe',
         '-Q', '-N 0', '-D', '-W', '-s500', '-V',
         '-a', anchorRating, '-A', anchor,
         '-U 0,1,2,6,4,7,8,9,10',
         '-j', 'h2h.txt', '-c', 'results.csv', '-o', 'results.txt', '-p', pgn]
    )

    s = ('**Match:** {}\n'
         '**LC0-version:** {}\n'
         '**LC0 options:** {}\n'
         '**Time control:** {}\n'
         '**Hardware:** {}\n'
         '**Speed:** {}\n'
         '**Book:** {}\n'
         '**Tablebases:** {}\n'
         '**Adjudication:** {}\n'
         '**Software:** {}\n'
         '**Comment:** {}\n\n').format(ws.GUI['input-match']['value'],
                                       ws.GUI['input-lc0version']['value'],
                                       ws.GUI['input-lc0options']['value'],
                                       ws.GUI['input-tc']['value'],
                                       ws.GUI['input-hardware']['value'], ws.GUI['input-speed']['value'],
                                       ws.GUI['input-book']['value'],
                                       ws.GUI['input-tb']['value'],
                                       ws.GUI['input-adjudication']['value'],
                                       ws.GUI['input-software']['value'],
                                       ws.GUI['input-comments']['value']
                                       )

    with open("results.txt", "r") as f:
        ws.GUI['label-results']['text'] = s + "```" + f.read() + "```"


installTool()
ws.initGUI(initGUI)
ws.onClick('btn-report', analyse)
ws.onChange('select-pgn', testPGN)
ws.startGUI('index.html')
