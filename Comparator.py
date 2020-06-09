import collections
import numpy as np

def revCompIterative(watson):
    complements = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
    watson = watson.upper()
    watsonrev = watson[::-1]
    crick = ""
    for nt in watsonrev:
        crick += complements[nt]
    return crick

def orf_Unmatched(o_Start, o_Stop, o_Strand, unmatched_ORFs):
    global genome_Seq,genome_Seq_Rev
    if o_Strand == '-':
        r_Start = genome_Size - o_Stop
        r_Stop = genome_Size - o_Start
        Unmatched_ORF = str(o_Start) + ',' + str(o_Stop) + ',' + o_Strand + ',' +genome_Seq_Rev[r_Start:r_Start+3] + ',' +genome_Seq_Rev[r_Stop - 2:r_Stop + 1]
        seq = (genome_Seq_Rev[r_Start-3:r_Stop+3])
        unmatched_ORFs.update({Unmatched_ORF: seq})
    elif o_Strand == '+':
        Unmatched_ORF = str(o_Start) + ',' + str(o_Stop) + ',' + o_Strand + ',' + genome_Seq[o_Start-1:o_Start+2] + ',' +genome_Seq[o_Stop-3:o_Stop]
        seq = (genome_Seq[o_Start - 1:o_Stop])
        unmatched_ORFs.update({Unmatched_ORF: seq})

def genes_Unmatched(g_Start,g_Stop,g_Strand):
    if g_Strand == '-':
        r_Start = genome_Size - g_Stop
        r_Stop = genome_Size - g_Start
        missed_Gene = str(g_Start) + ',' + str(g_Stop) + ',' + g_Strand + ',' +genome_Seq_Rev[r_Start:r_Start+3] + ',' +genome_Seq_Rev[r_Stop - 2:r_Stop + 1]
        genSeq = (genome_Seq_Rev[r_Start:r_Stop + 1])
        missed_Genes.update({missed_Gene: genSeq})
    elif g_Strand == '+':
        missed_Gene = str(g_Start) + ',' + str(g_Stop) + ',' + g_Strand + ',' + genome_Seq[g_Start-1:g_Start+2] + ',' +genome_Seq[g_Stop-3:g_Stop]
        genSeq = (genome_Seq[g_Start - 1:g_Stop])
        missed_Genes.update({missed_Gene: genSeq})

def match_Statistics(o_Start,o_Stop,g_Start,g_Stop,gene_Set):
    global perfect_Starts,perfect_Stops,start_Difference,stop_Difference,correct_Frame_Number,expanded_Start,expanded_Stop,expanded_CDS
    if g_Start == o_Start:
        perfect_Starts += 1
    if g_Stop == o_Stop:
        perfect_Stops += 1
    ############ Calculate prediction precision and determine frame accuracy
    start_Difference.append(o_Start - g_Start)
    stop_Difference.append(o_Stop - g_Stop)
    correct_Frame_Number += 1
    if o_Start < g_Start and o_Stop > g_Stop:
        expanded_CDS +=1
    if o_Start < g_Start:
        expanded_Start +=1
    if o_Stop > g_Stop:
        expanded_Stop +=1

def start_Codon_Count(orfs):
    atg,gtg,ttg,att,ctg,other = 0,0,0,0,0,0
    other_Starts = []
    for orf in orfs.values():
        codon = orf[1]
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
    atg_P = float((atg) * float(100) / float(len(orfs)))
    gtg_P = float((gtg) * float(100) / float(len(orfs)))
    ttg_P = float((ttg) * float(100) / float(len(orfs)))
    att_P = float((att) * float(100) / float(len(orfs)))
    ctg_P = float((ctg) * float(100) / float(len(orfs)))
    other_Start_P = float(other) * float(100) / float(len(orfs))
    return atg_P,gtg_P,ttg_P,att_P,ctg_P,other_Start_P,other_Starts

def stop_Codon_Count(orfs):
    tag,taa,tga,other = 0,0,0,0
    other_Stops = []
    for orf in orfs.values():
        codon = orf[2]
        if codon == 'TAG':
            tag += 1
        elif codon == 'TAA':
            taa += 1
        elif codon == 'TGA':
            tga += 1
        else:
            other += 1
            other_Stops.append(codon)
    tag_p = float((tag) * float(100) / float(len(orfs)))
    taa_p = float((taa) * float(100) / float(len(orfs)))
    tga_p = float((tga) * float(100) / float(len(orfs)))
    other_Stop_P = float(other) * float(100) / float(len(orfs))
    return tag_p,taa_p,tga_p,other_Stop_P,other_Stops

def candidate_ORF_Selection(gene_Set,candidate_ORFs): # Select ORF from candidates which is most similar to partially detected gene
    current_Coverage = 0
    candidate_ORF_Difference = 0
    pos = ''
    orf_Details = []
    for c_Pos, c_ORF_Details in candidate_ORFs.items():
        o_Start = int(c_Pos.split(',')[0])
        o_Stop = int(c_Pos.split(',')[1])
        coverage = c_ORF_Details[3]
        orf_Set = set(range(o_Start, o_Stop + 1))
        if coverage > current_Coverage:
            current_Coverage = coverage
            # Return set of elements outside the two sets/DNA ranges
            candidate_ORF_Difference = orf_Set.symmetric_difference(gene_Set)
            pos = c_Pos
            orf_Details = c_ORF_Details
        elif coverage == current_Coverage:
            current_ORF_Difference = orf_Set.symmetric_difference(gene_Set) # Pick least different ORF set from the Gene Set
            if len(current_ORF_Difference) > len(candidate_ORF_Difference):
                pos = c_Pos
                orf_Details = c_ORF_Details
        else:
            print("Match filtered out")
    return pos,orf_Details

def tool_comparison(genes,orfs,genome):
    global perfect_Starts,perfect_Stops,perfect_Matches,missed_Genes,unmatched_ORFs,genome_Seq,genome_Seq_Rev,genome_Size,start_Difference,stop_Difference,correct_Frame_Number,expanded_Start,expanded_Stop,expanded_CDS
    pos_Strand, neg_Strand, correct_Frame_Number, perfect_Matches, perfect_Starts, perfect_Stops, correct_Frame_Number, expanded_Start, expanded_Stop, expanded_CDS = 0,0,0,0,0,0,0,0,0,0
    matched_ORFs, genes_Covered,missed_Genes,unmatched_ORFs,out_Of_Frame_ORFs = collections.OrderedDict(),collections.OrderedDict(),collections.OrderedDict(),collections.OrderedDict(),collections.OrderedDict()
    start_Difference,stop_Difference,orf_Lengths,gene_Lengths = [],[],[],[]
    genome_Seq = genome
    genome_Seq_Rev = revCompIterative(genome_Seq)
    genome_Size = len(genome_Seq)
    #Loop through each gene to compare against predicted ORFs
    for gene_Num, gene_Details in genes.items():
        gene_Details = gene_Details.split(',')
        g_Start = int(gene_Details[0])
        g_Stop = int(gene_Details[1])
        g_Strand = gene_Details[2]
        gene_Length = g_Stop - g_Start
        gene_Lengths.append(gene_Length)
        gene_Set = set(range(g_Start, g_Stop + 1))
        ####################### Checking Overlap of ORFs and pick best match - slow but confirms best match
        overlapping_ORFs = collections.OrderedDict()
        perfect_Match = False
        for pos, orf_Details  in orfs.items(): #Check if perfect match, if not check if match covers at least 75% of gene - Loop through ALL ORFs
            o_Start = int(pos.split(',')[0])
            o_Stop = int(pos.split(',')[1])
            o_Strand = orf_Details[0]
            orf_Set = set(range(o_Start, o_Stop + 1))
            if o_Stop <= g_Start or o_Start >= g_Stop: #Not caught up yet or ORFs may not be ordered
                continue
            elif o_Start == g_Start and o_Stop == g_Stop: #If perfect match, break and skip the rest of the ORFs
                perfect_Match = True
                break
            elif g_Start <= o_Start < g_Stop or g_Start < o_Stop < g_Stop: # If at least ORF Stop is within gene range
                overlap = len(gene_Set.intersection(orf_Set))
                coverage = 100 * float(overlap) / float(len(gene_Set))
                orf_Details.append(coverage)
                if abs(o_Stop - g_Stop) % 3 == 0 and o_Strand == g_Strand and coverage >= 75 :  #Only continue if ORF covers at least 75% of the gene and is in frame
                    overlapping_ORFs.update({pos:orf_Details})
                elif coverage >= 75:
                    out_Of_Frame_ORFs.update({pos:orf_Details})
            elif o_Start <= g_Start and o_Stop >= g_Stop: # If ORF is extends one or both ends of the gene
                overlap = len(gene_Set.intersection(orf_Set))
                coverage = 100 * float(overlap) / float(len(gene_Set))
                orf_Details.append(coverage)
                if abs(o_Stop - g_Stop) % 3 == 0 and o_Strand == g_Strand and coverage >= 75:  #Only continue if ORF covers at least 75% of the gene and is in frame
                    overlapping_ORFs.update({pos:orf_Details})
                elif coverage >= 75:
                    out_Of_Frame_ORFs.update({pos:orf_Details})
            else:
                print("Unexpected Error Finding ORFs")
        #Now Check that we select the best ORF
        if perfect_Match == True: # Check if the ORF is a perfect match to the Gene
            genes_Covered.update({str(gene_Details):pos})
            orf_Details.append(100)
            matched_ORFs.update({pos:orf_Details})
            perfect_Matches += 1
            perfect_Starts += 1
            perfect_Stops += 1
            correct_Frame_Number += 1
            print('Perfect Match')
        elif perfect_Match == False and len(overlapping_ORFs) == 1: # If we do not have a perfect match but 1 ORF which has passed our filtering, we will calculate accordingly
            orf_Pos = list(overlapping_ORFs.keys())[0]
            o_Start = int(orf_Pos.split(',')[0])
            o_Stop = int(orf_Pos.split(',')[1])
            orf_Details = overlapping_ORFs[orf_Pos]
            genes_Covered.update({str(gene_Details):orf_Pos})
            matched_ORFs.update({orf_Pos: orf_Details})
            match_Statistics(o_Start,o_Stop,g_Start,g_Stop,gene_Set)
            print('Partial Match')
        elif perfect_Match == False and len(overlapping_ORFs) >= 1: # If we have more than 1 potential ORF match, we check to see which is the 'best' hit
            orf_Pos,orf_Details = candidate_ORF_Selection(gene_Set,overlapping_ORFs) # Return best match
            o_Start = int(orf_Pos.split(',')[0])
            o_Stop = int(orf_Pos.split(',')[1])
            matched_ORFs.update({orf_Pos:orf_Details})
            genes_Covered.update({str(gene_Details):orf_Pos})
            match_Statistics(o_Start,o_Stop,g_Start,g_Stop,gene_Set)
            print('There was more than 1 potential Match')
        elif len(out_Of_Frame_ORFs) >=1: # Keep record of ORFs which overlap a gene but in the wrong frame
            print("Out of Frame ORF")
            genes_Unmatched(g_Start, g_Stop, g_Strand)
        else:
            genes_Unmatched(g_Start, g_Stop, g_Strand) # No hit
            print("No Hit")
    for key in matched_ORFs: # Remove ORFs which are out of frame if ORF was correctly matched to another Gene
        if key in out_Of_Frame_ORFs:
            del out_Of_Frame_ORFs[key]
    print("Checked all predicted ORFs")
    min_Gene_Length = min(gene_Lengths)
    max_Gene_Length = max(gene_Lengths)
    median_Gene_Length = np.median(gene_Lengths)
    ##################################################### ORF Lengths and Precision
    start_Difference = [x for x in start_Difference if x != 0]
    stop_Difference = [x for x in stop_Difference if x != 0]
    if len(start_Difference) >= 1:
        median_Start_Difference = np.median(start_Difference)
    else:
        median_Start_Difference = 0
    if len(stop_Difference) >= 1:
        median_Stop_Difference = np.median(stop_Difference)
    else:
        median_Stop_Difference = 0

    # Get Start and Stop Codon Usage
    atg_P, gtg_P, ttg_P, att_P, ctg_P, other_Start_P,other_Starts = start_Codon_Count(orfs)
    tag_P, taa_P, tga_P, other_Stop_P,other_Stops = stop_Codon_Count(orfs)
    # Count nucleotides found from ALL ORFs
    gene_Nuc_Count = np.zeros((genome_Size), dtype=np.int)
    orf_Nuc_Count = np.zeros((genome_Size), dtype=np.int)
    matched_ORF_Nuc_Count = np.zeros((genome_Size), dtype=np.int)
    for g_Positions in genes.values():
        g_Start = int(g_Positions.split(',')[0])
        g_Stop = int(g_Positions.split(',')[1])
        gene_Nuc_Count[g_Start-1:g_Stop] = [1] # Changing all between the two positions to 1's
    for o_Positions,orf_Details in orfs.items():
        o_Start = int(o_Positions.split(',')[0])
        o_Stop = int(o_Positions.split(',')[1])
        o_Strand = orf_Details[0]
        orf_Lengths.append(o_Stop - o_Start)
        orf_Nuc_Count[o_Start-1:o_Stop] = [1] # Changing all between the two positions to 1's
        # Get ORF Strand metrics:
        if o_Strand == "+":  # Get number of Positive and Negative strand ORFs
            pos_Strand += 1
        elif o_Strand == "-":
            neg_Strand += 1
        # Stats just for Unmatched ORFs
        if o_Positions not in list(matched_ORFs.keys()):
            orf_Unmatched(o_Start, o_Stop, o_Strand, unmatched_ORFs)
    # Nucleotide Coverage calculated from ORFs matching a gene only
    for o_Positions,orf_Details in matched_ORFs.items():
        o_Start = int(o_Positions.split(',')[0])
        o_Stop = int(o_Positions.split(',')[1])
        matched_ORF_Nuc_Count[o_Start-1 :o_Stop] = [1] # Changing all between the two positions to 1's
    gene_Coverage_Genome = 100 * float(np.count_nonzero(gene_Nuc_Count)) / float(genome_Size)
    orf_Coverage_Genome = 100 * float(np.count_nonzero(orf_Nuc_Count)) / float(genome_Size)
    matched_ORF_Coverage_Genome = 100 * float(np.count_nonzero(matched_ORF_Nuc_Count)) / float(genome_Size)
    # gene and orf nucleotide union
    gene_ORF_Nuc_Union_Count = np.count_nonzero(gene_Nuc_Count & orf_Nuc_Count)
    #not gene but orf nucleotides
    not_Gene_Nuc = np.logical_not(gene_Nuc_Count) + [0 for i in range(len(gene_Nuc_Count))]
    not_Gene_Nuc_And_ORF_Count = np.count_nonzero(not_Gene_Nuc & orf_Nuc_Count)
    #not orf nucleotides but gene
    not_ORF_Nuc = np.logical_not(orf_Nuc_Count) + [0 for i in range(len(orf_Nuc_Count))]
    not_ORF_Nuc_And_Gene_Count = np.count_nonzero(not_ORF_Nuc & gene_Nuc_Count)
    #not gene or orf nucleotides
    not_Gene_Nuc_Not_ORF_Nuc_Count = np.count_nonzero(not_Gene_Nuc & not_ORF_Nuc)
    #Nucleotide 'accuracy'
    NT_TP = (float(gene_ORF_Nuc_Union_Count)  / float(np.count_nonzero(gene_Nuc_Count)))
    NT_FP = (float(not_Gene_Nuc_And_ORF_Count) / float(np.count_nonzero(gene_Nuc_Count)))
    NT_FN = (float(not_ORF_Nuc_And_Gene_Count) / float(np.count_nonzero(gene_Nuc_Count)))
    NT_TN = (float(not_Gene_Nuc_Not_ORF_Nuc_Count) / float(np.count_nonzero(gene_Nuc_Count)))
    NT_Precision = NT_TP / (NT_TP + NT_FP)
    NT_Recall = NT_TP / (NT_TP + NT_FN)
    NT_False_Discovery_Rate = NT_FP / (NT_FP + NT_TP)
    ################################# Precision and Recall of filtered ORFs
    TP = (len(genes_Covered)  / len(genes))
    FP = (len(unmatched_ORFs) / len(genes))
    FN = (len(missed_Genes)  / len(genes))
    try: # Incase no ORFs found a gene
        precision = TP/(TP+FP)
        recall = TP/(TP+FN)
        false_Discovery_Rate = FP/(FP+TP)
    except ZeroDivisionError:
        precision = 0
        recall = 0
        false_Discovery_Rate = 0
    min_ORF_Length = min(orf_Lengths)
    max_ORF_Length = max(orf_Lengths)
    median_ORF_Length = np.median(orf_Lengths)

    # Percenting Metrics
    ORFs_Diff = (float(len(orfs)) - float(len(genes))) / float(len(genes)) * 100
    genesCoveredPercentage = len(genes_Covered) / len(genes) * 100
    matched_ORF_Percentage = len(matched_ORFs) / len(orfs) * 100
    median_Length_Diff = ((float(median_ORF_Length) - median_Gene_Length) / median_Gene_Length) * 100
    min_Length_Diff = float((min_ORF_Length) - float(min_Gene_Length)) / float(min_Gene_Length) * 100
    max_Length_Diff = float((max_ORF_Length) - float(max_Gene_Length)) / float(max_Gene_Length) * 100
    pos_Strand_Percentage = (float(pos_Strand) * 100 / float(len(orfs)))
    neg_Strand_Percentage = (float(neg_Strand) * 100 / float(len(orfs)))
    #############################################
    try: # Incase no ORFs found a gene
        correct_Frame_Percentage = correct_Frame_Number * 100 / (len(genes_Covered) + len(out_Of_Frame_ORFs))
        per_Expanded_CDS = expanded_CDS * 100 / len(genes_Covered)
        per_Expanded_Start = expanded_Start * 100 / len(genes_Covered)
        per_Expanded_Stop = expanded_Stop * 100 / len(genes_Covered)
        perfect_Matches_Percentage = perfect_Matches * 100 / len(matched_ORFs)
        perfect_Starts_Percentage = float(perfect_Starts) * float(100) / float(len(matched_ORFs))
        perfect_Stops_Percentage = float(perfect_Stops) * float(100) / float(len(matched_ORFs))
    except ZeroDivisionError:
        correct_Frame_Percentage = 0
        per_Expanded_Coding_Regions = 0
        per_Expanded_Start = 0
        per_Expanded_Stop = 0
        perfect_Matches_Percentage = 0
        perfect_Starts_Percentage = 0
        perfect_Stops_Percentage = 0
    #############################################
    #Missed Genes  Metrics:
    mg_Starts = []
    mg_Stops = []
    mg_Lengths = []
    mg_Strands = []
    for mg, seq in missed_Genes.items():
        mg = mg.split(',')
        mg_Starts.append(mg[3])
        mg_Stops.append(mg[4])
        mg_Strands.append(mg[2])
        mg_Lengths.append(int(mg[1])-int(mg[0]))

    mg_ATG = mg_Starts.count('ATG') *100 / len(missed_Genes)
    mg_GTG = mg_Starts.count('GTG') *100 / len(missed_Genes)
    mg_TTG = mg_Starts.count('TTG') *100 / len(missed_Genes)
    mg_ATT = mg_Starts.count('ATT') *100 / len(missed_Genes)
    mg_CTG = mg_Starts.count('CTG') *100 / len(missed_Genes)
    mg_O_Start = 100 - (mg_ATG+mg_GTG+mg_TTG+mg_ATT+mg_CTG)
    mg_TGA = mg_Stops.count('TGA') *100 / len(missed_Genes)
    mg_TAA = mg_Stops.count('TAA') *100 / len(missed_Genes)
    mg_TAG = mg_Stops.count('TAG') *100 / len(missed_Genes)
    mg_O_Stop = 100 - (mg_TGA+mg_TAA+mg_TAG)
    median_mg_Len = np.median(mg_Lengths)
    mg_Pos = mg_Strands.count('+')
    mg_Neg = mg_Strands.count('-')
    Missed_Gene_Metrics = (format(mg_ATG,'.2f'),format(mg_GTG,'.2f'),format(mg_TTG,'.2f'),format(mg_ATT,'.2f'),format(mg_CTG,'.2f'),format(mg_O_Start,'.2f'),format(mg_TGA,'.2f'),format(mg_TAA,'.2f'),format(mg_TAG,'.2f'),format(mg_O_Stop,'.2f'),format(median_mg_Len,'.2f'),mg_Pos,mg_Neg)

    # Unmathced ORF Metrics:
    ou_Starts = []
    ou_Stops = []
    ou_Lengths = []
    ou_Strands = []
    for uo, seq in unmatched_ORFs.items():
        uo = uo.split(',')
        ou_Starts.append(uo[3])
        ou_Stops.append(uo[4])
        ou_Strands.append(uo[2])
        ou_Lengths.append(int(uo[1]) - int(uo[0]))
    ou_ATG = ou_Starts.count('ATG') * 100 / len(unmatched_ORFs)
    ou_GTG = ou_Starts.count('GTG') * 100 / len(unmatched_ORFs)
    ou_TTG = ou_Starts.count('TTG') * 100 / len(unmatched_ORFs)
    ou_ATT = ou_Starts.count('ATT') * 100 / len(unmatched_ORFs)
    ou_CTG = ou_Starts.count('CTG') * 100 / len(unmatched_ORFs)
    ou_O_Start = 100 - (ou_ATG + ou_GTG + ou_TTG + ou_ATT + ou_CTG)
    ou_TGA = ou_Stops.count('TGA') * 100 / len(unmatched_ORFs)
    ou_TAA = ou_Stops.count('TAA') * 100 / len(unmatched_ORFs)
    ou_TAG = ou_Stops.count('TAG') * 100 / len(unmatched_ORFs)
    ou_O_Stop = len(ou_Stops) -(ou_TGA+ou_TAA+ou_TAG)
    ou_O_Stop = ou_O_Stop *100 / len(unmatched_ORFs)
    median_ou_Len = np.median(ou_Lengths)
    ou_Pos = ou_Strands.count('+')
    ou_Neg = ou_Strands.count('-')
    unmatched_orf_metrics = (format(ou_ATG,'.2f'),format(ou_GTG,'.2f'),format(ou_TTG,'.2f'),format(ou_ATT,'.2f'),format(ou_CTG,'.2f'),format(ou_O_Start,'.2f'),format(ou_TGA,'.2f'),format(ou_TAA,'.2f'),format(ou_TAG,'.2f'),format(ou_O_Stop,'.2f'),format(median_ou_Len,'.2f'),ou_Pos,ou_Neg)
    #################################
    metric_description = ['Number of ORFs',	'Percentage Difference of ORFs', 'Number of ORFs Matching a Gene', 'Percentage of ORFs Matching a Gene', 'Number of Genes Correctly Identified',
                        'Percentage of Genes Correctly Identified', 'Mean Length of All ORFs', 'Mean Length Difference', 'Minimum Length of All ORFs', 'Minimum Length Difference',
                        'Maximum Length of All ORFs', 'Maximum Length Difference', 'Number of Perfect Matches', 'Percentage of Perfect Matches', 'Number of Perfect Starts',
                        'Percentage of Perfect Starts', 'Number of Perfect Stops',	'Percentage of Perfect Stops', 'Number of Matched ORFs in Correct Frame', 'Percentage of Matched ORFs in Correct Frame',
                        'Number of Matched ORFs Expanding a Coding Region', 'Percentage of Matched ORFs Expanding a Coding Region', 'Number of All ORFs on Positive Strand', 'Percentage of All ORFs on Positive Strand',
                        'Number of All ORFs on Negative Strand', 'Percentage of All ORFs on Negative Strand', 'Mean Start Difference of Matched ORFs', 'Mean Stop Difference of Matched ORFs','ATG Start Percentage',
                        'GTG Start Percentage', 'TTG Start Percentage', 'ATT Start Percentage', 'CTG Start Percentage', 'Other Start Codon Percentage', 'TAG Stop Percentage', 'TAA Stop Percentage',
                        'TGA Stop Percentage', 'Other Stop Codon Percentage', 'True Positive', 'False Positive', 'False Negative', 'Precision', 'Recall', 'False Discovery Rate',
                        'Nucelotide True Positive', 'Nucleotide False Positive', 'Nucelotide True Negative', 'Nucelotide False Negatie', 'Nucleotide Precision', 'Nucleotide Recall',
                        'Nucleotide False Discovery Rate','ORF nucleotide coverage of Genome','Matched ORF nucleotide coverage of Genome']

    metrics = [len(orfs), format(ORFs_Diff,'.2f'), len(matched_ORFs), format(matched_ORF_Percentage,'.2f'), len(genes_Covered),
              format(genesCoveredPercentage,'.2f'), format(median_ORF_Length,'.2f'), format(median_Length_Diff,'.2f'), min_ORF_Length, format(min_Length_Diff,'.2f'),
              max_ORF_Length, format(max_Length_Diff,'.2f'),perfect_Matches, format(perfect_Matches_Percentage,'.2f'),  perfect_Starts,
              format(perfect_Starts_Percentage,'.2f'), perfect_Stops, format(perfect_Stops_Percentage,'.2f'), correct_Frame_Number, format(correct_Frame_Percentage,'.2f'), expanded_Coding_Regions,
              format(per_Expanded_Coding_Regions,'.2f'), pos_Strand, format(pos_Strand_Percentage,'.2f'), neg_Strand, format(neg_Strand_Percentage,'.2f'),
              format(mean_start_difference,'.2f'), format(mean_stop_difference,'.2f'), format(atg_P, '.2f'), format(gtg_P,'.2f'), format(ttg_P, '.2f'), format(att_P, '.2f'), format(ctg_P, '.2f'), format(other_Start_P, '.2f'),
              format(tag_P, '.2f'), format(taa_P, '.2f'), format(tga_P, '.2f'), format(other_Stop_P,'.2f'), format(TP,'.2f'), format(FP,'.2f'), format(FN,'.2f'), format(precision,'.2f'), format(recall,'.2f'),
              format(false_Discovery_Rate,'.2f'), format(NT_TP,'.2f'), format(NT_FP,'.2f'), format(NT_TN,'.2f'), format(NT_FN,'.2f'), format(NT_Precision,'.2f'), format(NT_Recall,'.2f'),
              format(NT_False_Discovery_Rate,'.2f'),format(orf_Coverage_Genome,'.2f'),format(matched_ORF_Coverage_Genome,'.2f')]

    rep_metric_description = ['Percentage of ORFs Matching a Gene','Percentage Difference of ORFs','Mean Length Difference','Percentage of Perfect Matches','Percentage of Perfect Starts','Percentage of Perfect Stops',
                               'Mean Start Difference of Matched ORFs', 'Mean Stop Difference of Matched ORFs','Precision', 'Recall']

    rep_metrics = [format(matched_ORF_Percentage,'.2f'),format(ORFs_Diff,'.2f'),format(mean_Length_Diff,'.2f'),format(perfect_Matches_Percentage,'.2f'), format(perfect_Starts_Percentage,'.2f'), format(perfect_Stops_Percentage,'.2f'),
                   format(mean_start_difference,'.2f'), format(mean_stop_difference,'.2f'),format(precision,'.2f'), format(recall,'.2f')]

    return metric_description, metrics, rep_metric_description, rep_metrics, start_Difference, stop_Difference, other_Starts, other_Stops, missed_Genes, unmatched_ORFs, Missed_Gene_Metrics, unmatched_orf_metrics,gene_Coverage_Genome
