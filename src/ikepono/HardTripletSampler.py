import numpy as np
from torch.utils.data import Sampler

from ikepono.LabeledImageVector import LabeledImageVector

class HardTripletBatchSampler(Sampler):
    def __init__(self, vector_store, individuals_per_batch, max_photos_per_individual):
        self.vector_store = vector_store
        self.individuals_per_batch = individuals_per_batch
        self.max_photos_per_individual = max_photos_per_individual
        self.triplets = (max_photos_per_individual - 1) // 2

        self.individuals = self.vector_store.get_all_labels()

    def __iter__(self):
        while True:
            batch = []
            selected_individuals = np.random.choice(self.individuals, self.individuals_per_batch, replace=False)

            for individual in selected_individuals:
                positive_vectors = self.vector_store.get_vectors_by_label(individual)
                positive_sources = self.vector_store.get_sources_by_label(individual)
                primary_source = positive_sources[np.random.choice(positive_sources.shape[0])]

                primary_vector = self.vector_store.get_vector(primary_source)
                batch.append(('primary', LabeledImageVector(embedding=primary_vector, label=individual, source=primary_source)))

                positive_distances = self.vector_store.compute_distances(primary_vector, positive_vectors)
                hardest_positives = np.argsort(positive_distances)[-self.triplets:]
                batch.extend([('distant_positive', LabeledImageVector(embedding=positive_vectors[i],
                                                                      label = individual,
                                                                      source = positive_sources[i])) for i in hardest_positives])

                negative_vectors = np.vstack([self.vector_store.get_vectors_by_label(label)
                                              for label in self.individuals if label != individual])
                negative_distances = self.vector_store.compute_distances(primary_vector, negative_vectors)
                hardest_negatives = np.argsort(negative_distances)[:self.triplets]

                negative_label_sources = [(label,source) for label in self.individuals for source in self.vector_store.get_sources_by_label(label)
                                    if label != individual]

                batch.extend([('nearby_negative', LabeledImageVector(embedding=negative_vectors[i],
                                                                     label = negative_label_sources[i][0],
                                                                     source=negative_label_sources[i][1]) )for i in hardest_negatives])

            yield batch

    def __len__(self):
        return len(self.vector_store.get_all_sources()) // (self.individuals_per_batch * self.max_photos_per_individual)