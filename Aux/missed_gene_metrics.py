import argparse
import constants
import collections
import numpy as np


parser = argparse.ArgumentParser()
parser.add_argument('-r', '--results', required=True, help='Which output to look at?')
parser.add_argument('-a', '--annotation', required=True, help='Genome Annotation File')

args = parser.parse_args()


def gc_count(dna):
    c = 0
    a = 0
    g = 0
    t = 0
    n = 0
    for i in dna:
        if "C" in i:
            c += 1
        elif "G" in i:
            g += 1
        elif "A" in i:
            a += 1
        elif "T" in i:
            t+=1
        elif "N" in i:
            n+=1
    gc_content = format((g + c) * 100 / (a + t + g + c + n),'.2f')
    n_per = n * 100 / (a + t + g + c + n)
    return n_per,gc_content

def revCompIterative(watson):
    complements = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
    watson = watson.upper()
    watsonrev = watson[::-1]
    crick = ""
    for nt in watsonrev:
        crick += complements[nt]
    return crick

def start_Codon_Count(orfs):
    atg,gtg,ttg,att,ctg,other = 0,0,0,0,0,0
    other_Starts = []
    for orf in orfs.values():
        codon = orf[-2]
        if codon == 'ATG':
            atg += 1
        elif codon == 'GTG':
            gtg += 1
        elif codon == 'TTG':
            ttg += 1
        elif codon == 'ATT':
            att += 1
        elif codon == 'CTG':
            ctg += 1
        else:
            other += 1
            other_Starts.append(codon)
    atg_P = format(100* atg / len(orfs),'.2f')
    gtg_P = format(100 * gtg / len(orfs),'.2f')
    ttg_P = format(100 * ttg / len(orfs),'.2f')
    att_P = format(100 * att  / len(orfs),'.2f')
    ctg_P = format(100 * ctg  / len(orfs),'.2f')
    other_Start_P = format(100 * other / len(orfs),'.2f')
    return atg_P,gtg_P,ttg_P,att_P,ctg_P,other_Start_P,other_Starts

def stop_Codon_Count(orfs):
    tag,taa,tga,other = 0,0,0,0
    other_Stops = []
    for orf in orfs.values():
        codon = orf[-1]
        if codon == 'TAG':
            tag += 1
        elif codon == 'TAA':
            taa += 1
        elif codon == 'TGA':
            tga += 1
        else:
            other += 1
            other_Stops.append(codon)
    tag_p = format(100 * tag  / len(orfs),'.2f')
    taa_p = format(100 * taa  / len(orfs),'.2f')
    tga_p = format(100 * tga / len(orfs),'.2f')
    other_Stop_P = format(100 * other / len(orfs),'.2f')
    return tag_p,taa_p,tga_p,other_Stop_P,other_Stops

def missed_gene_read(results,missed_genes):
    #Missed Genes Read-In
    results_in = open('../Tools/'+results)
    read = False
    for line in results_in:
        if '4557410' in line:
            print("S")
        elif line.startswith('ORFs_Without_Corresponding_Gene_In_Ensembl_Metrics:'):
            break
        line = line.strip()
        if read == True:
            if line.startswith('>'):
                entry = line.split('_')
                entry = entry[1]+'_'+entry[2]
            elif len(line.strip()) > 0:
                startCodon = line[0:3]
                stopCodon = line[-3:]
                length = len(line)
                missed_genes.update({entry:[line,length,startCodon,stopCodon]})
        if line.startswith('Undetected_Genes:'):
            read = True

    return missed_genes

# def read_original_annotation(gff):
#     genes = collections.OrderedDict()  # Order is important
#     count = 0
#     with open('../genomes/' + gff + '.gff', 'r') as genome_gff:  # Should work for GFF3
#         for line in genome_gff:
#             line = line.split('\t')
#             try:
#                 if "CDS" in line[2] and len(line) == 9:
#                     start = int(line[3])
#                     stop = int(line[4])
#                     strand = line[6]
#                     gene = str(start) + ',' + str(stop) + ',' + strand
#                     genes.update({count: gene})
#                     count += 1
#             except IndexError:
#                 continue
#     return genes

def detail_transfer(genes,missed_genes):
    for missed,m_details in missed_genes.items():
        try:
            details = genes[missed]
            gc = details[2]
            up_Overlap = details[3]
            down_Overlap = details[4]
            m_details.insert(2,gc)
            m_details.insert(3,up_Overlap)
            m_details.insert(4,down_Overlap)
        except KeyError:
            pass
    return missed_genes


def result_compare(results,annotation):
    genome = ""
    with open('../genomes/' + annotation + '.fa', 'r') as genome_file:
        for line in genome_file:
            line = line.replace("\n", "")
            if ">" not in line:
                genome += str(line)

    missed_genes = collections.OrderedDict()
    missed_genes = missed_gene_read(results,missed_genes)
#    genes = read_original_annotation(gff)
    #Analysis

    genome_Rev = revCompIterative(genome)
    genome_Size = len(genome)
    genes = collections.OrderedDict()
    lengths_PCG = []
    gene_Overlaps = []
    count = 0
    prev_Stop = 0
    strands = collections.defaultdict(int)
    short_PCGs = []
    pcg_GC = []
    with open('../genomes/' + annotation + '.gff', 'r') as genome_gff:
        for line in genome_gff:
            line = line.split('\t')
            try:
                if "CDS" in line[2] and len(line) == 9:
                    start = int(line[3])
                    stop = int(line[4])
                    strand = line[6]
                    strands[strand] += 1
                    gene = str(start) + ',' + str(stop) + ',' + strand
                    if strand == '-':
                        r_Start = genome_Size - stop
                        r_Stop = genome_Size - start
                        seq = (genome_Rev[r_Start:r_Stop + 1])
                    elif strand == '+':
                        seq = (genome[start - 1:stop])
                    startCodon = seq[0:3]
                    stopCodon = seq[-3:]
                    length = stop - start
                    if length < constants.SHORT_ORF_LENGTH:
                        short_PCGs.append(gene)
                        #print(line)
                    n_per, gc = gc_count(seq)
                    pcg_GC.append(float(gc))
                    lengths_PCG.append(length)
                    if prev_Stop > start:
                        overlap = prev_Stop - start
                        gene_Overlaps.append(overlap)
                    else:
                        overlap = 0
                    count += 1
                    prev_Stop = stop
                    pos = str(start)+'_'+str(stop)

                    if genes:
                        prev_details = genes[prev_pos]
                        prev_details.insert(4,overlap)
                        genes.update({prev_pos:prev_details})
                    genes.update({pos:[strand,length,gc,overlap,seq,startCodon,stopCodon]})
                    prev_pos = pos



            except IndexError:
                continue

    median_PCG = np.median(lengths_PCG)
    median_PCG_Olap = np.median(gene_Overlaps)
    longest_Olap = max(gene_Overlaps)
    num_overlaps = len(gene_Overlaps)
    gc_median = format(np.median(pcg_GC),'.2f')
    num_Short_PCGs = len(short_PCGs)

    missed_genes = detail_transfer(genes,missed_genes)

    atg_P, gtg_P, ttg_P, att_P, ctg_P, other_Starts_P,other_Starts = start_Codon_Count(genes)
    tag_P, taa_P, tga_P, other_Stops_P,other_Stops = stop_Codon_Count(genes)
    m_atg_P, m_gtg_P, m_ttg_P, m_att_P, m_ctg_P, m_other_Starts_P,m_other_Starts = start_Codon_Count(missed_genes)
    m_tag_P, m_taa_P, m_tga_P, m_other_Stops_P,m_other_Stops = stop_Codon_Count(missed_genes)

    output = ("Number of Protein Coding Genes in " + str(annotation) + " : " + str(len(lengths_PCG)) + ", Median Length of PCGs: " +
              str(median_PCG) + ", Min Length of PCGs: " + str(min(lengths_PCG)) + ", Max Length of PCGs: " + str(max(lengths_PCG)) +
              ", Number of PCGs on Pos Strand: " + str(strands['+']) + ", Number of PCGs on Neg Strand: " + str(strands['-']) +
              ", Median GC of PCGs: " + str(gc_median) + ", Number of Overlapping PCGs: " + str(num_overlaps) +
              ", Longest PCG Overlap: " + str(longest_Olap) + ", Median PCG Overlap: " + str(median_PCG_Olap) +
              ", Number of PCGs less than 100nt: " + str(num_Short_PCGs) +

              '\nPercentage of Genes starting with ATG - Annotation/Missed: ' + atg_P + ' ' + m_atg_P +
              '\nPercentage of Genes starting with GTG - Annotation/Missed: ' + gtg_P + ' ' + m_gtg_P +
              '\nPercentage of Genes starting with TTG - Annotation/Missed: ' + ttg_P + ' ' + m_ttg_P +
              '\nPercentage of Genes starting with ATT - Annotation/Missed: ' + att_P + ' ' + m_att_P +
              '\nPercentage of Genes starting with CTG - Annotation/Missed: ' + ctg_P + ' ' + m_ctg_P +
              '\nPercentage of Genes starting with Alternative Start Codon - Annotation/Missed: ' + other_Starts_P + ' ' + m_other_Stops_P +
              '\nPercentage of Genes ending with TAG - Annotation/Missed: ' + tag_P + ' ' + m_tag_P +
              '\nPercentage of Genes ending with TAA - Annotation/Missed: ' + taa_P + ' ' + m_taa_P +
              '\nPercentage of Genes ending with TGA - Annotation/Missed: ' + tga_P + ' ' + m_tga_P +
              '\nPercentage of Genes ending with Alternative Stop Codon - Annotation/Missed: ' + other_Stops_P + ' ' + m_other_Stops_P)




    print(output)





if __name__ == "__main__":
    result_compare(**vars(args))














