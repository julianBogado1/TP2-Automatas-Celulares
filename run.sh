#!/bin/bash


#Run java simulation 
cd ../../../
mvn clean package
mvn exec:java -Dexec.mainClass="ar.edu.itba.sims.Main"

#Run python analysis
# cd src/main/python
# source env/bin/activate
# python main.py