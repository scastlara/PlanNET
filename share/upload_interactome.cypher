# UPLOADING CONTIGS
USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM "file:///transcriptome.csv" AS row
MERGE (n:Smest {symbol: row.symbol, sequence: row.sequence, orf: row.orf, length: row.length})

# UPLOAD HOMOLOGIES
USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM "file:///homology.csv" AS row
MATCH (n:Smest {symbol:row.symbol})
MERGE (m:Human {symbol: row.human})
MERGE (n)-[r:HOMOLOG_OF {
	blast_eval: row.blast_eval,
    blast_cov:  row.blast_cov,
    blast_brh:  row.blast_brh,
    nog_eval:   row.nog_eval,
    nog_brh:    row.nog_brh,
    pfam_sc:    row.pfam_sc,
    pfam_brh:   row.pfam_brh
}]->(m)

# UPLOAD INTERACTIONS
USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM "file:///interactions.csv" AS row
MATCH (n:Smest {symbol:row.symbol1})
MATCH (m:Smest {symbol: row.symbol2})
CREATE (n)-[r:INTERACT_WITH {
	path_length: row.path_length,
    dom_int_sc:  row.dom_int_sc,
    molfun_nto:  row.molfun_nto,
    cellcom_nto:   row.cellcom_nto,
    bioproc_nto: row.bioproc_nto,
    int_prob:    row.int_prob
}]->(m)


# UPLOADING DOMAINS
USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM "file:///domains.csv" AS row
MERGE (p:Pfam {accession: row.accession, description: row.description, identifier: row.identifier, mlength: row.length})

# UPLOADING SEQUENCE->DOMAINS
USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM "file:///sequence_domains.csv" AS row
MATCH (n:Smest {symbol: row.symbol})
WITH n, row
MATCH (m:Pfam { accession: row.accession })
MERGE (n)-[r:HAS_DOMAIN {pfam_start: row.pfam_start, pfam_end: row.pfam_end, s_start: row.s_start, s_end: row.s_end, perc: row.perc }]->(m)

# UPLOAD CONTIG<-GENE
# USING PERIODIC COMMIT 10000
LOAD CSV FROM "file:///smest-x-smesg.tsv" AS row
FIELDTERMINATOR '\t'
MATCH (n:Smest {symbol: row[0]})
MATCH (m:Smesgene {symbol: row[1]})
CREATE (m)-[r:HAS_TRANSCRIPT]->(n)
