import random, string

from annotateOffs import *

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.backends.backend_pdf as pltBack


plotRel = False

def plot(maxMMs, guideGcs):
    xVals = []
    yVals = []

    studyX = defaultdict(list)
    studyY = defaultdict(list)
    studyLabels = defaultdict(list)
    for name, maxMM in maxMMs.iteritems():
        study = name.split("_")[0]
        xVals.append(guideGcs[name])
        studyX[study].append( guideGcs[name] )
        studyY[study].append( maxMM )
        guideName = string.split(name, "_", 1)[1]

        studyLabels[study].append(guideName )

    print studyX
    print studyY
    outfname = "readFraction" + '.pdf'
    pdf = pltBack.PdfPages(outfname)
    fig = plt.figure(figsize=(5,5),
                   dpi=300, facecolor='w')
    fig = plt.figure()

    colors = ["green", "blue", "black", "yellow", "red", "grey"]
    markers = ["o", "s", "+", ">", "<", "^"]
    studyNames = []
    figs = []
    i = 0
    for study, xVals in studyX.iteritems():
        yVals = studyY[study]
        studyFig = plt.scatter(xVals, yVals, \
            alpha=.5, \
            marker=markers[i], \
            s=30, \
            color=colors[i])
        figs.append(studyFig)
        studyNames.append(study)
        i+=1

        labels = studyLabels[study]
        for x, y, label in zip(xVals, yVals, labels):
               # arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0')
               # bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5))
               plt.annotate(
                  label, fontsize=6, rotation=30, ha="right", rotation_mode="anchor",
                  xy = (x, y), xytext = (0,0), alpha=.5,
                  textcoords = 'offset points', va = 'bottom')

    plt.legend(figs,
           studyNames,
           scatterpoints=1,
           loc='upper left',
           ncol=3,
           fontsize=10)

    plt.xlabel("GC content")
    if plotRel:
        plt.ylabel("relative efficacy (fraction of reads relative to all indel-causing reads)")
    else:
        plt.ylabel("Efficacy of on-target / Fraction of on-target reads (Tsai)")
    fig.savefig(pdf, format = 'pdf')
    pdf.close()
    print "Wrote %s" % outfname

def countMms(string1, string2):
    " count mismatches between two strings "
    mmCount = 0
    string1 = string1.upper()
    string2 = string2.upper()
    diffLogo = []
    for pos in range(0, len(string1)):
        if string1[pos]!=string2[pos]:
            mmCount+=1
            diffLogo.append("*")
        else:
            diffLogo.append(".")

    return mmCount, "".join(diffLogo)

def annotateOts():
    targetSeqs = {}
    inFname = "offtargets.tsv"
    inRows = []
    for row in iterTsvRows(inFname):
        if "Frock" in row.name:
            continue
        if row.type=="on-target":
            targetSeqs[row.name] = row.seq
        inRows.append(row)

    sums = defaultdict(float)
    for row in inRows:
        sums[row.name] += float(row.score)

    headers = ["name", "guideSeq", "otSeq", "guideGc", "otGc", "assayScore", "mmCount", "diffLogo"]
    rows = [headers]
    maxMMs = defaultdict(int)
    guideGcConts = {}
    i = 0
    for row in inRows:
        #if row.type=="on-target":
            #continue
        if row.type=="off-target":
            continue
        if "Frock" in row.name:
            continue
        guideSeq = targetSeqs[row.name][:-3].upper()
        otSeq = row.seq[:-3].upper()
        mmCount, diffLogo = countMms(guideSeq, otSeq)
        #if mmCount<=4:
            #continue
        otGcCont = gcCont(otSeq)
        guideGc = gcCont(guideSeq)
        otRow = [row.name, guideSeq, otSeq, str(guideGc), str(otGcCont), row.score, str(mmCount), diffLogo]
        rows.append(otRow)
        #dataName = row.name+str(i)
        dataName = row.name
        #maxMMs[row.name+str(i)] = max(maxMMs[row.name], mmCount)
        #maxMMs[dataName] = mmCount + random.random()
        #maxMMs[dataName] = mmCount
        assert(dataName not in maxMMs)
        freq = float(row.score) 
        if plotRel:
            if "Tsai" not in dataName:
                freq = freq/sums[dataName]
                #print "correction: ", dataName, freq, sums[dataName]
        #else:
            #freq = 1.0 - freq
        maxMMs[dataName] = freq

        #guideGcConts[row.name] = guideGc
        #guideGcConts[dataName] = otGcCont+random.random()*3
        guideGcConts[dataName] = guideGc
        i+=1

    ofh = open("annotOfftargets.tsv", "w")
    for row in rows:
        ofh.write("\t".join(otRow))
        ofh.write("\n")
    ofh.close()
    print "wrote %s" % ofh.name

    return maxMMs, guideGcConts

def main():
    maxMMs, guideGcConts = annotateOts()
    plot(maxMMs, guideGcConts)

main()
