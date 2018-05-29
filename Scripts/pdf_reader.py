# This program is designed to read in the tables from the 2017 and 2016 TSA
# claims data, found at https://www.dhs.gov/tsa-claims-data in pdf form.
#
# When read in using read_pdf from the tabula module, the columns must be
# specified manually since the automated process gets things wrong here, and
# a single claim may be spread over 3 rows.
# The function read_to_csv will do the necessary work to turn the pdf
# tables into csv files.

from tabula import read_pdf
import pandas as pd


def read_to_csv(filename, column_boundaries, drop_rows):
    """This function will read in data from the tables in one of the pdfs,
    store it as a dataframe, do some preliminary cleaning to glue rows
    together, and save it as a csv file with the same name.

    filename (string) = name of pdf file to read in, without extension
    column_boundaries (list of ints) = list of x-coordinates of the boundaries
        between columns
    drop_rows (integer) = number of rows to drop at the end
    """
    df = read_pdf("../original_data/" + filename +'.pdf', pages = 'all', guess = False, columns = column_boundaries)

    print "Read in file: " + filename + ".pdf"

    x = len(df)
    df = df.drop(range(x - drop_rows, x))

    row_list = []
    temp_dict = {}
    for i in range(len(df.index)):
        for j in df.columns:
            if ~df[j].isnull()[i]:
                if j in temp_dict:
                    temp_dict[j] += ' ' + df[j][i]
                else:
                    temp_dict[j] = df[j][i]
        if ~df[df.columns[1]].isnull()[i]:
            row_list.append(temp_dict)
            temp_dict = {}

    data = pd.DataFrame(row_list)
    data = data[df.columns]
    data.to_csv("../csv/" + filename + '.csv', encoding = 'utf-8', index = False)
    print "Saved clean data as: " + filename + ".csv"


filename = '17_claims'
column_boundaries = [208, 304, 397, 470, 645, 777, 948, 1043, 1506, 1570]
drop_rows = 7
read_to_csv(filename, column_boundaries, drop_rows)



filename = '16_claims'
column_boundaries = [190, 262, 375, 430, 585, 708, 855, 940, 1202, 1264]
drop_rows = 7
read_to_csv(filename, column_boundaries, drop_rows)
