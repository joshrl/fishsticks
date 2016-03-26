#!/bin/bash

function die
{
	echo "$1" 1>&2
	exit 1
}

if [ -z "$1" ] || [ -z "$2" ]
  then
    die "Usage: $0 [project-path] [artifact-path]"
fi

project_path=$1
artifact_path=$2

mkdir -p "$artifact_path" > /dev/null 2>&1

pushd "${project_path}" > /dev/null 2>&1

workspaces=(*.xcworkspace)
if [ ${#workspaces[@]} -eq 0 ]
  then
    die "Project must have a workspace at the top level."
fi

if [ ${#workspaces[@]} -gt 1 ]
  then
    die "Project must have only one workspace at the top level."
fi

popd > /dev/null 2>&1

workspace=${workspaces[0]}
projest_name=${workspace%.*}
scheme=${projest_name}
workspace_path="${project_path}/${workspace}"
test_output_path="${artifact_path}/test_output.txt"
test_report_path="${artifact_path}/test_report.json"

echo "Settings:"
echo "  workspace: $workspace"
echo "  project name: $projest_name"
echo "  scheme: $scheme"
echo "  test output path: $test_output_path"
echo "  test report path: $test_report_path"

# Test
xcodebuild test \
    -workspace "${workspace_path}" \
    -scheme "${scheme}" \
    -destination 'platform=iOS Simulator,name=iPhone 6s,OS=9.2' \
    | tee "$test_output_path"

result=${PIPESTATUS[$1]}

# If xcpretty is installed, generate report
if hash xcpretty 2>/dev/null; then
   cat "$test_output_path" | xcpretty -r json-compilation-database --output ${test_report_path}
else
    echo "Test Report Unavailable." > ${test_report_path}
fi

exit result
