#!/bin/bash
app=$@
y="${app//[[:space:]]/}"
x=$(sed -e 's/^"//' -e 's/"$//' <<<"$y" )
app_url=$(echo $x | base64 -d | awk '{ print $3 }' - | sed -n '2p')
status=$(curl -o /dev/null -s -w "%{http_code}\n" ${app_url})
if [[ $status == 200 ]]; then
    echo "status code is $status"
    echo $PWD
    cat > test.xml <<- EOM
<testsuites>
  <testsuite tests="1" failures="0" time="0.100" name="package/name">
        <properties>
            <property name="go.version" value="1.0"></property>
        </properties>
        <testcase classname="PetstoreWebApplication" name="TestOne" time="0.100"></testcase>
  </testsuite>
</testsuites>
EOM
else
   cat > test.xml <<- EOM
<testsuites>
  <testsuite tests="1" failures="1" time="0.100" name="package/name">
        <properties>
            <property name="go.version" value="1.0"></property>
        </properties>
        <testcase classname="PetstoreWebApplication" name="TestOne" time="0.100"></testcase>
  </testsuite>
</testsuites>
EOM
fi
