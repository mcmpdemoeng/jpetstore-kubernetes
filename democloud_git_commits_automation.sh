git clone https://github.com/mcmpdemoeng/sonarqube-sample-projects
cd sonarqube-sample-projects
commit_date=$(date +'%m/%d/%Y %T')
echo "# Sonarqube sample projects. Automatic commit date: ${commit_date}" > daily-commits.md
cat daily-commits.md
git add .
git commit -m "Automatic commit for DI data on: ${commit_date}"
git push https://${AUTOMATIC_COMIT_GIT_TOKEN}@github.com/mcmpdemoeng/sonarqube-sample-projects.git