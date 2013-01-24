# grab candidate files. Not sure about '78.
datadir=./data

for year in '80' '82' '84' '86' '88' '90' '92' '94' '96' '98' 
do
    echo "Getting files for: $year"
    
    mkdir -p $datadir/$year/
    # Master candidates file -- includes *all* candidates
    curl -o $datadir/$year/cn$year.zip ftp://ftp.fec.gov/FEC/19$year/cn$year.zip 
    # Y2K:
    # curl -o $datadir/$year/cn$year.zip ftp://ftp.fec.gov/FEC/20$year/cn$year.zip 
    unzip -o $datadir/$year/cn$year.zip -d $datadir/$year

    sleep 1 

done

for year in '00' '02' '04' '06' '08' '10' '12' 
do
    echo "Getting files for: $year"
    
    mkdir -p $datadir/$year/
    curl -o $datadir/$year/cn$year.zip ftp://ftp.fec.gov/FEC/20$year/cn$year.zip 
    unzip -o $datadir/$year/cn$year.zip -d $datadir/$year

    sleep 1 

done