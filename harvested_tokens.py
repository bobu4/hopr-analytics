from etherscan import Etherscan
import datetime
import calendar
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg


class Table_Model(QAbstractTableModel):
    def __init__(self, data):
        super(Table_Model, self).__init__()
        self._data = data
        self._header = ['Date', 'Harvest amount']

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._header[section]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])


class Table(QWidget):
    def __init__(self):
        super().__init__()
        farm = Farm_analytics()
        table_data, x, y = farm.harvest_tokens()
        plt = pg.plot()
        xdict = dict(enumerate(x))
        bargraph = pg.BarGraphItem(x=[n for n in range(len(y))], height=y, width=0.6)
        plt.getAxis('bottom').setTicks([xdict.items()])
        plt.addItem(bargraph)
        plt.setBackground(background=None)
        self.table = QTableView()
        self.model = Table_Model(table_data)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()
        layout = QGridLayout()
        layout.addWidget(self.table, 0, 0)
        self.resize(500, 600)
        self.setLayout(layout)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.show()


class Farm_analytics():
    def __init__(self):
        self.eth = Etherscan('B6F4YNTIAZD481BGYQV64URITSI4QJRDAX')
        self.hopr_contract = '0xf5581dfefd8fb0e4aec526be659cfab1f8c781da'.lower()
        self.farm_address = '0x2Fc0E2Cfe5D6Ea300D555E5907319a5F7E09884f'.lower()
        self.uni_address = '0x92c2fC5F306405eaB0fF0958f6D85d7F8892CF4D'.lower()

    def harvest_tokens(self):
        number = 1
        days_amount = {}
        harvest_list = []
        harvest_date = []
        first_harvest_date = 0
        table_list = []
        while 1:
            try:
                transactions = self.eth.get_erc20_token_transfer_events_by_address_and_contract_paginated(
                    contract_address=self.hopr_contract, address=self.farm_address, page=number, offset=100, sort='asc')
                for transaction in transactions:
                    if transaction['from'] == self.farm_address:
                        if first_harvest_date == 0:
                            first_harvest_date = datetime.date.fromtimestamp(float(transaction['timeStamp']))
                        date = datetime.datetime.fromtimestamp(float(transaction['timeStamp']))
                        day_month = str(date.day) + ' ' + calendar.month_abbr[int(date.month)]
                        tokens_amount = float(transaction['value']) / pow(10, 18)
                        if day_month not in days_amount:
                            days_amount[day_month] = 0
                        days_amount[day_month] += tokens_amount
                        last_harvest_date = datetime.date.fromtimestamp(float(transaction['timeStamp']))
                number += 1
            except:
                delta = last_harvest_date - first_harvest_date
                compression = round(delta.days / 10)
                for amount in days_amount:
                    table_list.append([amount, days_amount[amount]])
                    harvest_list.append(days_amount[amount])
                    harvest_date.append(amount)
                update_date_list = []
                for index, date in enumerate(harvest_date):
                    if (index + 1) % compression == 0:
                        update_date_list.append(' ')
                    else:
                        update_date_list.append(date)
                break
        return table_list, update_date_list, harvest_list


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Table()
    sys.exit(app.exec_())
