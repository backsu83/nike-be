download_deps () {
    curl --header "PRIVATE-TOKEN: $API_ACCESS_TOKEN" "http://34.110.253.167/api/v4/projects/$1/pipelines?status=success" > pipeline.json
    cat pipeline.json
    PIPELINE_ID=$(cat pipeline.json | jq '.[0].id')
    curl --header "PRIVATE-TOKEN: $API_ACCESS_TOKEN" "http://34.110.253.167/api/v4/projects/$1/pipelines/$PIPELINE_ID/jobs" > jobs.json
    cat jobs.json
    JOB_ID=$(cat jobs.json | jq '.[] | select(.name == "'$2'").id')
    curl -L --header "PRIVATE-TOKEN: $API_ACCESS_TOKEN" "http://34.110.253.167/api/v4/projects/$1/jobs/$JOB_ID/artifacts" > artifacts.zip
    unzip artifacts.zip
}
set -e
download_deps 5 build
