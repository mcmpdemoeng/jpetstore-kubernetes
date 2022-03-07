echo install dependencies

wget -q https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.6.2.2472-linux.zip
unzip -qq -o sonar-scanner-cli-4.6.2.2472-linux.zip
rm sonar-scanner-cli-4.6.2.2472-linux.zip

wget -q https://dlcdn.apache.org/maven/maven-3/3.8.4/binaries/apache-maven-3.8.4-bin.tar.gz
tar -xzf apache-maven-3.8.4-bin.tar.gz
rm apache-maven-3.8.4-bin.tar.gz
./apache-maven-3.8.4/bin/mvn --version

echo run scans

SONAR_HOST=$(echo $DEMOCLOUD_SONARQUBE_HOST | base64 -d)

cd angular
../sonar-scanner-4.6.2.2472-linux/bin/sonar-scanner -Dsonar.projectKey=angular-ui -Dsonar.sources=. -Dsonar.host.url=${SONAR_HOST} -Dsonar.login=${SONARQUBE_DEMOCLOUD_TOKEN}

cd ..

cd external-issues
../sonar-scanner-4.6.2.2472-linux/bin/sonar-scanner -Dsonar.projectKey=go -Dsonar.sources=. -Dsonar.host.url=${SONAR_HOST} -Dsonar.login=${SONARQUBE_DEMOCLOUD_TOKEN}

cd ..

cd security
../apache-maven-3.8.4/bin/mvn clean verify sonar:sonar -Dsonar.projectKey=Democloud---Java-Sample-Project -Dsonar.host.url=${SONAR_HOST} -Dsonar.login=${SONARQUBE_DEMOCLOUD_TOKEN}
