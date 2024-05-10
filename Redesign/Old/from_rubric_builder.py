
def instantiateTable(self,):


        self.numColumns = dpg.get_value(self.columnSetter)

        with dpg.child_window(horizontal_scrollbar=True):

            with dpg.group(horizontal=True):

                with dpg.child_window(width=120,border=False):
                    with dpg.table(header_row=True):

                        rowLabels = dpg.add_table_column(label=f'Index',width_fixed=True,width=self.tableColumnDefaultWidth)
                        with dpg.table_row():
                            dpg.add_text("Column Name")
                        with dpg.table_row():
                            dpg.add_text("Necessary?")
                        with dpg.table_row():
                            dpg.add_text("Tag")


                with dpg.table(header_row=True,scrollX=True,) as self.tableEditor:

                    columns = []
                    columnNames = []
                    columnNecessary = []
                    columnNecessary = []


                    for column in range(0,self.numColumns):
                        _ = dpg.add_table_column(label=f'{column}',tag=f'{self._id}_c{column}',width_fixed=False,width=self.tableColumnDefaultWidth)
                        self.allColumns.append(_)
                    #for i in range(0,dpg.get_value(self._columns)):
                    with dpg.table_row() as self.columnNameRow:
                        for j in range(0,self.numColumns):
                            dpg.add_input_text()#label="Name?")
                   
                    
                    with dpg.table_row() as self.necessaryRow:
                        for j in range(0,self.numColumns):
                            dpg.add_checkbox()#label="Necessary?")

                    with dpg.table_row() as self.tagRow:
                        for j in range(0,self.numColumns):
                            dpg.add_input_text()#label="TAG")

def change_columns(self,sender,app_data):
        
        if app_data>=self.maxCols:
            dpg.configure_item(self.error,show=True)
        else:
            dpg.configure_item(self.error,show=False)

        # WORK ON A DECELLERATOR HERE
        time.sleep(0.01)

        # Fixed Width Setter for expanding columns
        if app_data >= 9:
            defaultFixedWidth=True
            for column in self.editor.columns:
                dpg.configure_item(column,width_fixed=True)
        else:
            defaultFixedWidth=False
            for column in self.editor.columns:
                dpg.configure_item(column,width_fixed=False)

        # Adding Columns
        if app_data > self.columns:
            for column in range(self.columns,app_data):
                self.editor.add_column(column,defaultFixedWidth)
                '''dpg.push_container_stack(self.tableEditor)
                _ = dpg.add_table_column(label=f'{column}',tag=f'{self._id}_c{column}',width_fixed=defaultFixedWidth,width=self.tableColumnDefaultWidth)
                self.allColumns.append(_)

                dpg.push_container_stack(self.necessaryRow)
                dpg.add_checkbox(label="Necessary?")
                dpg.push_container_stack(self.tagRow)
                dpg.add_input_text(label="TAG")'''
        # Subtracting COlumns
        elif app_data < self.columns:
            for column in range(app_data,self.columns):
                self.editor.delete_column(column)

                '''dpg.push_container_stack(self.tableEditor)
                dpg.delete_item(f'{self._id}_c{column}')
                self.allColumns = self.allColumns[:-1]'''
                pass

        self.columns = app_data
        #except Exception as e:
        #    print(e)
