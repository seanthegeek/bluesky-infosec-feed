#!/usr/bin/env bash

sort -o lists/keywords.txt lists/keywords.txt
sort -o lists/keywords_case_sensitive.txt lists/keywords_case_sensitive.txt
sort -o lists/keywords_vendors.txt lists/keywords_vendors.txt
csvsort lists/users.csv
csvsort lists/ignore_users.csv
csvsort lists/ignore_keywords.csv
