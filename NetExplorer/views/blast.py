from common import *

def blast(request):
    """
    View for the BLAST form page
    """
    if request.POST:
        if not request.POST['database']:
            return render(request, 'NetExplorer/blast.html', {"error_msg": "No Database selected", 'databases': get_databases(request)})
        if "type" not in  request.POST or not request.POST['type']:
            return render(request, 'NetExplorer/blast.html', {"error_msg": "No valid BLAST application selected",'databases': get_databases(request)})

        fasta = str()
        database = request.POST['database'].lower()
        results = list()
        if request.FILES:
            logging.info("There is a file")
            # Must check if FASTA
            fasta = request.FILES['fastafile'].read()
        else:
            logging.info("No-file")
            # Must check if FASTA/plain or otherwise not valid
            fasta = request.POST['fasta_plain']

        if not fasta:
            return render(request, 'NetExplorer/blast.html', {"error_msg": "No query", 'databases': get_databases(request)})

        # Check length of sequence/number of sequences
        joined_sequences = list()
        numseq           = 0
        for line in fasta.split("\n"):
            if not line:
                continue
            if line[0] == ">":
                numseq += 1
                continue
            joined_sequences.append(line.strip())
        joined_sequences = "".join(joined_sequences)

        if numseq > MAX_NUMSEQ:
            return render(request, 'NetExplorer/blast.html', {"error_msg": "Too many query sequences (> 50)", 'databases': get_databases(request)})
        elif len(joined_sequences) >  MAX_CHAR_LENGTH:
            return render(request, 'NetExplorer/blast.html', {"error_msg": "Query sequence too long (> 25,000 characters)", 'databases': get_databases(request)})

        # Create temp file with the sequences
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(fasta)
            temp.flush()
            # Run BLAST
            pipe = Popen([request.POST['type'], "-evalue", "1e-10", "-db", BLAST_DB_DIR + database , "-query", temp.name, '-outfmt', '6'], stdout=PIPE, stderr=STDOUT)
            stdout, stderr = pipe.communicate()
            results = [ line.split("\t") for line in stdout.split("\n") if line ]
        if results:
            return render(request, 'NetExplorer/blast.html', {'results': results, 'database': database.title(), 'databases': get_databases(request) })
        else:
            return render(request, 'NetExplorer/blast.html', {'results': results, 'noresults': True, 'database': database.title(), 'databases': get_databases(request) })
    else:
        return render(request, 'NetExplorer/blast.html',{'databases': get_databases(request)})
