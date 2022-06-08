#!/bin/bash -e

dir_parent=$(cd $(dirname $0); pwd)
f_name="${0}"
f_basename=$(basename "${0}")

ker_version=""
no_check_ker_ver=false
reverse_build_order=false
exact_ver1=""
opt_exact_ver1=""
exact_ver2=""
opt_exact_ver2=""
qareport_project=""
opt_qareport_project=""


function printUsage(){
    # e.g.
    # ./kernelreport.sh 5.10
    # ./kernelreport.sh 5.10 --exact-version-1 5.10.40 --no-check-kernel-version

    echo "Please run like this:"
    echo -e "\t${f_name} kernel_ver [--exact-version-1 exact_ver1 [--exact-version-2 exact_ver2 [--reverse-build-order]]] [--no-check-kernel-version] [--qareport-project qareport-project]"
}

function parseArgs(){
    while [ -n "${1}" ]; do
        case "X$1" in
            X--no-check-kernel-version)
                no_check_ker_ver=true
                shift
                ;;
            X--reverse-build-order)
                reverse_build_order=true
                shift
                ;;
            X--exact-version-1)
                if [ -z "${2}" ]; then
                    echo "Please specify value for the --exact-version-1 option"
                    exit 1
                fi
                exact_ver1=$(echo "${2}"|sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
                opt_exact_ver1="--exact-version-1 ${exact_ver1}"
                shift 2
                ;;
            X--exact-version-2)
                if [ -z "${2}" ]; then
                    echo "Please specify value for the --exact-version-2 option"
                    exit 1
                fi
                exact_ver2=$(echo "${2}"|sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
                opt_exact_ver2="--exact-version-2 ${exact_ver2}"
                shift 2
                ;;
            X--qareport-project)
                if [ -z "${2}" ]; then
                    echo "Please specify value for the --qareport-project option"
                    exit 1
                fi
                qareport_project="$2"
                opt_qareport_project="--qareport-project ${qareport_project}"
                shift 2
                ;;
            X-h|X--help)
                printUsage
                exit 1
                ;;
            X*)
                if [ -n "${ker_version}" ]; then
                    echo "kernel_ver could be only spedified once"
                    printUsage
                    exit 1
                fi
                ker_version=$(echo "${1}"|sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
                shift
                ;;

        esac
    done
}


parseArgs "$@"
if [ -z "${ker_version}" ]; then
    printUsage
    exit 1
fi

if ${no_check_ker_ver}; then
    opt_no_check_ker_ver="--no-check-kernel-version"
fi

if ${reverse_build_order}; then
    opt_reverse_build_order="--reverse-build-order"
fi

if [ -z "${exact_ver1}" ]; then
    f_report="/tmp/kernelreport-${ker_version}"
elif [ -z "${exact_ver2}" ]; then
    f_report="/tmp/kernelreport-${ker_version}-${exact_ver1}"
elif ${reverse_build_order}; then
    f_report="/tmp/kernelreport-${ker_version}-${exact_ver2}-${exact_ver1}"
else
    f_report="/tmp/kernelreport-${ker_version}-${exact_ver1}-${exact_ver2}"
fi
if [ -n "${qareport_project}" ]; then
    f_report="${f_report}-${qareport_project}"
fi
f_report="${f_report}.txt"
rm -f "${f_report}.scribble"
rm -f "${f_report}.errorprojects"
rm -f "${f_report}.successprojects"

PYTHON="$(command -v python3)"
if [ -e "${dir_parent}/../workspace-python3/bin/python" ]; then
    PYTHON="${dir_parent}/../workspace-python3/bin/python"
fi

wget -c https://raw.githubusercontent.com/tom-gall/android-qa-classifier-data/master/flakey.txt -O /tmp/flakey.txt
"${PYTHON}" ${dir_parent}/manage.py kernelreport \
        ${opt_no_check_ker_ver} \
        "${ker_version}" \
        ${f_report} \
        /tmp/flakey.txt \
        ${opt_exact_ver1} \
        ${opt_exact_ver2} \
        ${opt_reverse_build_order} \
        ${opt_qareport_project}

if [ -f "${f_report}.scribble" ]; then
    mv -f "${f_report}" "${f_report}.successprojects"
    cat "${f_report}.errorprojects" >> "${f_report}"
    cat "${f_report}.successprojects" >> "${f_report}"
    cat "${f_report}.scribble" >> "${f_report}"
    echo "############ Reports End #########################"
    echo "## Command to reproduce this report ##############"
    echo "##   ./${f_basename} $@"
    echo "##################################################"
    echo "Please check the file of ${f_report} for report"
    rm -f "${f_report}.scribble" "${f_report}.errorprojects" "${f_report}.successprojects"
else
    echo "Failed to generate the test report, Please check and try again"
fi
