import logging


class Helpers:
    def check_duplicates(self, new_data, table_values, key):
        need_insertion = []
        for obj in new_data:
            if type(obj) == dict:
                if not table_values.isin([obj[key]]).any().any():
                    need_insertion.append(obj)
                # else:
                    # logging.info("Tuple with github's {} key value already".format(key) +
                    #     "exists in our db: {}\n".format(str(obj[key])))
        logging.info("Page recieved has {} tuples, while filtering duplicates this ".format(str(len(new_data))) +
            "was reduced to {} tuples.\n".format(str(len(need_insertion))))
        return need_insertion
