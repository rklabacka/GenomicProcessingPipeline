#! usr/bin/env/ python
import sys
import re

VCF_in = open(sys.argv[1], 'r')
TSV_out = open(sys.argv[2], 'w')
log = open(sys.argv[6], 'w')

for blast in BlastResults:
    blast = blast.split("\t")
    exon = blast[0]
    gene = exon.split("_")[0]
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
    capturedGenes.add(capturedGene)

# Here I'm adding and removing genes I found via manual search to the capturedGene list 15 Feb 2021
capturedGenes.remove("FGFR2")
capturedGenes.remove("GRIN2B")
capturedGenes.remove("SEC31A")
capturedGenes.remove("IFNGR1")
capturedGenes.remove("SNTG1")
capturedGenes.remove("LOC116520613")
capturedGenes.remove("LOC116524024")
capturedGenes.remove("LOC116520185")
capturedGenes.remove("LOC116519247")
capturedGenes.remove("FRY")
capturedGenes.remove("HDAC4")
capturedGenes.remove("LOC116502493")
capturedGenes.remove("LOC116507472")
# capturedGenes.remove("LOC116515779")
capturedGenes.remove("LOC116518885")
capturedGenes.remove("LOC116520346")
capturedGenes.remove("LOC116522496")
capturedGenes.remove("RBMS3")
capturedGenes.remove("STK17A")

capturedGenes.add("ATP5MC2")
capturedGenes.add("CATSPER1")
capturedGenes.add("RNH1")
capturedGenes.add("LOC116503212")
capturedGenes.add("TRPC6")
capturedGenes.add("SV2A")
capturedGenes.add("LOC116503105")
capturedGenes.add("LOC116507994")
capturedGenes.add("MDM2")
capturedGenes.add("FOXA3")
capturedGenes.add("AMDHD1")
capturedGenes.add("HSPA2")
capturedGenes.add("LOC116507565")
          
log.write("\n\nFinding the captured genes in the GFF\n")

GFF_read = open(sys.argv[2], 'r')
for region in GFF_read:
    region_split = region.split("\t")
    kind = region_split[2]
    if "gene=" in region_split[8]:
        gene_inquire = region_split[8].split("gene=")[1]
        gene_inquire = gene_inquire.split(";")[0]
        if gene_inquire in capturedGenes:
            if kind == "gene":
                GFF_genes_out.write(region) 
                gffGenes.append(gene_inquire)
            elif kind == "exon":
                GFF_exons_out.write(region)
            elif kind == "CDS":
                GFF_cds_out.write(region)

log.write("\n\nCaptured gene list:\n")
for i in capturedGenes:
    log.write(i + "\n")

log.write("\n\nDuplicates in captured gene list:\n")
#log.write([item for item, count in Counter(capturedGenes).items() if count > 1])

BlastResults.close()
GFF_read.close()
GFF_genes_out.close()
GFF_exons_out.close()
GFF_cds_out.close()
log.close()
