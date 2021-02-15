#! usr/bin/env/ python
import sys
import re
import copy
from collections import OrderedDict
from collections import Counter


##### CLASS EXON #####
class Exon(object):
    def __init__(self, exon_in, contig_name_in, start_in, stop_in):
        self.exon = exon_in
        self.gene = exon_in.split("_")[0]
        self.contig_name = contig_name_in
        self.start = start_in
        self.stop = stop_in
### Getters
    def getExon(self):
        return self.exon
    def getContig(self):
        return self.contig_name
    def getStart(self):
        return self.start
    def getStop(self):
        return self.stop
    def getGene(self):
        return self.gene

##### CLASS GENE #####
class Gene(object):
    def __init__(self, gene_in, first_candLocus):
        self.gene = gene_in
        self.candidateLoci = [first_candLocus]
### Getters
    def getGene(self):
        return self.gene
    def getCandLoci(self):
        return self.candidateLoci
### Setters
    def addCandLocus(self, locus_in):
        self.candidateLoci.append(locus_in)

def most_frequent(List):
    occurence_count = Counter(List)
    return occurence_count.most_common(1)[0][0]


#Open infile with all genes (blast output from BlastResults.txt). Infile nature is very important:
#   Column 0: Locus name FROM INFERRED EXONS
#   Column 1: Region name FROM GENOME
#   Column 2: e value
#   Column 3: start point FROM INFERRED EXONS
#   Column 4: stop point FROM INFERRED EXONS
#   Column 5: start point FROM GENOME
#   Column 6: stop point FROM GENOME

BlastResults = open(sys.argv[1], 'r')
GFF_read = open(sys.argv[2], 'r')
GFF_genes_out = open(sys.argv[3], 'w')
GFF_exons_out = open(sys.argv[4], 'w')
GFF_cds_out = open(sys.argv[5], 'w')
log = open(sys.argv[6], 'w')

exon_dict = {}
gene_dict = {}
capturedGenes = []
gffGenes = []
num = 0 

for blast in BlastResults:
    blast = blast.split("\t")
    exon = blast[0]
    gene = exon.split("_")[0]
    log.write("Gene: " + gene + '\n')
    if exon not in exon_dict:
        contig = blast[1]
        start = blast[5]
        stop = blast[6].strip()
        new_exon = Exon(exon, contig, start, stop)
        exon_dict[exon] = new_exon

gff_dict = {}
for line_unsplit in GFF_read:
    line = line_unsplit.split("\t")
    haystack_locus = line[0]
    kind = line[2]
    haystack_start = line[3]
    haystack_stop = line[4]
    if kind == "gene":
        for needle in exon_dict:
            if exon_dict[needle].getContig() == haystack_locus:
                if ((int(haystack_start) <= int(exon_dict[needle].getStart())) and (int(haystack_stop) >= int(exon_dict[needle].getStop()))):
#                    GFF_genes_out.write(line_unsplit) 
                    candLocus = line[8].split("gene=")[1]
                    candLocus = candLocus.split(";")[0]
                    needleGene = exon_dict[needle].getGene()
                    if needleGene in gene_dict:
                        # add candLocus to gene object
                        gene_dict[needleGene].addCandLocus(candLocus)
                    else:
                        # create gene object and initialize with candLocus
                        new_gene = Gene(needleGene, candLocus)
                        gene_dict[needleGene] = new_gene
                    log.write("Exon " + exon_dict[needle].getExon() + "found in GFF as: " + candLocus + "\n")

GFF_read.close()
log.write("\n\n\nFIND CAPTURED GENES:")
for gene in gene_dict:
    capturedGene = most_frequent(gene_dict[gene].getCandLoci())
    log.write(gene + ": " + capturedGene + "\n")
    capturedGenes.append(capturedGene)

# Here I'm adding and removing genes I found via manual search to the capturedGene list 15 Feb 2021
capturedGenes.remove("FGFR2")
capturedGenes.remove("GRIN2B")
capturedGenes.remove("UPF3B")
capturedGenes.remove("LOC116518885")
capturedGenes.remove("SEC31A")
capturedGenes.remove("IFNGR1")
capturedGenes.remove("SNTG1")
capturedGenes.remove("LOC116520613")
capturedGenes.remove("LOC116503105")
capturedGenes.remove("LOC116524024")
capturedGenes.remove("LOC116520185")
capturedGenes.remove("SYMPK")
capturedGenes.remove("SYMPK")
capturedGenes.remove("LOC116522919")
capturedGenes.remove("LOC116519247")
capturedGenes.remove("LOC116515672")
capturedGenes.remove("LOC116516442")
capturedGenes.extend("ATP5MC2", "CATSPER1", "RNH1", "LOC116522919", "LOC116503212", "TRPC6", "SV2A", "LOC116503105", , "LOC116507994", "MDM2", "FOXA3", "AMDHD1", "HSPA2", "LOC116507565")
          
log.write("\n\nFinding the captured genes in the GFF\n")

GFF_read = open(sys.argv[2], 'r')
for region in GFF_read:
    region_split = region.split("\t")
    kind = region_split[2]
    if "gene=" in region_split[8]:
        gene_inquire = region_split[8].split("gene=")[1]
        gene_inquire = gene_inquire.split(";")[0]
        log.write("GFF gene: " + gene_inquire + "\n")
        if gene_inquire in capturedGenes:
            if kind == "gene":
                GFF_genes_out.write(region) 
                gffGenes.append(gene_inquire)
            elif kind == "exon":
                GFF_exons_out.write(region)
            elif kind == "CDS":
                GFF_cds_out.write(region)
        else:
            log.write(gene_inquire + " has no match\n")

log.write("\n\nCaptured gene list:\n")
for i in capturedGenes:
    log.write(i + "\n")

log.write("\n\nDuplicates in captured gene list:\n")
log.write([item for item, count in Counter(capturedGenes).items() if count > 1])

BlastResults.close()
GFF_read.close()
GFF_genes_out.close()
GFF_exons_out.close()
GFF_cds_out.close()
log.close()
