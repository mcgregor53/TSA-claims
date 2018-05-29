import pandas as pd


data_17 = pd.read_csv("../csv/17_claims.csv", dtype = str, na_values = '-')
data_16 = pd.read_csv("../csv/16_claims.csv", dtype = str, na_values = '-')
data_15 = pd.read_csv("../csv/15_claims.csv", dtype = str, na_values = '-')
data_14 = pd.read_csv("../csv/14_claims.csv", dtype = str, na_values = '-', nrows = 8855)
data_10 = pd.read_csv("../csv/10-13_claims.csv", dtype = str, na_values = '-', nrows = 41598)
data_07 = pd.read_csv("../csv/07-09_claims.csv", dtype = str, na_values = '-')
data_02 = pd.read_csv("../csv/02-06_claims.csv", dtype = str, na_values = '-')

print 'Read in all csv files'

data_17['Claim Type'] = data_17['Claim Type'].str.replace('Injur$', 'Injury')
data_17['Disposition'] = data_17['Disposition'].str.replace('^losed', 'Closed')
data_17['Disposition'] = data_17['Disposition'].str.replace('\*', '')

data_16 = data_16[data_16['Claim Number'] != 'Claim Number']
data_16['Claim Number'] = data_16['Claim Number'].str.replace('\s', '')
data_16['Incident Date'] = data_16['Incident Date'].str.replace('\s', '')
data_16['Incident Date'] = data_16['Incident Date'].str.replace('2016', '2016 ')
data_16['Disposition'] = data_16['Disposition'].str.replace('\*', '')
data_16['Disposition'] = data_16['Disposition'].str.replace('-', '')

data_15.rename(columns = {"Incident D":"Incident Date"}, inplace = True)

data_10 = data_10[data_10['Claim Number'] != '<BR>']

data_07.rename(columns = {"Item":"Item Category"}, inplace = True)

data_02.rename(columns = {"Item":"Item Category"}, inplace = True)

col_list = data_02.columns.tolist()

data = pd.concat([data_02, data_07, data_10, data_14, data_15, data_16, data_17], ignore_index = True)

data = data[col_list]
data.drop_duplicates(subset = 'Claim Number', inplace = True)

data['Item Category'] = data['Item Category'].str.replace('Décor', 'Decor')
data['Item Category'] = data['Item Category'].str.replace('[\s]', '')
data['Airline Name'] = data['Airline Name'].str.replace('[\s]', '').str.upper()
data['Claim Type'] = data['Claim Type'].str.replace('[\s]', '')
data['Claim Amount'] = data['Claim Amount'].str.replace('[\s]|\$|,', '')
data['Close Amount'] = data['Close Amount'].str.replace('[\s]|\$|,', '')
data['Disposition'] = data['Disposition'].str.replace('[\s]', '')

data.to_csv('../csv/all_claims.csv', index = False)

print 'Saved combined data to all_claims.csv'
