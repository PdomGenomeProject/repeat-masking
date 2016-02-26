# Repeat masking

This data set is part of the [*Polistes dominula* genome project][pdomproj], and provides details regarding the annotation and masking of transposable elements and other repetitive sequences in the *P. dominula* genome, as described in ([Standage *et al.*, *Molecular Ecology*, 2016][ref]).
Included in this data set are the repeat annotations, the masked genome sequence, and documentation providing complete disclosure of the masking procedure.

## Synopsis

The genome assembly was screened for known repetitive elements using [RepeatMasker][] version [open-4.0.5][] and [Repbase][] version 20140131.
After masking repeats identified by RepeatMasker, the assembly was screened for additional repeats using [Tallymer] version [1.5.2].
To discriminate _bona fide_ repetitive elements from genes occurring in high copy number in the genome, all repeats identified by Tallymer were subjected to a BLASTX search against a database of Hexapod proteins.
Any repeats with matches in the database and e-values < 1e-5 were discarded as probable high copy number genes, while the rest were used to mask the genome.

## Data access

The unmasked *P. dominula* reference genome assembly is available for download at the DOI [10.6084/m9.figshare.1593098][genomedoi].

## Procedure

First, we identified known repeats with RepeatMasker.
By default, RepeatMasker produces soft-masked (lower-case) sequences, so we need to post-process the output to hard mask (N) the sequence.

```bash
NumProcs=16
GCContent=30.77
RepeatMasker -species insects -parallel $NumProcs -gc $GCContent \
             -frag 4000000 -lcambig -xsmall -gff \
             pdom-scaffolds-unmasked-r1.2.fa \
             > rm.log 2>&1
python lc2n.py < pdom-scaffolds-unmasked-r1.2.fa.masked \
               > pdom-rm-masked.fa
```

Next, we performed additional *k*-mer based screening for repetitive elements using Tallymer (procedure published by [Dan Bolser][]).

```bash
gt suffixerator -v \
                -db $IDX \
                -indexname $IDX \
                -tis -suf -lcp -des -ssp -sds -dna \
                > suffixerator.log 2>&1

gt tallymer occratio -v \
                     -minmersize 10 \
                     -maxmersize 45 \
                     -output unique nonunique nonuniquemulti total relative \
                     -esa $IDX \
                     > pdom.occratio.10.45.dump

gt tallymer mkindex -v \
            -mersize 19 \
            -minocc 50 \
            -esa $IDX \
            -counts -pl \
            -indexname pdom.idx.19.50 \
            > mkindex.log 2>&1

gt tallymer search -v \
            -output qseqnum qpos counts \
            -tyr pdom.idx.19.50 \
            -q $IDX \
            > pdom.repeats.19.50.tmer \
            2> tallymer.search.log

tallymer2gff3.plx -k 19 -s $IDX \
                  pdom.repeats.19.50.tmer \
                  > pdom.repeats.19.50.gff3

gff2fasta.plx -s pdom-rm-masked.fa \
              -f pdom.repeats.19.50.gff3 \
              > pdom.repeats.19.50.fa
```

We then did a BLASTx search of repeats found by Tallymer vs known hexapod proteins, and parsed out those with hits using [MuSeqBox][].

```bash
curl 'http://www.uniprot.org/uniprot/?query=taxonomy%3a6960&force=yes&format=fasta' \
     > hexapoda.fa
makeblastdb -in hexapoda.fa -dbtype prot -parse_seqids
blastx -query pdom.repeats.19.50.fa -db hexapoda.fa \
       -num_alignments 10 -evalue 1e-5 -num_threads 64 \
       -out pdom.repeats.19.50.blastx \
       > pdom.repeats.19.50.log 2>&1

MuSeqBox -i pdom.repeats.19.50.blastx -L 100 \
    | cut -f 1 -d ' ' | sort | uniq \
    | perl -ne 'm/(PdomSCFr1.2-\d+)-\d+\/(\d+)-(\d+)/ and print "$1\t$2\t$3\n"' \
    > pdom.repeats.19.50.hexapodhits.txt
```

Finally, we masked the Tallymer repeats, excluding any that match Hexapod proteins as probably high-copy-number genes.

```bash
mask.pl pdom.repeats.19.50.gff3 \
        pdom.repeats.19.50.hexapodhits.txt \
        pdom-rm-masked.fa \
        > pdom-scaffolds-masked-r1.2.fa
```

------

[![Creative Commons License](https://i.creativecommons.org/l/by/4.0/88x31.png)][ccby4]  
This work is licensed under a [Creative Commons Attribution 4.0 International License][ccby4].

[pdomproj]: https://github.com/PdomGenomeProject
[ref]: http://dx.doi.org/10.1111/mec.13578
[RepeatMasker]: http://www.repeatmasker.org/
[open-4.0.5]: http://www.repeatmasker.org/RepeatMasker-open-4-0-5.tar.gz
[Repbase]: http://www.girinst.org/server/RepBase/index.php
[Tallymer]: http://www.zbh.uni-hamburg.de/?id=211
[1.5.2]: http://genometools.org/pub/genometools-1.5.2.tar.gz
[genomedoi]: http://dx.doi.org/10.6084/m9.figshare.1593098
[Dan Bolser]: https://github.com/dbolser/PGSC/tree/master/kmer-filter
[MuSeqBox]: http://brendelgroup.org/bioinformatics2go/MuSeqBox.php
[ccby4]: http://creativecommons.org/licenses/by/4.0/
