POPULATE_SQL_FILE := sql/populate-drs-dataset.sql
DEVDB := db/cnest-ga4gh-test.db

Nothing:
	@echo "No target provided. Stop"

.PHONY: setup-db
setup-db:
	@python scripts/generate_populate_commands.py /Volumes/ftp-private.ebi.ac.uk/upload/cnest_tests/downsample .downsample .bam application/bam .bam.bai application/bai /Volumes/ftp-private.ebi.ac.uk/upload/cnest_tests/md5.downsample
	@sqlite3 ga4gh-starter-kit.dev.db < sql/create-drs-tables.sql
	@sqlite3 ga4gh-starter-kit.dev.db < sql/create-wes-tables.sql
	@sqlite3 ga4gh-starter-kit.dev.db < ${POPULATE_SQL_FILE}

.PHONY: clean
clean:
	@rm -f ${POPULATE_SQL_FILE}
	@rm -f ${DEVDB}