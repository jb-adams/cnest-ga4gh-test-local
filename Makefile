POPULATE_SQL_FILE := sql/populate-drs-dataset.sql
DB := db/cnest-ga4gh-test.db

Nothing:
	@echo "No target provided. Stop"

.PHONY: setup-db
setup-db:
	@python scripts/generate_populate_commands.py /Volumes/ftp-private.ebi.ac.uk/upload/cnest_tests/downsample .downsample .bam application/bam .bam.bai application/bai /Volumes/ftp-private.ebi.ac.uk/upload/cnest_tests/md5.downsample
	@sqlite3 ${DB} < sql/create-drs-tables.sql
	@sqlite3 ${DB} < sql/create-wes-tables.sql
	@sqlite3 ${DB} < ${POPULATE_SQL_FILE}

.PHONY: clean
clean:
	@rm -f ${POPULATE_SQL_FILE}
	@rm -f ${DB}