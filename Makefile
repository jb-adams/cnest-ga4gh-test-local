POPULATE_SQL_FILE := sql/populate-drs-dataset.sql
DB := db/cnest-ga4gh-test.db
DOCKER_IMG_DRS=ga4gh/ga4gh-starter-kit-drs:0.1.6
DOCKER_NAME_DRS=cnest-ga4gh-test-drs

Nothing:
	@echo "No target provided. Stop"

.PHONY: setup-db
setup-db:
	@python scripts/generate_populate_commands.py /Users/jadams/Test/21/210519-cnest-attempts/data/downsample .downsample .bam application/bam .bam.bai application/bai /Users/jadams/Test/21/210519-cnest-attempts/data/md5.downsample
	@sqlite3 ${DB} < sql/create-drs-tables.sql
	@sqlite3 ${DB} < sql/create-wes-tables.sql
	@sqlite3 ${DB} < ${POPULATE_SQL_FILE}

.PHONY: run-drs
run-drs:
	@docker image pull ${DOCKER_IMG_DRS}
	@docker run -d --rm --name ${DOCKER_NAME_DRS} -v `pwd`/db:/db -v `pwd`/config/drs:/config -p 5050:5050 -p 5060:5060 ${DOCKER_IMG_DRS} java -jar ga4gh-starter-kit-drs.jar -c /config/config.yml

.PHONY: run-wes
run-wes:
	@echo "Run WES here"

.PHONY: clean
clean:
	@rm -f ${POPULATE_SQL_FILE}
	@rm -f ${DB}
	@docker stop ${DOCKER_NAME_DRS}

.PHONY: build-run
build-run: setup-db run-drs run-wes

.PHONY: clean-build-run
clean-build-run: clean build-run