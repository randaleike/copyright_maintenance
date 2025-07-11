#!/bin/bash

# Update doxygen html
doxygen Doxyfile

# Get list of files
echo "Build WIKI"
for file in doc/html/*.html; do
    inputname=$(basename "$file")
    mdname="$(basename -- "$file" .html).md"

    if [[ $mdname == *"classcopyright__maintenance__grocsoftware_1_1"* ]]; then
        p1name=${mdname/classcopyright__maintenance__grocsoftware_1_1/}

        if [[ $p1name == *"comment__block_1_1"* ]]; then
            outputname=${p1name/comment__block_1_1/}
        elif [[ $p1name == *"copyright__finder_1_1"* ]]; then
            outputname=${p1name/copyright__finder_1_1/}
        elif [[ $p1name == *"copyright__generator_1_1"* ]]; then
            outputname=${p1name/copyright__generator_1_1/}
        elif [[ $p1name == *"copyright__tools_1_1"* ]]; then
            outputname=${p1name/copyright__tools_1_1/}
        elif [[ $p1name == *"file__dates_1_1"* ]]; then
            outputname=${p1name/file__dates_1_1/}
        elif [[ $p1name == *"oscmdshell_1_1"* ]]; then
            outputname=${p1name/oscmdshell_1_1/}
        elif [[ $p1name == *"update__copyright_1_1"* ]]; then
            outputname=${p1name/update__copyright_1_1/}
        else
            outputname=$p1name
        fi
    else
        outputname=$mdname
    fi

    #echo "in:$inputname, out:$outputname"
    if [ $outputname != 'index.md' ]; then
        pandoc -s --to=markdown_strict -o $1/$outputname $file
        sed -i 's/.html//g' $1/$outputname
        sed -i 's/classcopyright__maintenance__grocsoftware_1_1//g' $1/$outputname
        sed -i 's/comment__block_1_1//g' $1/$outputname
        sed -i 's/copyright__finder_1_1//g' $1/$outputname
        sed -i 's/copyright__generator_1_1//g' $1/$outputname
        sed -i 's/file__dates_1_1//g' $1/$outputname
        sed -i 's/oscmdshell_1_1//g' $1/$outputname
        sed -i 's/update__copyright_1_1//g' $1/$outputname
        sed -i 's/^No Matches.*$//g' $1/$outputname
        sed -i 's/^Loading\.\.\..*$//g' $1/$outputname
        sed -i 's/^Searching\.\.\..*$//g' $1/$outputname
    fi

done