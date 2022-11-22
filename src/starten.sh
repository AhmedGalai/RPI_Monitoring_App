#!/env/bin/bash
$srcPath="~/Desktop/RPI_beobachtungsapp/src"
source "$srcPath/../env/bin/activate"
cd $srcPath
flask run --host=0.0.0.0