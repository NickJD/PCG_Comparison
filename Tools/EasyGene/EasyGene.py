import collections
import sys
sys.path.append('../')
from DNA_Reverse_Compliment import revCompIterative

def EasyGene(input_to_analyse,Genome):

    EasyGene_ORFs = collections.OrderedDict()
    Genome_Size = len(Genome)
    Genome_rev = revCompIterative(Genome)

    with open('EasyGene/' + input_to_analyse, 'r') as EasyGene_input:
        for line in EasyGene_input:
            line = line.split()
            if len(line) >=9 and "Chromosome" in line[0] and "CDS" in line[2]:
                start = int(line[3])
                stop = int(line[4])
                strand = line[6]
                if '-' in strand:  # Reverse Compliment starts and stops to confirm to our definition
                    # Switched to match Sense Strand
                    r_start = Genome_Size - stop
                    r_stop = Genome_Size - start
                    startCodon = Genome_rev[r_start:r_start + 3]
                    stopCodon = Genome_rev[r_stop - 2:r_stop + 1]


                elif '+' in strand:
                    startCodon = Genome[start - 1:start - 1 + 3]
                    stopCodon = Genome[stop - 3:stop - 1 + 1]

                po = str(start) + ',' + str(stop)
                orf = [strand, startCodon, stopCodon]
                EasyGene_ORFs.update({po: orf})

    # TO make sure all ORFs are in order - Not Working
    #EasyGene_ORFs = collections.OrderedDict(sorted(EasyGene_ORFs.items(), key=lambda t: t[0]))
    return EasyGene_ORFs

