import collections
from ..DNA_Reverse_Compliment import  revCompIterative

def GeneMark(input_to_analyse,Genome):
    GeneMark_ORFs = collections.OrderedDict()
    Genome_Size = len(Genome)
    Genome_rev = revCompIterative(Genome)
    prev_Start = 0
    prev_Stop = 0
    started = False
    with open('Tools/GeneMark/' + input_to_analyse, 'r') as GeneMark_input:
        for line in GeneMark_input:
            line = line.split()
            if len(line) == 7:
                started = True
                if 'direct' in line[2] or 'complement' in line[2]:  # Strange Output requires strange code - We select the Longest ORF from each set
                    start = int(line[0])
                    stop = int(line[1])
                    strand = line[2]
                    if 'complement' in strand:  # Reverse Compliment starts and stops adjusted
                        if start != prev_Start:
                            r_start = Genome_Size - stop
                            r_stop = Genome_Size - start
                            strand = '-'
                            startCodon = Genome_rev[r_start:r_start + 3]
                            stopCodon = Genome_rev[r_stop - 2:r_stop + 1]
                            po = str(start) + ',' + str(stop)
                            orf = [strand, startCodon, stopCodon]
                            GeneMark_ORFs.update({po: orf})
                    elif 'direct' in strand:
                        if stop != prev_Stop:
                            startCodon = Genome[start - 1:start+2]
                            stopCodon = Genome[stop - 3:stop]
                            strand = '+'
                            po = str(start) + ',' + str(stop)
                            orf = [strand, startCodon, stopCodon]
                            GeneMark_ORFs.update({po: orf})
                    prev_Start = start
                    prev_Stop = stop
            elif len(line) == 0 and started == True:
                prev_Stop = 0
                prev_Start = 0
    return GeneMark_ORFs

############# This section can be used to select the ORF with highest probability score.
    # with open('Tools/GeneMark/' + input_to_analyse, 'r') as GeneMark_input:
    #     prob_score = 0
    #     started = False
    #
    #     for line in GeneMark_input:
    #         line = line.split()
    #
    #         if len(line) == 7:
    #             if 'direct' in line[2] or 'complement' in line[2] and '....' not in line[6] : # Strange Output requires strange code
    #                 started = True
    #                 start = int(line[0])
    #                 stop = int(line[1])
    #                 score = float(line[5])
    #                 strand = line[2]
    #                 if 'complement' in strand:  # Reverse Compliment starts and stops to confirm to our definition
    #                     if start != prev_Start:
    #                         prob_score = score
    #                         # Switched to match Sense Strand
    #                         r_start = Genome_Size - stop
    #                         r_stop = Genome_Size - start
    #                         strand = '-'
    #                         startCodon = Genome_rev[r_start:r_start + 3]
    #                         stopCodon = Genome_rev[r_stop - 2:r_stop + 1]
    #                         po = str(start) + ',' + str(stop)
    #                         orf = [strand, startCodon, stopCodon]
    #                     elif start == prev_Start and score > prob_score:
    #                         # Switched to match Sense Strand
    #                         prob_score = score
    #                         r_start = Genome_Size - stop
    #                         r_stop = Genome_Size - start
    #                         strand = '-'
    #                         startCodon = Genome_rev[r_start:r_start + 3]
    #                         stopCodon = Genome_rev[r_stop - 2:r_stop + 1]
    #                         po = str(start) + ',' + str(stop)
    #                         orf = [strand, startCodon, stopCodon]
    #                 elif 'direct' in strand:
    #                     if stop != prev_Stop:
    #                         prob_score = score
    #                         startCodon = Genome[start - 1:start - 1 + 3]
    #                         stopCodon = Genome[stop - 3:stop - 1 + 1]
    #                         strand = '+'
    #                         po = str(start) + ',' + str(stop)
    #                         orf = [strand, startCodon, stopCodon]
    #                     elif stop == prev_Stop and score > prob_score:
    #                         prob_score = score
    #                         startCodon = Genome[start - 1:start - 1 + 3]
    #                         stopCodon = Genome[stop - 3:stop - 1 + 1]
    #                         strand = '+'
    #                         po = str(start) + ',' + str(stop)
    #                         orf = [strand, startCodon, stopCodon]
    #                 prev_Start = start
    #                 prev_Stop = stop
    #         elif len(line) == 0 and started == True:
    #             prob_score = 0
    #             prev_Start = 0
    #             prev_Stop = 0
    #             GeneMark_ORFs.update({po: orf})
    #             po = ''
    #             orf = []
    # #Remove last empty dict
    # del GeneMark_ORFs['']
    # print(GeneMark_ORFs)
    # return GeneMark_ORFs
