# import pandas as pd
from pandas import read_csv

# from sklearn.metrics.pairwise import cosine_similarity  # linear_kernel

import numpy as np
DATA_KEY = "proccessed"
DATA_FILE = "./product/recommenders/bert_with_description_field.csv"


def to_numpy(x):
    return np.fromstring(x[3:-2].replace("\n", ""), sep=" ")


class CB_MODEL(object):
    def __init__(self, threshold=0.5):
        self._dataset = read_csv(DATA_FILE)
        self._dataset[DATA_KEY] = self._dataset[DATA_KEY].apply(to_numpy)
        self._threshold = threshold

    def __str__(self):
        return len(self._dataset)

    def get_item_vector_by_uid(self, items):

        # Get the table of item
        # :param items: The list of items (type is product.Models.Book)
        # :return: Table (with 2 column (id, feature)) of the items
        return self._dataset[
            self._dataset["id"].isin(items.values_list("sku", flat=True))
        ]

    def _similarity(self, v_base_items, v_compare_items):
        return []
        # return cosine_similarity(v_base_items, v_compare_items)

    def run(self, rate_items, target_items):
        v_rate_items = self.get_item_vector_by_uid(rate_items)
        v_target_items = self.get_item_vector_by_uid(target_items)

        # Implement the CB filter here

        rate_vector = np.array(v_rate_items.feature.to_list())
        target_vector = np.array(v_target_items.feature.to_list())
        print(rate_vector)
        print(target_vector)
        index = self._similarity(rate_vector, target_vector).flatten().argsort()[::-1]

        # ordering = 'FIELD(`sku`, %s)' % ','.join(str(id) for id in index)
        skus = v_target_items.iloc[index].id.to_list()
        clauses = " ".join(
            ["WHEN sku=%s THEN %s" % (pk, i) for i, pk in enumerate(skus)]
        )
        ordering = "CASE %s END" % clauses

        return target_items.extra(select={"ordering": ordering}, order_by=("ordering",))


cb = CB_MODEL()
