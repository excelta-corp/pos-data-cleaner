# Setting up a new distributor
Are you looking to set up a brand new distributor, adjust to a new
 POS report format, or investigate an error? This
 document will help by providing a step-by-step setup process with an in-depth 
 look at how pattern files work.
 
## For example
Let's say we're a leading manufacturer of quality bladed instruments—namely
, knives and axes. We have recently started distributing our fine products
 through **Bob's Blades** and have received our first POS report.
 
First, let's take a look at our own product information:

## Our catalog
Here's a sample of our hypothetical products:

﻿Stock Code|Description|Price|Group|Category
---|---|---|---|---|
KNF-CHEF|Chef's Knife|$53.00|Kitchen|Knife
KNF-PARI|Paring Knife|$55.00|Kitchen|Knife
KNF-UTIL|Utility Knife|$65.00|Kitchen|Knife
KNF-SANT|Santoku|$54.00|Kitchen|Knife
KNF-BONI|Boning Knife|$47.00|Kitchen|Knife
KNF-BREA|Bread Knife|$59.00|Kitchen|Knife
KNF-CLEA|Cleaver|$35.00|Kitchen|Knife
KNF-STEA|Steak Knife|$35.00|Kitchen|Knife
KNF-PEEL|Peeler|$43.00|Kitchen|Knife
KNF-JAM|Jam Knife|$48.00|Kitchen|Knife
KNF-KITC|Kitchen Axe|$37.00|Kitchen|Axe
KNF-SPAT|Spatula|$36.00|Kitchen|Knife
KNF-CARV|Carving Fork|$50.00|Kitchen|Knife
KNF-WHIT|Whittling Knife|$27.00|Timber|Knife
AXE-SPLI|Splitting Maul|$23.00|Timber|Axe
AXE-SCAN|Scandanavian Axe|$28.00|Timber|Axe
AXE-HATC|Splitting Hatchet|$46.00|Timber|Axe
AXE-HUNT|Hunter's Axe|$38.00|Timber|Axe
AXE-DOUB|Double Axe|$49.00|Timber|Axe
AXE-FELL|Felling Axe|$27.00|Timber|Axe
AXE-CARP|Carpenter's Axe|$43.00|Timber|Axe

The table above would be similar to our **Product Lookup Table** reference
 document, which is used to associate a given Stock Code with a Group and
  Category.
  
## Looking at Bob's POS Report
The report we get from the distributor is called the "raw data" for the
 purposes of this documentation. As each disty is different, we'll have to
  pay close attention to the details of this document in order to create the
   pattern file.

### Save as CSV UTF-8 to strip formatting
The first thing to do is to open up Bob's POS report in Excel and save it in
 the raw data input folder as
 a UTF-8 CSV file. (The file type will be `CSV UTF-8 (Comma delimited)(*.csv)` in Excel.) Keep spaces, if desired, but remove any other punctuation
  symbols. For example, Bob's Blades would become `Bobs Blades.csv`. 
  
  Once the file has been saved, close Excel and open the CSV file to view the
   data with no formatting.
  
### Headers, or no headers?
All POS files that we receive can be divided into two categories: Those with
 a header row, and those without. Reports that add titles, dates, or blank
  rows to the top of the document are considered to have no headers.
  
![Example of headers and no headers](images/header_example.png)

In the above example, the document on the left is considered to have **no
 headers**, even though there are column names on row 5. The document on the
  right has column names in its first non-blank row, so it has headers.
  
>Why does this matter? When we're putting together a Pattern file later on, 
>we'll need to refer to columns in this file. If the document has headers, we
>can use the column names. If not, we use letters instead.

### Do we have all the fields we need?
Here are the fields we're looking for:

Data|Required|Note
----|--------|----
Customer|❌|Person or business
City|❌|If available
St|❌|State - highly recommended!
Zip|✔|Postal code, any format
Item|✔|Our part number
Qty|✔|Necessary
Cost|✔|Unnecessary if we have Ext
Ext|✔|Unnecessary if we have Cost
Disty|❌|Special - see note below

>Note that most POS files won't have a column containing distributor names
> because they're from a single distributor. However, our internal reports
> sometimes combine multiple distributors. If this is the case, we need to have
> a column which includes the distributor names.

If we have the bare minimum of part number, quantity, zip code, and either
 the item cost or the total cost, we're good to go. However, the more of
  these fields we can satisfy (except Disty) the better.

If we do not have these fields, the program will not have enough data to
 proceed and we should find an alternative way to process the file, or
  request more information from the distributor.

## Creating the pattern file
Pattern files are tiny spreadsheets that the program uses to map a column in the 
raw file to a column in the finished file. As long as future POS reports
 follow the same format, you should only need to create one pattern file per
  new distributor.
  
### Create a blank pattern file
Open Excel and type the following exactly:

◢|A|B|C
-----|---|---|---
**1**|Target|Source|Strip String
**2**|Customer||
**3**|City||
**4**|St||
**5**|Zip||
**6**|Item||
**7**|Qty||
**8**|Cost||
**9**|Ext||
**10**|Disty||

When you're done, save this file as a UTF-8 CSV where the other pattern files
 are kept. Set the filename to the raw data filename, followed by `_PATTERN.csv
 `. For example
 , we'd
  save this one as `Bobs Blades_PATTERN.csv`

## Strip String