issue_date=$(date +'%m/%d/%Y %T')
mkdir issues
cd issues
git clone https://github.com/mcmpdemoeng/sonarqube-sample-projects
cd sonarqube-sample-projects
wget -q https://github.com/cli/cli/releases/download/v2.5.2/gh_2.5.2_linux_386.tar.gz
tar -xf gh_2.5.2_linux_386.tar.gz
echo ${AUTOMATIC_COMIT_GIT_TOKEN} > temp_token.txt
./gh_2.5.2_linux_386/bin/gh auth login -h GitHub.com --with-token < temp_token.txt
./gh_2.5.2_linux_386/bin/gh issue create --title "Automatic issue created at ${issue_date}" --body "This is a mock issue" --label "bug"