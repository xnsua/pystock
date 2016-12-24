import pandas as pd


def read_sci_short():
    sci_all = read_sci()
    sci_short = pd.DataFrame({
        'open': sci_all['Open'],
        'close': sci_all['Close'],
        'high': sci_all['High'],
        'low': sci_all['Low'], },
       )
    # Fatal : Can not write this line as parameter 'index=sci_all'Date'' in above line
    sci_short.set_index(sci_all['Date'])
    return sci_short;


def read_sci():
    return pd.read_csv('stockSci.csv')
