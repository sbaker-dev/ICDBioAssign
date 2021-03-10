from miscSupports import flip_list, terminal_time
from csvObject import CsvObject, write_csv
import sys


class ICDBioAssign:
    def __init__(self, definition_path, write_directory, write_name, id_column=0):

        # Construct the lookup for both the ICD 10 and 9 types
        self._icd_10_lookup = self._construct_icd10_lookup(definition_path)
        self._icd_9_lookup = self._construct_icd9_lookup(definition_path)

        # Set the ID column, defaults to 0
        self._id_column = id_column

        # Set output information
        self._write_directory = write_directory
        self._write_name = write_name

        self.data_set_values = []
        self.ids_list = []

    def set_definitions(self, file_path, column_indexes=None, icd_10=True):
        """
        Match the ICP row data to a dictionary of definitions, assigning a value of 1 if an individual matches that
        specification and 0 otherwise for each definition defined in the lookup file.

        :param file_path: The path to the ICD extract file you wish to load
        :type file_path: Path | str

        :param column_indexes: If you wish to use specific column indexes you can provide a common string or a list of
            ints to extract values from these headers specifically. If you want to use all the headers, leave as the
            default of None.
        :type column_indexes: None | list[int] | str

        :param icd_10: If the ICD file contains ICD 10 or ICD 9 values, icd 10 if True icd 9 otherwise. Defaults to True
        :type icd_10: bool

        :return: Nothing, append values to data_set_values to compile when ready
        :rtype: None
        """

        icd_file, index_min, index_max = self._load_file(file_path, column_indexes)

        write_list = []
        for i, row in enumerate(icd_file.row_data):
            # Log progress
            if i % 10000 == 0:
                print(f"{i} / {icd_file.column_length}")

            # Isolate the id
            ids = row[self._id_column]
            self.ids_list.append(ids)

            # Remove the id from the row so that we don't match codes to it
            row = [r for i, r in enumerate(row) if i != self._id_column]

            # Assign each individual a 1 or 0 for each phenotype based on the codes in the lookup
            if icd_10:
                assigned_values = [self._assign_definition(self._extract_codes(row, index_min, index_max), code_list)
                                   for code_list in self._icd_10_lookup.values()]
            else:
                assigned_values = [self._assign_definition(self._extract_codes(row, index_min, index_max), code_list)
                                   for code_list in self._icd_9_lookup.values()]

            # write this id's assigned_value and update the list of ids
            write_list.append([ids] + assigned_values)

        self.data_set_values.append(write_list)

    @staticmethod
    def _load_file(file_path, column_indexes):
        """
        Load the file containing the ICD codes, and return this and the column indexes of interest based on the type of
        column indexes.

        :param file_path: Path to the icd file
        :type file_path: str | Path

        :param column_indexes:
        The indexes to use will be compared to column indexes if they are set.
        If a str, headers will be checked to see if this str is in the header and kept it true.
        If a list[int], then these indexes will be used.
        If None, then all indexes will be used.
        :type column_indexes: None | str | list[int]

        :return: The load Csv file as well as the min and max indexes to use
        :rtype: (CsvObject, int, int)
        """
        print("Loading file...")
        icd_file = CsvObject(file_path)

        if column_indexes is None:
            indexes = [i for i in range(len(icd_file.headers))]
        elif isinstance(column_indexes, str):
            indexes = [i for i, header in enumerate(icd_file.headers) if column_indexes in header]
        elif isinstance(column_indexes, list):
            indexes = column_indexes
        else:
            sys.exit(f"Unexpected argument for column indexes: Found type {type(column_indexes)} but expected a "
                     f"NoneType, string or list\n"
                     f"If you want to use all columns, leave Column indexes as None\n"
                     f"If you want to use columns containing a string, for example for ICD 10 Primary 41202, then "
                     f"assign 41202 to column indexes\n"
                     f"If you want to use only specific columns, pass a list of the indexes of this columns to "
                     f"column indexes")

        return icd_file, min(indexes), max(indexes)

    @staticmethod
    def _extract_codes(raw_row, index_min, index_max):
        """
        Extract data from the columns for this row, if the row is not equal nan and the columns are between the min and
        max indexes
        """
        return [row for row in raw_row[index_min: index_max] if row != "nan"]

    def _assign_definition(self, row, code_list):
        """
        For the current definitions code list, check to see if any of the row's ICD codes match a code in our code list.
        If so, return 1. If no codes are set then return 0.
        """
        for code in code_list:
            if self._check_icd(row, code):
                return 1
        return 0

    @staticmethod
    def _check_icd(row, code):
        """
        For the current code in current row, return True if the code is within one of the ICD codes assign to this
        individual
        """
        for icd in row:
            if code in icd:
                return True

    @staticmethod
    def _construct_icd10_lookup(definition_path):
        """
        For ICD 10, we just need to assign each phenotype each code from rows, starting from the third row where ICD 10
        codes start in the csv file. Row[0] represents the phenotype name.
        """
        return {row[0]: [r for r in row[3:] if r != ""] for row in CsvObject(definition_path).row_data}

    def _construct_icd9_lookup(self, definition_path):
        """
        For ICD 9, we need to take the first and second columns to get the min and max range to convert these into a
        process similar to our ICD10 codes. Row[0] represents the phenotype name.
        """
        return {row[0]: self._set_icd9_def(row) for row in CsvObject(definition_path).row_data}

    @staticmethod
    def _set_icd9_def(row):
        """
        ICD 9 codes need to be converted into a manner that can be used with our ICD 10 system, this converts them by
        taking currently 1 of 3 rules. If there is only 1 int in both of the columns allowed for ICD9 Codes, then an
        inclusive range of codes is made between the two values. If there is only 1 number in the first column then it
        is set as the only code, and if there is more than 1 entry in the first column then each number is returned as a
        list.
        """
        minimum, maximum = row[1].split(" "), row[2].split(" ")

        if maximum[0] == "":
            maximum = []
        if (len(minimum) == 1) and (len(maximum) == 1):
            return [str(i) for i in range(int(minimum[0]), int(maximum[0]) + 1)]
        elif (len(minimum) == 1) and (len(maximum) == 0):
            return [str(minimum[0])]
        elif (len(minimum) > 1) and (len(maximum) == 0):
            return [str(char) for char in minimum]
        else:
            raise ValueError("Unexpected Input for ICD9")

    def compile_and_write(self, merger="Maximum"):
        """
        This will compile all the data you have collected into a single dataset based on a merge type

        :param merger: This takes the value of Maximum or Constant to determine the merge type. If Maximum then if 1 is
            present in any of the dataset's then this individual will be assigned a 1. If constant, then individuals
            must be assigned a 1 in every dataset to be assigned a 1
        :type merger: str

        :return: Nothing, write out the output to a file then stop
        :rtype: None
        """

        assert merger in ("Maximum", "Constant"), f"Merger takes the values of Maximum or Constant yet was given " \
                                                  f"{merger}"

        # Isolate the unique ids
        unique_ids = {i: [] for i in sorted(list(set(self.ids_list)))}

        # For each dataset that has been appended
        for data_set in self.data_set_values:
            # Iterate the rows
            for row in data_set:
                # Add the row values to the id
                unique_ids[row[self._id_column]].append([r for i, r in enumerate(row) if i != self._id_column])

        # For id - value set
        output_values = []
        for ids, value_list in unique_ids.items():
            id_row = [ids]

            # If we isolated an entry in every dataset
            if len(value_list) == len(self.data_set_values):

                # Then isolate the row values based on one of the rules
                for row in flip_list(value_list):
                    # If the merger type of maximum then if 1 is present in any of the dataset's then this individual
                    # will be assigned a 1
                    if merger == "Maximum":
                        id_row.append(max(row))

                    # If constant, then individuals must be assigned a 1 in every dataset to be assigned a 1
                    elif merger == "Constant":
                        if sum(row) == len(row):
                            id_row.append(1)
                        else:
                            id_row.append(0)

                    else:
                        raise TypeError("Critical error: Reached Non-set merger value")

            output_values.append(id_row)

        write_csv(self._write_directory, self._write_name, ["ID"] + list(self._icd_9_lookup.keys()), output_values)
        print(f"Constructed {self._write_name} at {terminal_time()}")
