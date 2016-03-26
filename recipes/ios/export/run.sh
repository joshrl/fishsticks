# #!/bin/bash
#
# function die
# {
#     echo "$1" 1>&2
#     exit 1
# }
#
# # Check status of previous piped command
# function checkstatus_of_pipe
# {
#     if [ ${PIPESTATUS[$1]} -ne 0 ]
#     then
#         echo "$2" 1>&2
#         exit ${PIPESTATUS[0]}
#     fi
# }
#
# if [ -z "$1" ] || [ -z "$2" ]
#   then
#     die "Usage: $0 [project-path] [artifact-path]"
# fi
#
# pushd `dirname $0` > /dev/null
# script_path=`pwd -P`
# popd > /dev/null
#
# project_path=$1
# artifact_path=$2
#
# mkdir -p "$artifact_path" > /dev/null 2>&1
#
# pushd "${project_path}" > /dev/null 2>&1
#
# workspaces=(*.xcworkspace)
# if [ ${#workspaces[@]} -eq 0 ]
#   then
#     die "Project must have a workspace at the top level."
# fi
#
# if [ ${#workspaces[@]} -gt 1 ]
#   then
#     die "Project must have only one workspace at the top level."
# fi
#
# popd > /dev/null 2>&1
#
#
# workspace=${workspaces[0]}
# projest_name=${workspace%.*}
# scheme=${projest_name}
# workspace_path="${project_path}/${workspace}"
# sources_path="${project_path}/${projest_name}"
# archive_path="${artifact_path}/${projest_name}"
# archive_package_path="${archive_path}.xcarchive"
# test_output_path="${artifact_path}/test-output.txt"
# archive_output_path="${artifact_path}/archive-output.txt"
# export_output_path="${artifact_path}/export-output.txt"
# test_report_path="${artifact_path}/test-report.html"
#
# echo "Settings:"
# echo "  workspace: $workspace"
# echo "  project name: $projest_name"
# echo "  scheme: $scheme"
# echo "  sources path: $sources_path"
# echo "  archive path: $archive_path"
# echo "  ipa path: $ipa_path"
# echo "  script path: $script_path"
# echo "  test output path: $test_output_path"
# echo "  achive output path: $archive_output_path"
# echo "  export output path: $export_output_path"
# echo "  test report path: $test_report_path"
#
# #Set Version
# pushd "${sources_path}" > /dev/null 2>&1
# build_number=`git rev-list HEAD --count`
# agvtool new-version "${build_number}"
# popd > /dev/null 2>&1
#
# # Test
# xcodebuild test \
#     -workspace "${workspace_path}" \
#     -scheme "${scheme}" \
#     -destination 'platform=iOS Simulator,name=iPhone 6s,OS=9.2' \
#     | tee "$test_output_path"
#
# checkstatus_of_pipe 0 "Tests Failed"
#
#
# # If xcpretty is installed, generate report
# if hash xcpretty 2>/dev/null; then
#    cat "$test_output_path" | xcpretty -r html --output ${test_report_path}
# else
#     echo "Test Report Unavailable." > ${test_report_path}
# fi
#
# # Archive
# xcodebuild archive \
#     -workspace "${workspace_path}" \
#     -archivePath "${archive_package_path}" \
#     -scheme "${scheme}" \
#     | tee "$archive_output_path"
#
# checkstatus_of_pipe 0 "Archive Failed"
#
# # Export
# xcodebuild -exportArchive \
#     -archivePath "${archive_package_path}" \
#     -exportOptionsPlist "${script_path}/export.plist" \
#     -exportPath "${artifact_path}" \
#     | tee "$export_output_path"
#
# checkstatus_of_pipe 0 "Export Failed"
#
# # Rename ipa
# mv "${artifact_path}/${projest_name}.ipa" "${artifact_path}/${projest_name}-Inhouse.ipa" > /dev/null 2>&1
#
# #Reset version to 0
# pushd "${sources_path}" > /dev/null 2>&1
# agvtool new-version 0 > /dev/null 2>&1
# popd > /dev/null 2>&1
#
#
#
#
