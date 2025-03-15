import pandas as pd
import numpy as np
from datetime import date, timedelta

class DataConnector(object):
    """
    Data Connector object for reading app data.
    """

    def __init__(self, data_path):
        self.data_path = data_path
        self.data = self._load_data(data_path)
        self.category_order = self._define_category_order()


    def get_available_categories(self):
        # Returns distinct Categories (dataframe) for filter
        return self.data[["ExpenseCategory"]].drop_duplicates().dropna()


    def get_total_balance(self, filters):
        # Returns total balance (for metric card)
        filtered = self._filter_data(filters)
        return filtered[filtered["ExpenseType"] == "Credit"].ExpenseAmount.sum() - filtered[filtered["ExpenseType"] == "Debit"].ExpenseAmount.sum()  


    def get_overview_data(self, filters):
        # Returns data for summary figure (spending by category)
        filtered = self._filter_data(filters)
        catgs = filtered[
            ["ExpenseCategory", "ExpenseAmount"]
        ][filtered["ExpenseType"] == "Debit"]
        agg = (
            catgs.groupby("ExpenseCategory")
            .agg(
                {"ExpenseAmount": "sum"}
            )
            .reset_index()
        )
        return agg.rename(
            columns={
                "ExpenseAmount": "TotalExpenses",
            }
        )

    def get_savings_goal(self, filters):
        # Returns the Savings goal for the specified date filters
        if filters["ExpenseDate"][0] is None and filters["ExpenseDate"][1] is None:
            saving_goal = self.data.SavingGoal.max()
        elif filters["ExpenseDate"][0] is not None and filters["ExpenseDate"][1] is None:
            start_date = pd.to_datetime(filters["ExpenseDate"][0])
            saving_goal = self.data[self.data.ExpenseDate >= start_date].SavingGoal.max()
        elif filters["ExpenseDate"][0] is  None and filters["ExpenseDate"][1] is not None:
            end_date = pd.to_datetime(filters["ExpenseDate"][1])
            saving_goal = self.data[self.data.ExpenseDate <= end_date].SavingGoal.max()
        else:
            start_date = pd.to_datetime(filters["ExpenseDate"][0])
            end_date = pd.to_datetime(filters["ExpenseDate"][1])
            date_filter = (self.data.ExpenseDate >= start_date) & (self.data.ExpenseDate <= end_date)
            saving_goal = self.data[date_filter].SavingGoal.max()
        return saving_goal
    

    def get_change_data(self, filters):

        curr_filters = filters
        start_date_curr = pd.to_datetime(filters["ExpenseDate"][0] if filters["ExpenseDate"][0] is not None else self.data.ExpenseDate.min())
        end_date_curr = pd.to_datetime(filters["ExpenseDate"][1] if filters["ExpenseDate"][1] is not None else self.data.ExpenseDate.max())
        period = end_date_curr - start_date_curr
        
        curr_filters["ExpenseDate"][0] = start_date_curr
        curr_filters["ExpenseDate"][1] = end_date_curr
        curr = self._filter_data(curr_filters)
        curr = curr[curr["ExpenseType"] == "Debit"]


        prev_filters = filters
        start_date_prev = start_date_curr - period
        end_date_prev = start_date_curr - timedelta(days=1)
        prev_filters["ExpenseDate"][0] = start_date_prev
        prev_filters["ExpenseDate"][1] = end_date_prev
        prev = self._filter_data(prev_filters)
        prev = prev[prev["ExpenseType"] == "Debit"]


        agg_curr = curr.groupby("ExpenseCategory").agg({"ExpenseAmount":"sum"}).reset_index()
        agg_prev = prev.groupby("ExpenseCategory").agg({"ExpenseAmount":"sum"}).reset_index()
        merged = pd.merge(agg_curr, agg_prev, on="ExpenseCategory", how="outer", suffixes=["_curr", "_prev"]).fillna(0)
        merged["net_change"] = merged["ExpenseAmount_curr"] - merged["ExpenseAmount_prev"]
        return merged
    

    def _define_category_order(self):
        sorted = (
                self.data.groupby("ExpenseCategory")
                .count().ExpenseDate
                .sort_values(ascending=False)
            )
        return sorted.index.tolist()



    def _filter_data(self, filters):
        if len(filters["ExpenseCategory"]) != 0:
            category_filter = self.data.ExpenseCategory.isin(filters["ExpenseCategory"])
        else:
            category_filter = pd.Series(True, index=self.data.index)

        if filters["ExpenseDate"][0] is None and filters["ExpenseDate"][1] is None:
            date_filter = pd.Series(True, index=self.data.index)
        elif filters["ExpenseDate"][0] is not None and filters["ExpenseDate"][1] is None:
            start_date = pd.to_datetime(filters["ExpenseDate"][0])
            date_filter = self.data.ExpenseDate >= start_date
        elif filters["ExpenseDate"][0] is  None and filters["ExpenseDate"][1] is not None:
            end_date = pd.to_datetime(filters["ExpenseDate"][1])
            date_filter = self.data.ExpenseDate <= end_date
        else:
            start_date = pd.to_datetime(filters["ExpenseDate"][0])
            end_date = pd.to_datetime(filters["ExpenseDate"][1])
            date_filter = (self.data.ExpenseDate >= start_date) & (self.data.ExpenseDate <= end_date)


        return self.data[
            (category_filter)
            & (date_filter)
        ]

    def _load_data(self, demo):
        # Load data from excel file
        df = pd.read_excel(self.data_path, sheet_name="Data", header=None)
        df_savings = pd.read_excel(self.data_path, sheet_name="Savings", header=None)
        df_savings.rename(columns={0: "SavingGoal", 1:"SavingGoalDate"}, inplace=True)
        df_savings["SavingGoalDate"] = pd.to_datetime(df_savings["SavingGoalDate"], format='%d-%m-%Y')
        df.rename(columns={0: "ExpenseDate", 1: "ExpenseAmount", 2:"ExpenseCategory", 3:"ExpenseType", 4:"ExpenseDesc", 5:"ExpenseCurr"}, inplace=True)
        df["ExpenseDate"] = pd.to_datetime(df["ExpenseDate"], format='%d-%m-%Y')
        df["SavingGoal"] = 0
        for idx1, _ in df.iterrows():
            for _, row2 in df_savings.iterrows():
                df.loc[idx1, "SavingGoal"] = row2["SavingGoal"] if df.loc[idx1, "ExpenseDate"] <= row2["SavingGoalDate"] else 0
        return df

