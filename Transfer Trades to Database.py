import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import sqlalchemy as db
import pymysql

# IMPORT data from .xlsx
df = pd.read_excel({"""Your DIrectory Goes Here"""})

# set live account number
liveAccount = 35281648

#get account number from xlsx file
tmp = df.iloc[1, 0]

# extract account number from xlsx file
accountNumber = tmp[[x.isdigit() for x in tmp].index(True):]

# check if account number matches, set accountNumber variable with ternary operator
accountType = 'Live' if int(accountNumber) == liveAccount else "Demo"

# drop first three rows
df = df.drop(df.index[[0, 1, 2]])

### set column names as first row
df.columns = df.iloc[0]

# drop first row
df = df.drop(df.index[[0]])

### drop rows from where Ticket column is 'Closed P/L:' onward
#df = df.drop(df.index[(df.loc[df['Ticket'] == 'Closed P/L:'].index[0] - 6):])
df = df.drop(df.index[df.loc[df.Ticket == 'Closed P/L:'].index[0] - 6: ])

### drop rows with blanks in the 'Ticket' column
df.dropna(subset = ["Ticket"], inplace=True)

### extract date from 'Open Time' column
df['Date'] = df['Open Time'].str[:10]

### extract open time from 'Open Time' column
df['OpenTime'] = df['Open Time'].str[11:]

### extract close time from 'Close Time' column
df['CloseTime'] = df['Close Time'].str[11:]

### drop unnecessary columns
df = df.drop(columns = ['Open Time', 'Close Time', 'Taxes', 'Swap', 'S / L'])

### rename 'price' columns - can't include it below because 2 columns were named identically
df.columns.values[[4, 6]] = ["OpenPrice", "ClosePrice"]

### rename remaining columns
df = df.rename(columns = {
                            'T / P': 'TakeProfitPrice',
                            'Type': 'TradeType',
                            'Size': 'TradeSize',
                            'Item': 'TradeSymbol',
                            'Date': 'TradeDate'})

### set value of 'accountType' column
df['accountType'] = accountType

### drop dataframe index
df = df.reset_index(drop = True)

# sqlalchemy
### CONNECT to db
engine = db.create_engine('mysql+pymysql://root:ReganjohnD1@localhost:3306/rj_ecosystem')
con = engine.connect()

### INSERT data into table
df.to_sql(name = 'snptrades', con = con, if_exists = 'append', index = False)