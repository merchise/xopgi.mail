#!/bin/sh

# Preamble: find current dir (assumes you execute tox inside your package)
# Get the main's addons name by replacing dots with underscores, etc...
CDIR=`pwd`
MAIN_ADDON=`pwd | xargs basename | tr . _`

# Finds the addons inside xopgi (assuming all directories are addons)
ADDONS=`find xopgi/ -maxdepth 1 -mindepth 1 -type d | xargs basename -a | \
        while read addon; do echo -n "$addon,"; done `

# Finds all packages that include doctests and run them if possible.  You may
# have doctests in modules that import OpenERP and they won't run properly
# from the `python` script.
grep ">>> " --include="*.py" -r xopgi/ -l | xargs python -m doctest || echo "!"


# The name of the DB is built from the name of the addon but it's hashed to
# avoid clashes in a shared DB env with a CI server not running in a
# container.
NOW=`date --utc +"%Y%m%d%H%M%N"`
HASH=`echo "$CWD-$NOW" | md5sum -t - | awk '{print $1}'`
DB=testingdb_"$HASH"
STDOUT=$(tempfile --prefix="$HASH-" --suffix=.log)


# Trick to test with openerp-server.
if [ -z "$1" ]; then
    EXECUTABLE=xoeuf
else
    EXECUTABLE="$1"
fi

echo ">>> $EXECUTABLE ..."

# Just in case
dropdb $DB 2>/dev/null

# Create the DB install the addons and run tests.
createdb "$DB" && \
   $EXECUTABLE -d $DB -i all --stop-after-init && \
   $EXECUTABLE -d $DB -i "$ADDONS" --stop-after-init \
      --test-enable --log-level=test | tee "$STDOUT"

if egrep -q "(At least one test failed when loading the modules.|ERROR ${DB})" "$STDOUT"; then
    CODE=1
else
    CODE=0
fi

rm -f -- "$STDOUT"
dropdb $DB

exit $CODE
