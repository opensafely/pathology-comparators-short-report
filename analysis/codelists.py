from cohortextractor import codelist_from_csv

path_tests = codelist_from_csv(
    'codelists/user-helen-curtis-tests-with-comparators.csv',
    column='code',
    system='snomed')
