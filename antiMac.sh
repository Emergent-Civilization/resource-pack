find ./ | grep "__MACOSX" | xargs -I {} rm -rf "{}"
find ./ | grep ".DS_Store" | xargs -I {} rm -rf "{}"