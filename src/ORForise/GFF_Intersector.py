from importlib import import_module
import argparse
import collections
from datetime import date
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-dna', '--genome_DNA', required=True, help='Genome DNA file (.fa) which both annotations '
                                                                'are based on')
parser.add_argument('-rt', '--reference_tool', required=False,
                    help='Which tool format to use as reference? - Default: Standard Ensembl GFF format, can be '
                         'Prodigal or any of the other tools available')
parser.add_argument('-ref', '--reference_annotation', required=True,
                    help='Which reference annotation file to use as reference?')
parser.add_argument('-at', '--additional_tool', required=True,
                    help='Which tool format to use as additional?')
parser.add_argument('-add', '--additional_annotation', required=True,
                    help='Which annotation file to add to reference annotation?')
parser.add_argument('-cov', '--coverage', default=100, type=int, required=False,
                    help='ORF coverage of Gene in percentage - Default: 100 == exact match')
parser.add_argument('-o', '--output_file', required=True,
                    help='Output filename')
args = parser.parse_args()


def gff_writer(genome_ID, genome_DNA,reference_annotation, reference_tool, ref_gene_set, additional_annotation, additional_tool, genes_To_Keep, output_file):
    write_out = open(output_file, 'w')
    write_out.write("##gff-version\t3\n#\tGFF_Intersector\n#\tRun Date:" + str(date.today()) + '\n')
    write_out.write("##Genome DNA File:" + genome_DNA + '\n')
    write_out.write("##Original File: " + reference_annotation + "\n##Intersecting File: " + additional_annotation + '\n')
    for pos, data in genes_To_Keep.items():
        pos_ = pos.split(',')
        start = pos_[0]
        stop = pos_[-1]
        strand = data[0]
        type = 'original'
        entry = (
                    genome_ID + '\t' + type + '\tORF\t' + start + '\t' + stop + '\t.\t' + strand + '\t.\tID=Original_Annotation;Coverage=' + str(
                data[1]) + '\n')
        write_out.write(entry)


def comparator(genome_DNA, reference_tool, reference_annotation, additional_tool, additional_annotation, coverage, output_file):  # Only works for single contig genome
    genome_seq = ""
    with open(genome_DNA, 'r') as genome_fasta:
        for line in genome_fasta:
            line = line.replace("\n", "")
            if not line.startswith('>'):
                genome_seq += str(line)
            else:
                genome_ID = line.split()[0].replace('>', '')
    ###########################################
    if not reference_tool:  # IF using Ensembl for comparison
        ref_genes = collections.OrderedDict()  # Order is important
        count = 0
        with open(reference_annotation, 'r') as genome_gff:
            for line in genome_gff:
                line = line.split('\t')
                try:
                    if "CDS" in line[2] and len(line) == 9:
                        start = int(line[3])
                        stop = int(line[4])
                        strand = line[6]
                        pos = str(start)+','+str(stop)
                        ref_genes.update({pos:[strand,'ref']})
                        count += 1
                except IndexError:
                    continue
    else:  # IF using a tool as reference
        try:
            reference_tool_ = import_module('Tools.' + reference_tool + '.' + reference_tool,
                                             package='my_current_pkg')
        except ModuleNotFoundError:
            try:
                reference_tool_ = import_module('ORForise.Tools.' + reference_tool + '.' + reference_tool,
                                             package='my_current_pkg')
            except ModuleNotFoundError:
                sys.exit("Tool not available")
        reference_tool_ = getattr(reference_tool_, reference_tool)
        ############ Reformatting tool output for ref_genes
        ref_genes = reference_tool_(reference_annotation, genome_seq)
    ref_gene_set = list(ref_genes.keys())
    ############################## Get Add'l
    try:
        additional_tool_ = import_module('Tools.' + additional_tool + '.' + additional_tool,
                                        package='my_current_pkg')
    except ModuleNotFoundError:
        try:
            additional_tool_ = import_module('ORForise.Tools.' + additional_tool + '.' + additional_tool,
                                            package='my_current_pkg')
        except ModuleNotFoundError:
            sys.exit("Tool not available")
    additional_tool_ = getattr(additional_tool_, additional_tool)
    additional_orfs = additional_tool_(additional_annotation, genome_seq)
    ##############################


    genes_To_Keep = collections.OrderedDict()

    if coverage == 100:
        for orf, data in additional_orfs.items():
            o_Start = int(orf.split(',')[0])
            o_Stop = int(orf.split(',')[1])
            o_Strand = data[0]
            try:
                if ref_genes[str(o_Start) + ',' + str(o_Stop)]:
                    genes_To_Keep.update(
                        {str(o_Start) + ',' + str(o_Stop): [o_Strand, coverage]})  # o_ and g_ would be the same here
            except KeyError:
                continue
    else:
        for orf, data in additional_orfs.items():  # Currently allows ORF to be bigger than Gene
            o_Start = int(orf.split(',')[0])
            o_Stop = int(orf.split(',')[1])
            o_Strand = data[0]
            orf_Set = set(range(int(o_Start), int(o_Stop) + 1))
            for gene, g_data in ref_genes.items():  # Very ineffecient
                g_Start = int(gene.split(',')[0])
                g_Stop = int(gene.split(',')[1])
                g_Strand = g_data[0]
                gene_Set = set(range(int(g_Start), int(g_Stop) + 1))
                overlap = len(orf_Set.intersection(gene_Set))
                cov = 100 * float(overlap) / float(len(gene_Set))
                if abs(o_Stop - g_Stop) % 3 == 0 and o_Strand == g_Strand and cov >= coverage:
                    genes_To_Keep.update({str(g_Start) + ',' + str(g_Stop): [g_Strand, int(cov)]})
                if g_Start > o_Stop:
                    break
    #########################################################
    gff_writer(genome_ID, genome_DNA,reference_annotation, reference_tool, ref_gene_set, additional_annotation, additional_tool, genes_To_Keep, output_file)


if __name__ == "__main__":
    comparator(**vars(args))

    print("Complete")
