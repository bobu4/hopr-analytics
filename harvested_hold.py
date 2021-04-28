from etherscan import Etherscan
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Table_Model(QAbstractTableModel):
    def __init__(self, data):
        super(Table_Model, self).__init__()
        self._data = data
        self._header = ['Address','Holding harvest', 'Total harvest']

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
        table_data = farm.hold_tokens()
        self.table = QTableView()
        self.model = Table_Model(table_data)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()
        layout = QGridLayout()
        layout.addWidget(self.table, 0, 0)
        self.resize(500,400)
        self.setLayout(layout)
        self.show()

class Farm_analytics():
    def __init__(self):
        self.eth  = Etherscan('B6F4YNTIAZD481BGYQV64URITSI4QJRDAX')
        self.hopr_contract = '0xf5581dfefd8fb0e4aec526be659cfab1f8c781da'.lower()
        self.farm_address = '0x2Fc0E2Cfe5D6Ea300D555E5907319a5F7E09884f'.lower()
        self.uni_address = '0x92c2fC5F306405eaB0fF0958f6D85d7F8892CF4D'.lower()

    def hold_tokens(self):
        number = 1
        tokens_holders = {}
        while 1:
            try:
                transactions = self.eth.get_erc20_token_transfer_events_by_address_and_contract_paginated(contract_address=self.hopr_contract, address=self.farm_address, page=number, offset=100, sort='asc')
                for transaction in transactions:
                    if transaction['from'] == self.farm_address:
                        timestamp = float(transaction['timeStamp'])
                        address = transaction['to']
                        if transaction['to'] not in tokens_holders:
                            tokens_holders[address] = {'total_harvest': 0, 'holding_harvest': 0}
                        else:
                            continue
                        transactions_by_address = self.eth.get_erc20_token_transfer_events_by_address_and_contract_paginated(contract_address=self.hopr_contract, address=address, page=1, offset=100, sort='asc')
                        tokens_holders[address]['total_harvest'] += float(transaction['value']) / pow(10, 18)
                        tokens_holders[address]['holding_harvest'] += float(transaction['value']) / pow(10,18)
                        for transaction_by_address in transactions_by_address:
                            if float(transaction_by_address['timeStamp']) > timestamp:
                                if transaction_by_address['from'] == self.farm_address:
                                    timestamp = float(transaction_by_address['timeStamp'])
                                    tokens_holders[address]['total_harvest'] += float(transaction_by_address['value']) / pow(10,18)
                                    tokens_holders[address]['holding_harvest'] += float(transaction_by_address['value']) / pow(10,18)
                                elif transaction_by_address['from'] == address:
                                    tokens_holders[address]['holding_harvest'] -= (float(transaction_by_address['value']) / pow(10,18))
                                    if tokens_holders[address]['holding_harvest'] < 0:
                                        tokens_holders[address]['holding_harvest'] = 0
                number += 1
            except:
                table_data = []
                for addresses in tokens_holders:
                    if tokens_holders[addresses]['holding_harvest'] > 0:
                        table_data.append([addresses, tokens_holders[addresses]['holding_harvest'], tokens_holders[addresses]['total_harvest']])
                break
        return table_data


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Table()
    sys.exit(app.exec_())
