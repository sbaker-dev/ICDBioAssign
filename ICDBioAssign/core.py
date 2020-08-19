from csvObject import CsvObject, write_csv
import sys


class ICDBioAssign:
    def __init__(self, definition_path, file_path, icd10=True, column_indexes=None):
        print("Loading Files...")
        if icd10:
            self._lookup = self._construct_icd10_lookup(definition_path)
        else:
            self._lookup = self._construct_icd9_lookup(definition_path)

        self._icd_file, indexes = self._load_file(column_indexes, file_path)
        self._column_min = min(indexes)
        self._column_max = max(indexes)
        print("Loaded Files")

    def set_definitions(self, write_directory, write_name):
        """
        Match our ICP10 row data to a dictionary of definitions, assigning a value of 1 if an individual matches that
        specification and 0 otherwise for each definition defined in the lookup file. Write out the results
        :return:
        """
        write_list = []
        for i, row in enumerate(self._icd_file.row_data):
            # Log progress
            if i % 10000 == 0:
                print(f"{i} / {len(self._icd_file.row_data)}")

            # Assign each individual a 1 or 0 for each phenotype based on the codes in the lookup
            write_list.append([self._assign_definition(self._extract_codes(row), code_list)
                               for code_list in self._lookup.values()])

        write_csv(write_directory, write_name, list(self._lookup.keys()), write_list)

    def _extract_codes(self, raw_row):
        """
        Extract data from the columns for this row, if the row is not equal nan and the columns are between the min and
        max indexes
        """
        return [row for row in raw_row[self._column_min: self._column_max] if row != "nan"]

    def _assign_definition(self, row, code_list):
        """
        For the current definitions code list, check to see if any of the row's ICD codes match a code in our code list. If
        so, return 1. If no codes are set then return 0.
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
    def _load_file(column_indexes, file_path):
        """
        Load the file containing the ICD codes, and return this and the column indexes of interest based on the type of
        column indexes.
        """
        icd_file = CsvObject(file_path)

        if column_indexes is None:
            return icd_file, [i for i in range(len(icd_file.headers))]
        elif isinstance(column_indexes, str):
            return icd_file, [i for i, header in enumerate(icd_file.headers) if column_indexes in header]
        elif isinstance(column_indexes, list):
            return icd_file, column_indexes
        else:
            sys.exit(f"Unexpected argument for column indexes: Found type {type(column_indexes)} but expected a "
                     f"NoneType, string or list\n"
                     f"If you want to use all columns, leave Column indexes as None\n"
                     f"If you want to use columns containing a string, for example for ICD 10 Primary 41202, then "
                     f"assign 41202 to column indexes\n"
                     f"If you want to use only specific columns, pass a list of the indexes of this columns to "
                     f"column indexes")

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
        return {row[0]: self._icd9_to_10(row) for row in CsvObject(definition_path).row_data}

    @staticmethod
    def _icd9_to_10(row):
        """
        ICD 9 codes need to be converted into a manner that can be used with our ICD 10 system, this converts them by taking
        currently 1 of 3 rules. If there is only 1 int in both of the columns allowed for ICD9 Codes, then an inclusive
        range of codes is made between the two values. If there is only 1 number in the first column then it is set as the
        only code, and if there is more than 1 entry in the first column then each number is returned as a list.
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
            sys.exit("Unexpected input")
