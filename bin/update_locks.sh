workdir=`pwd`
docker_dir=$workdir/docker

echo "workdir:" $workdir

for project_dir in ./src/*/
do
    # remove the trailing "/"
    project=${project_dir#./src/}
    project=${project%/}

    pyproject=./src/$project/pyproject.toml

    if [ ! -f $pyproject ]; then
        echo "skip" $project " — no pyproject.toml found: " $pyproject
        continue
    fi

    echo "process" $project

    cd $project_dir && poetry lock

    cd $workdir

done
