#!/bin/bash
app=$@
y="${app//[[:space:]]/}"
x=$(sed -e 's/^"//' -e 's/"$//' <<<"$y" )
app_url=$(echo $x | base64 -d | awk '{ print $3 }' - | sed -n '2p')
status=$(curl -o /dev/null -s -w "%{http_code}\n" ${app_url})
if [[ $status == 200 ]]; then
    echo "status code is $status"
    echo """
<?xml version="1.0" encoding="UTF-8" ?>
<testsuite errors="0" failures="0" hostname="jenkin--vm" name="petstore application functional test" skipped="0" tests="1" time="0.1">
<testcase classname="petstore web application" name="start" time="0.1" />
</testsuite>""">test.xml
else
   echo """
<?xml version="1.0" encoding="UTF-8" ?>
<testsuite errors="0" failures="1" hostname="jenkin--vm" name="petstore application functional test" skipped="0" tests="1" time="0.1">
<testcase classname="petstore web application" name="start" time="0.1" />
</testsuite>""">test.xml
fi
