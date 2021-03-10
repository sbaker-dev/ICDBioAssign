# ICDBioAssign

Individuals in the UK Biobank have ICD 9 and 10 codes, which we may wish to use either individually or multiple at a 
time to construct a phenotype. This code just produce these phenotypes for you from a few lines of code. 

## Instructions

### Create your definitions

You will need to create a set of definitions for your phenotypes and write these into a csv file. The format is fairly
simple, you need the name of your phenotype, the ICD9 codes and then your ICD10 codes. ICD9 formats are slightly 
different than ICD10 so you need to follow at present of these three rules.

* If there is only 1 int in both of the columns allowed for ICD9 Codes, then an inclusive range of codes is made between
    the two values.
* If there is only 1 number in the first column, then it is set as the only code
* If there is more than 1 entry in the first column, then each number is returned as a list.

ICD 10 on the other hand is simpler, if you want all of the codes within I you can just use I, if you want all the codes
that are in I4 you can just use I4 etc. An example file is available within Templates, that looks like the following to
give you an example of what you need to submit. 

|Definition|ICD9Min  |ICD9Max|Codes|Codes|Codes|Codes|Codes|Codes|
|----------|---------|-------|-----|-----|-----|-----|-----|-----|
|RD        |3909     |3929   |I0   |     |     |     |     |     |
|VM        |4240     |       |I34  |     |     |     |     |     |
|VA        |4241     |       |I35  |     |     |     |     |     |
|VT        |4242     |       |I36  |     |     |     |     |     |
|V         |4240     |4249   |I34  |I35  |I36  |I37  |I38  |     |
|HID       |4010     |4059   |I1   |     |     |     |     |     |
|IHD       |4109     |4149   |I21  |I22  |I23  |I24  |I25  |     |
|AMI       |4109 4129|       |I21  |I22  |     |     |     |     |
|PHD       |4150     |4179   |I26  |I27  |I28  |     |     |     |



### Install and run the code

The code is available from github, you can install it in python by going to the console and typing the following

```shell script
pip install git+https://github.com/sbaker-dev/ICDBioAssign
```

You will need a csv file containing the ICD codes from your biobank application. If you have isolated only the codes,
then you do not need to set column indexes. If you have other information then you need to tell the program which 
columns contain the data ICD codes for 9 or 10. If you want to use columns containing a string, for example for ICD 10 
Primary 41202, then assign "41202" as a string to column indexes. If you want to use only specific columns, pass a list 
of the indexes of this columns to column indexes. 

You can isolate from multiple files, before compiling out which may be useful if you are working with data split in
ICD9 and ICD10. If you do have ICD9 codes, then you need to specify that ICD10=False, as ICD9 codes function
differently.

When you want to output your file, call the compile_and_write method. You can use one of the two definitions of 
"Maximum" or "Constant" when combining multiple files, both are case sensitive and the program defaults to Maximum.
Maximum, will set an individual to be equal to 1 if any of outcomes in any of the dataset's you isolated is 1. Constant
on the other hand requires all rows in all dataset's to be equal to 1 for the outcome to also be equal to 1. 


```python
from ICDBioAssign.core import ICDBioAssign

icd9_path = "pathHere"
icd10_path = "pathHere"
cod_path = "pathHere"
definition_path = "pathHere"
write_directory = "pathHere"

icd = ICDBioAssign(definition_path, write_directory, "CVD_Outcomes")

icd.set_definitions(icd10_path, column_indexes="40202")
icd.set_definitions(icd9_path, icd_10=False)
icd.set_definitions(cod_path)
icd.compile_and_write()

```

That's it! You should now have everything you need to construct your phenotype definitions from ICD data. 