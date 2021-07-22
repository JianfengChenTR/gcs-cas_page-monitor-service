#!/bin/bash
version=$1


for f in $2*.yaml; do
    if [[ $f == $2versioned-* ]]
    then
        mv "$f" "${f%.yaml}-v$version.yaml"


        template_name=${f%.*}
        template_name=${template_name##*/}
        updated_version="-v"$version


        sed -i -e "s@Version:\s*[0-9]*@Version: \"$version\"@" $template_name$updated_version.yaml


        for file_to_update in $2*.yaml; do
          echo $2$template_name$updated_version.yaml
          if [ $file_to_update != $2$template_name$updated_version.yaml ]
          then
            sed -i -e "s@$template_name@$template_name$updated_version@" $file_to_update
          fi
        done
    fi
done
