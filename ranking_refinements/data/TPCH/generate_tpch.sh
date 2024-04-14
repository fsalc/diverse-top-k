this_dir=`pwd`

mkdir SCALE-$1
cd SCALE-$1

echo "Working directory $(pwd)"

cp ../dbgen .
cp ../dists.dss .

touch customer.tbl lineitem.tbl orders.tbl partsupp.tbl part.tbl supplier.tbl region.tbl nation.tbl

echo "Generating TPC-H with Scale $1"
for i in {1..10}
do
  echo "Generating chunk number $i..."
  ./dbgen -s $1 -C 10 -S $i -f
  mkdir "$i"
  for file in customer.tbl lineitem.tbl orders.tbl partsupp.tbl part.tbl supplier.tbl region.tbl nation.tbl
  do
    echo "Appending $file with $file.$i..."
    cat "$file.$i" >> $file

    echo "Deleting file $file.$i..."
    rm -f $file.$i

    echo "Copy chunks 1...$i of $file to directory $i"
    cp $file $i
  done
done

echo "All tables were generated!"

for j in {1..10}
do
  echo "Taking care of chunks 1...$j in directory $j"
  cd $j
  echo "Creating .csv files from .tbl files"
  for i in `ls *.tbl`; do sed 's/|$//' $i > ${i/tbl/csv}; echo $i; done;
  rm -rf *.tbl

  echo "Adding headers to tables"
  sed -i '1iNATIONKEY|NAME|REGIONKEY|COMMENT' nation.csv
  sed -i '1iCUSTKEY|NAME|ADDRESS|NATIONKEY|PHONE|ACCTBAL|MKTSEGMENT|COMMENT' customer.csv
  sed -i '1iORDERKEY|PARTKEY|SUPPKEY|LINENUMBER|QUANTITY|EXTENDEDPRICE|DISCOUNT|TAX|RETURNFLAG|LINESTATUS|SHIPDATE|COMMITDATE|RECEIPTDATE|SHIPINSTRUCT|SHIPMODE|COMMENT' lineitem.csv
  sed -i '1iORDERKEY|CUSTKEY|ORDERSTATUS|TOTALPRICE|ORDERDATE|ORDERPRIORITY|CLERK|SHIPPRIORITY|COMMENT' orders.csv
  sed -i '1iPARTKEY|NAME|MFGR|BRAND|TYPE|SIZE|CONTAINER|RETAILPRICE|COMMENT' part.csv
  sed -i '1iPATRKEY|SUPPKEY|AVAILQTY|SUPPLYCOST|COMMENT' partsupp.csv
  sed -i '1iREGIONKEY|NAME|COMMENT' region.csv
  sed -i '1iSUPPKEY|NAME|ADDRESS|NATIONKEY|PHONE|ACCTBAL|COMMENT' supplier.csv

  echo "Making the relevant adjustments..."
  python3 $this_dir/adjust_tpch.py $(pwd)
  cd ..
done

echo "DONE! TPC-H Data of factor-scale $1 was generated!"
